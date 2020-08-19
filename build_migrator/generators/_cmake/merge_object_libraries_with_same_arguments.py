import logging
import itertools

from build_migrator.helpers import (
    get_source_with_inherited_flags,
    get_module_target,
    get_source_file_reference,
    ModuleTypes,
)
from build_migrator.modules import Generator

logger = logging.getLogger(__name__)


def source_object_to_string_without_path(target):
    return " ".join(target["compile_flags"]) + " ".join(
        ["-I" + d for d in target["include_dirs"]]
    )


def split_target_groups_if_needed(target_groups1, target_groups2):
    r1 = []
    r2 = []
    for target_group1 in target_groups1:
        for target_group2 in target_groups2:
            common_targets = set(target_group1) & set(target_group2)

            new_target_group = [
                target for target in target_group1 if target in common_targets
            ]
            if len(new_target_group) > 0 and set(new_target_group) not in [
                set(tg) for tg in r1
            ]:
                r1.append(new_target_group)

            new_target_group = [
                target for target in target_group1 if target not in common_targets
            ]
            if len(new_target_group) > 0 and set(new_target_group) not in [
                set(tg) for tg in r1
            ]:
                r1.append(new_target_group)

            new_target_group = [
                target for target in target_group2 if target in common_targets
            ]
            if len(new_target_group) > 0 and set(new_target_group) not in [
                set(tg) for tg in r2
            ]:
                r2.append(new_target_group)

            new_target_group = [
                target for target in target_group2 if target not in common_targets
            ]
            if len(new_target_group) > 0 and set(new_target_group) not in [
                set(tg) for tg in r2
            ]:
                r2.append(new_target_group)

    return r1, r2, (len(r1) > len(target_groups1)) or (len(r2) > len(target_groups2))


def build_optimal_target_groups(target_groups):
    libs_changed = True

    while libs_changed:
        libs_changed = False
        for index, t1 in enumerate(target_groups.keys()):
            for t2 in itertools.islice(target_groups.keys(), index + 1, None):
                (
                    target_groups[t1],
                    target_groups[t2],
                    these_libs_changed,
                ) = split_target_groups_if_needed(target_groups[t1], target_groups[t2])
                if these_libs_changed:
                    libs_changed = True

    return target_groups


def optimize_pending_object_libs(pending_object_list):
    res = {}
    for source_id, target_groups in pending_object_list.items():
        target_groups = build_optimal_target_groups(target_groups)
        res[source_id] = target_groups

    return res


def build_object_lib_from_sources(project_name, targets_by_output, object_libs, index):
    lib_name = "_".join(filter(None, [project_name, "object_lib", str(index)]))
    output_name = "@build_dir@/" + lib_name + ".o"

    sources = []
    for object_lib_output in object_libs:
        old_object_lib = targets_by_output[object_lib_output]
        for source in old_object_lib["sources"]:
            sources.append(get_source_with_inherited_flags(old_object_lib, source))

    target = get_module_target(
        "object_lib",
        lib_name,
        output_name,
        compile_flags=sources[0]["compile_flags"],
        include_dirs=sources[0]["include_dirs"],
        sources=[
            get_source_file_reference(
                source["path"],
                language=source["language"],
                dependencies=source.get("dependencies"),
            )
            for source in sources
        ],
    )

    return target


def build_new_targets(project_name, pending_object_libs, targets_by_output):
    deps_to_remove = {}  # target_output -> object_set
    deps_to_add = {}  # target_output -> object_list
    new_targets = {}  # target_output -> target

    new_targets_cache = {}
    index = 1
    for source_id in sorted(pending_object_libs):
        target_libs = pending_object_libs[source_id]
        for target_output in sorted(target_libs):
            libs = target_libs[target_output]
            for lib_objects in libs:
                if len(lib_objects) == 1:
                    # skip unoptimized lib
                    continue

                old_deps_for_target = deps_to_remove.get(target_output, set())
                old_deps_for_target |= set(lib_objects)
                deps_to_remove[target_output] = old_deps_for_target

                cache_key = ";".join(lib_objects)
                if cache_key not in new_targets_cache:
                    lib_target = build_object_lib_from_sources(
                        project_name, targets_by_output, lib_objects, index
                    )
                    index += 1
                    new_targets_cache[cache_key] = lib_target
                    new_targets[lib_target["output"]] = lib_target

                deps_for_target = deps_to_add.get(target_output) or []
                deps_for_target.append(lib_target["output"])
                deps_to_add[target_output] = deps_for_target

    return new_targets, deps_to_remove, deps_to_add


