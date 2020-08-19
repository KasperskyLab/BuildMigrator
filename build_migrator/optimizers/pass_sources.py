from copy import copy, deepcopy
from build_migrator.common.algorithm import add_unique_stable
from build_migrator.helpers import get_minified_target, get_final_module_copy_source
from build_migrator.modules import Optimizer


# pass sources/flags from object files into their respective binary targets
# also removes unused non top-level module_copy targets
class PassSources(Optimizer):
    priority = 2

    @staticmethod
    def add_arguments(arg_parser):
        pass

    def __init__(self, context):
        self.context = context

    def optimize(self, targets):
        index = self._get_target_index(targets)
        optimized_targets = []
        skipset = self._get_module_copy_skipset(
            index, targets
        ) | self._get_object_lib_skipset(index, targets)
        for target in targets:
            if target["type"] == "module_copy":
                if target["output"] in skipset:
                    dep_target = get_final_module_copy_source(target, index)
                    if target["source"] != dep_target["output"]:
                        target["dependencies"].remove(target["source"])
                        target["dependencies"].append(dep_target["output"])
                        target["source"] = dep_target["output"]
                    optimized_targets.append(target)
                continue
            elif target["type"] != "module":
                optimized_targets.append(target)
                continue

            if target["module_type"] == "object_lib":
                if target["output"] in skipset:
                    optimized_targets.append(target)
                # object libraries are merged into parent targets
                continue

            remaining_object_files = []
            for dep in target["objects"]:
                dep_target = index.get(dep)
                if (
                    dep_target is None
                    or dep_target["output"] in skipset
                    or dep_target["type"] in ("file", "cmd")
                ):
                    remaining_object_files.append(dep)
                    continue

                target["dependencies"].remove(dep)

                dep_target = get_final_module_copy_source(dep_target, index)
                assert (
                    dep_target["type"] == "module"
                    and dep_target["module_type"] == "object_lib"
                ), get_minified_target(dep_target)

                # Source files from child object targets is going to be moved to
                # current target.
                # If current target already contains compile_flags or include_dirs,
                # they should be moved to source file scope, otherwise
                # source files from child object targets are going to inherit
                # them and may compile with unnecessary additional flags.
                for s in target["sources"]:
                    if s.get("language") is not None:
                        flags = copy(target["compile_flags"])
                        s["compile_flags"] = add_unique_stable(
                            flags, *s["compile_flags"]
                        )
                        dirs = copy(target["include_dirs"])
                        s["include_dirs"] = add_unique_stable(dirs, *s["include_dirs"])
                target["compile_flags"] = []
                target["include_dirs"] = []

                is_cmd_target = (
                    lambda output: output in index
                    and index[output].get("type") == "cmd"
                )
                cmd_deps = [
                    d_ for d_ in dep_target["dependencies"] if is_cmd_target(d_)
                ]
                for d_ in cmd_deps:
                    dep_target["dependencies"].remove(d_)

                for src in dep_target["sources"]:
                    src["compile_flags"] = add_unique_stable(
                        copy(dep_target["compile_flags"]), *src["compile_flags"]
                    )
                    src["include_dirs"] = add_unique_stable(
                        copy(dep_target["include_dirs"]), *src["include_dirs"]
                    )
                    # Move type: 'cmd' dependencies from target to sources,
                    # to allow more granular dependency control for later optimizers
                    src["dependencies"] = add_unique_stable(
                        cmd_deps, *(src.get("dependencies") or [])
                    )
                target["sources"].extend(deepcopy(dep_target["sources"]))

                # empty dirs and object output dirs won't be used,
                # leave only only include dirs and dirs with aggregated files
                unused_dir_target = (
                    lambda t: t is not None
                    and t["type"] == "directory"
                    and not t["output"] in dep_target["include_dirs"]
                )
                deps = [
                    dep
                    for dep in dep_target["dependencies"]
                    if not unused_dir_target(index.get(dep))
                ]
                add_unique_stable(target["dependencies"], *deps)

            target["objects"] = remaining_object_files

            if "libs" in target:
                modified_libs = []
                for dep in target["libs"]:
                    if isinstance(dep, dict):
                        # { 'gcc_whole_archive': True, 'value': '<output>'}
                        dep_output = dep["value"]
                    else:
                        dep_output = dep
                    dep_target = index.get(dep_output)
                    if dep_target is None:
                        modified_libs.append(dep)
                        continue

                    if dep_target["type"] == "module_copy":
                        dep_target = get_final_module_copy_source(dep_target, index)
                        if dep_output != dep_target["output"]:
                            target["dependencies"].remove(dep_output)
                            target["dependencies"].append(dep_target["output"])
                            if isinstance(dep, dict):
                                dep["value"] = dep_target["output"]
                            else:
                                dep = dep_target["output"]
                    modified_libs.append(dep)

                target["libs"] = modified_libs

            optimized_targets.append(target)

        index = self._get_target_index(optimized_targets)
        # find module_copy targets without source and remove them
        pending_removal = []
        for t in optimized_targets:
            if t["type"] == "module_copy":
                if t["source"] not in index:
                    if t.get("top_level"):
                        raise ValueError(
                            "Lost source for top-level module_copy target: {}. This is probably a bug.".format(
                                t["source"]
                            )
                        )
                    pending_removal.append(t)
        for t in pending_removal:
            optimized_targets.remove(t)

        return optimized_targets

    def _get_object_lib_skipset(self, index, targets):
        # creates a set object libraries that cannot be optimized away

        referenced_obj_files = {}
        for target in targets:
            for o in target.get("dependencies") or []:
                referenced_obj_files[o] = True

        skip_set = set()
        for target in targets:
            if target["type"] == "module":
                if target["module_type"] == "object_lib":
                    output = target["output"]
                    is_unreferenced = output not in referenced_obj_files
                    has_post_build_commands = (
                        target.get("post_build_commands") is not None
                    )
                    if (
                        target.get("top_level")
                        or is_unreferenced
                        or has_post_build_commands
                    ):
                        skip_set.add(output)
                        continue

            referenced_by_cmd = False
            if target["type"] == "cmd":
                referenced_by_cmd = True
                dependencies = target["dependencies"]
            else:
                dependencies = [target["output"]]

            for dep in dependencies:
                dep_target = index.get(dep)
                referenced_by_top_level_copy = False
                while dep_target and dep_target["type"] == "module_copy":
                    if not referenced_by_top_level_copy:
                        referenced_by_top_level_copy = bool(dep_target.get("top_level"))
                    dep_target = index.get(dep_target["source"])

                if (
                    dep_target
                    and dep_target["type"] == "module"
                    and dep_target["module_type"] == "object_lib"
                ):
                    if referenced_by_top_level_copy or referenced_by_cmd:
                        skip_set.add(dep_target["output"])

        return skip_set

    def _get_module_copy_skipset(self, index, targets):
        # creates a set of module copy targets that cannot be optimized away

        skip_set = set()
        for target in targets:
            if target["type"] == "module_copy":
                if target.get("top_level"):
                    skip_set.add(target["output"])
                    continue
            elif target["type"] == "cmd":
                for dep in target["dependencies"]:
                    dep_target = index.get(dep)
                    if dep_target and dep_target["type"] == "module_copy":
                        skip_set.add(dep_target["output"])

        return skip_set

    def _get_target_index(self, targets):
        index = {}
        for target in targets:
            if "output" in target:
                index[target["output"]] = target
            for o in target.get("msvc_import_lib") or []:
                index[o] = target
        return index


__all__ = ["PassSources"]