class MergeObjectLibrariesWithSameArguments(Generator):
    priority = -1.9

    @staticmethod
    def add_arguments(arg_parser):
        pass

    def __init__(self, context):
        self.context = context

    def optimize(self, targets):
        targets_by_output = {}
        for target in targets:
            if "output" in target:
                targets_by_output[target["output"]] = target
            msvc_import_libs = target.get("msvc_import_lib") or []
            for implib in msvc_import_libs:
                targets_by_output[implib] = target

        # key: all compile flags for source,
        # value:
        #     {
        #          key: target output,
        #          value: list
        #          [
        #               [
        #                   TARGET_OUTPUT1, ... TARGET_OUTPUTn - TARGET_OUTPUTi - output of corresponding object_lib which is candidate for merge
        #               ] - each list is candidate for merged object lib
        #          ]
        #     }
        pending_object_libs = {}

        for target in filter(lambda target: target["type"] == "module", targets):
            for object in target.get("objects") or []:
                child_target = targets_by_output.get(object)
                if (
                    not child_target
                    or child_target["module_type"] != ModuleTypes.object_lib
                ):
                    continue
                post_build_commands = child_target.get("post_build_commands") or []
                if len(post_build_commands) > 0:
                    logger.debug(
                        "Skip target {t} because of non empty post build commands".format(
                            t=child_target["output"]
                        )
                    )
                    continue

                child_sources = child_target.get("sources") or []
                if child_sources:
                    # assume that all source files in object_lib are built with same flags
                    source_id = source_object_to_string_without_path(
                        get_source_with_inherited_flags(child_target, child_sources[0])
                    )

                    targets_for_src_id = pending_object_libs.get(source_id, {})
                    libs_for_target = targets_for_src_id.get(target["output"], [[]])
                    libs_for_target[0].append(object)
                    targets_for_src_id[target["output"]] = libs_for_target
                    pending_object_libs[source_id] = targets_for_src_id

        pending_object_libs = optimize_pending_object_libs(pending_object_libs)

        new_targets, deps_to_remove, deps_to_add = build_new_targets(
            self.context.project, pending_object_libs, targets_by_output
        )

        res = []
        newly_added_target_cache = set()
        for target in filter(
            lambda target: target.get("output")
            not in set().union(*deps_to_remove.values()),
            targets,
        ):
            if target["type"] == "module":
                target_output = target["output"]

                for object_to_remove in deps_to_remove.get(target_output) or []:
                    logger.debug(
                        "Remove dependency from target {tgt}: {object}".format(
                            tgt=target["output"], object=object_to_remove
                        )
                    )
                    target["objects"].remove(object_to_remove)
                    target["dependencies"].remove(object_to_remove)
                    unused_sources = (
                        targets_by_output[object_to_remove].get("sources") or []
                    )
                    target["dependencies"] = [
                        dep
                        for dep in target["dependencies"]
                        if dep not in unused_sources
                    ]

                for object_to_add in deps_to_add.get(target_output) or []:
                    target["objects"].append(object_to_add)
                    target["dependencies"].append(object_to_add)
                    logger.debug(
                        "Added new object for target {tgt}: {object}".format(
                            tgt=target["output"], object=object_to_add
                        )
                    )

                    if object_to_add not in newly_added_target_cache:
                        logger.debug(
                            "Added new target with output {output}".format(
                                output=object_to_add
                            )
                        )
                        res.append(new_targets[object_to_add])
                        newly_added_target_cache.add(object_to_add)

            res.append(target)

        return res


__all__ = ["MergeObjectLibrariesWithSameArguments"]
