import argparse
import copy
import fnmatch
import glob
import io
import logging
import os
from pprint import pformat
import sys
import traceback
from build_migrator.helpers import (
    get_directory_target,
    get_file_target,
    get_variable_target,
    get_minified_target,
    get_target_and_dependencies,
    get_copy_target,
    get_module_copy,
)
from build_migrator.modules import EntryPoint, Parser
from build_migrator.common.algorithm import add_unique_stable
from build_migrator.common.argparse_actions import Extend
import build_migrator.common.os_ext as os_ext
import build_migrator.common.path_ext as path_ext

logger = logging.getLogger(__name__)


class BuildLogParserContext(Parser, EntryPoint):
    build_dir_placeholder = "@build_dir@"
    source_dir_placeholder = "@source_dir@"
    known_log_types = ("ninja", "make", "msbuild", "strace")

    @classmethod
    def add_arguments(cls, arg_parser):
        try:
            arg_parser.add_argument(
                "--source_dir",
                help="Source directory of the project that you want to migrate.",
                metavar="DIR",
            )
        except argparse.ArgumentError:
            # Already added somewhere else
            # TODO: make a better solution for cases when multiple extensions require the same argument
            pass
        try:
            arg_parser.add_argument(
                "--platform",
                choices=["linux", "windows", "darwin"],
                help="Platform under which the build log was obtained. "
                "Mac and Linux builds can be parsed on any platform. "
                "Windows build logs can be parsed only on Windows. "
                "Default: current platform.",
            )
        except argparse.ArgumentError:
            # Already added somewhere else
            # TODO: make a better solution for cases when multiple extensions require the same argument
            pass
        arg_parser.add_argument(
            "--logs",
            metavar=("[TYPE:]PATH"),
            nargs="+",
            action=Extend,
            help="Path to build log. For allowed log types, see --log_type argument. "
            "Logs are processed in order.",
        )
        arg_parser.add_argument(
            "--log_type",
            help="Supported log types.",
            choices=sorted(cls.known_log_types),
        )
        arg_parser.add_argument(
            "--build_dirs",
            metavar="DIR",
            nargs="+",
            dest="build_dirs",
            help="Directory with build artifacts described in the provided build log. "
            "Cannot be the same as source directory.",
        )
        arg_parser.add_argument(
            "--working_dir",
            metavar="DIR",
            help="Initial working directory for given build logs.",
        )
        arg_parser.add_argument(
            "--path_alias",
            metavar=("PATH", "ALIAS"),
            nargs=2,
            action="append",
            dest="path_aliases",
            help="During parsing, if an argument points to PATH, replace it with ALIAS. "
            "PATH can be relative to build directory. "
            "ALIAS can be made into a configurable variable by specifying "
            "a value like this: @VARIBLE_NAME@. After a variable is created, "
            "it can be used in other ALIASES like this: @DIR@/path-to-file.txt.",
        )
        arg_parser.add_argument(
            "--max_relpath_level",
            metavar="NUM",
            type=int,
            default=0,
            help="Maximum allowed relative path level when resolving paths. "
            "Paths are resolved relative to build dirs or source dir. "
            "Examples: @build_dir@/../../a.txt: level = 2; "
            "@source_dir@/b.txt: level = 0. If file can be resolved under "
            "multiple directories, the one giving the lowest relpath "
            "level is chosen.",
        )
        arg_parser.add_argument(
            "--targets",
            metavar="PATH/GLOB",
            nargs="+",
            help="Only specified files and their dependencies will be "
            "added to Build Object Model. Values can be a path "
            "or a glob expression. Values are evaluated "
            "relative to build directory. If a glob expression contains "
            "filename without directory, it matches recursively.",
        )
        arg_parser.add_argument(
            "--force_target_name",
            metavar=("OUTPUT", "NAME"),
            action="append",
            nargs=2,
            help="During parsing, set custom name for target with specified output.",
        )
        arg_parser.add_argument(
            "--capture_sources",
            metavar="PATH/GLOB",
            nargs="+",
            help="Store only selected source files into Build Object Model. "
            "Paths are evaluated relative to source directory. "
            "By default, all source files are captured.",
        )
        arg_parser.add_argument(
            "--dont_capture_sources",
            action="store_true",
            help="Don't store source files in Build Object Model.",
            default=None,
        )

    def _list_files(self, directory, pattern=None):
        if pattern is not None:
            path = self.normalize_path(pattern, directory)
            if os.path.exists(path):
                return [path]
        else:
            pattern = "*"

        glob_matches = []
        if "*" in pattern and "\\" not in pattern and "/" not in pattern:
            # recursive glob
            for root, _, files in os.walk(directory):
                for f in files:
                    if fnmatch.fnmatch(f, pattern):
                        glob_matches.append(os.path.join(root, f))
        else:
            path = self.normalize_path(pattern, directory)
            glob_matches = glob.glob(path)
        return sorted(glob_matches)

    class _Log(object):
        def __init__(self, path, type):
            self.path = path
            self.type = type

    def _parse_logs(self, logs, default_log_type=None):
        result = []
        for value in logs:
            split_idx = value.find(":")
            path = None
            if split_idx != -1:
                log_type = value[0:split_idx]
                if log_type in self.known_log_types:
                    path = value[split_idx + 1:]
            if path is None:
                if default_log_type is None:
                    raise ValueError("log_type is not specified")
                log_type = default_log_type
                path = value
            result.append(self._Log(path, log_type))
        return result

    def __init__(
        self,
        build_migrator,
        logs,
        source_dir,
        build_dirs,
        platform=None,
        working_dir=None,
        path_aliases=None,
        max_relpath_level=0,
        targets=None,
        force_target_name=None,
        capture_sources=None,
        log_type=None,
        dont_capture_sources=None,
    ):
        if platform is None:
            platform = os_ext.get_host_system_name()

        if not logs:
            raise ValueError("Specify at least one log (--logs argument)")

        if capture_sources and dont_capture_sources:
            raise ValueError(
                "capture_sources cannot be specified if dont_capture_sources is True"
            )

        self.current_target = None
        self.platform_name = platform
        self.platform = os_ext.get_platform(platform)
        self.logs = self._parse_logs(logs, log_type)
        self.build_dirs = [
            self.platform.normalize_path(os.path.abspath(os.path.join(os.curdir, bd)))
            for bd in build_dirs
        ]
        self.source_dir = self.platform.normalize_path(
            os.path.abspath(os.path.join(os.curdir, source_dir))
        )
        if working_dir:
            self._working_dir = self.platform.normalize_path(
                os.path.abspath(working_dir)
            )
        else:
            self._working_dir = self.build_dirs[0]
        self.max_relpath_level = max_relpath_level
        self.path_aliases = None
        self.target_index = None  # target_output => target
        self.targets = None
        self._variable_targets = {}
        self._arg_path_aliases = path_aliases
        self._arg_dont_capture_sources = dont_capture_sources
        self._arg_capture_sources = capture_sources

        self.dir_mapping = {self.source_dir: self.source_dir_placeholder}
        for build_dir in self.build_dirs:
            self.dir_mapping[build_dir] = self.build_dir_placeholder
            if source_dir == build_dir:
                raise ValueError("Source dir cannot be the same as build directory")

        # Without some form of caching, path normalization / resolution
        # can take up to 90% of parsing time
        self._path_normalizer_cache = {
            0: {},
            1: {},
        }

        self.required_targets = None
        if targets:
            self.required_targets = []
            for tgt in targets:
                file_found = False
                for bd in self.build_dirs:
                    paths = self._list_files(bd, tgt)
                    if paths:
                        file_found = True
                    for path in paths:
                        # search target by output
                        path = self._construct_path_arg(path).relocatable
                        if path not in self.required_targets:
                            self.required_targets.append(path)
                if not file_found:
                    # search target after parsing provided log
                    if tgt not in self.required_targets:
                        self.required_targets.append(tgt)

        self.force_target_name = {}
        for output, name in force_target_name or []:
            self.force_target_name[output] = name

    def _capture_explicitly_specified_sources(self, capture_sources):
        for src in capture_sources:
            paths = self._list_files(self.source_dir, src)
            if paths:
                for p in paths:
                    self.register_target(self._force_capture_source_file(p))
            else:
                raise ValueError("Pattern did not match any source files: %r" % src)

    def _initialize_path_aliases(self, path_aliases):
        self.path_aliases = []
        for path, alias in path_aliases or []:
            if alias.startswith("@") and alias.endswith("@"):
                # it's a variable
                if alias not in self.target_index:
                    var_name = alias[1:-1]
                    relocatable_path = self._construct_path_arg(path).relocatable
                    target = get_variable_target(var_name, alias, relocatable_path)
                    self.register_target(target)
            else:
                alias = self.normalize_path(alias, ignore_working_dir=True)
            path = self.normalize_path(path)
            self.path_aliases.append((path, alias))

    def parse(self, targets, parsers):
        self.target_index = {}
        if targets:
            for target in targets:
                self._add_target_to_index(target)
            self.targets = targets
        else:
            self.targets = []

        self._initialize_path_aliases(self._arg_path_aliases)

        self.capture_sources = not bool(self._arg_dont_capture_sources)
        if self._arg_capture_sources:
            self._capture_explicitly_specified_sources(self._arg_capture_sources)
            # don't capture any more source files
            self.capture_sources = False

        for log in self.logs:
            # newline=None argument allows processing logs from any platform,
            # irregardless of line ending type.
            with io.open(
                log.path, newline=None, encoding="utf-8", errors="replace"
            ) as f:
                for line in f:
                    line = line.strip()
                    logger.info(" > " + line)
                    # Don't use Unicode strings in Python 2,
                    # or each regular expression will have to
                    # have a second Unicode version.
                    if sys.version_info <= (3, 0):
                        line = line.encode("utf-8")
                    targets = [{"line": line}]
                    parse_targets(
                        targets, self, parsers, log_type=log.type
                    )

                logger.info(" > (EOF)")
                # 'end of file' instructs parsers like line_accumulator and response_file to pass on any accumulated data
                targets = [{"eof": True}]
                parse_targets(
                    targets, self, parsers, log_type=log.type
                )

        finalize(self)
        return self.targets

    @property
    def working_dir(self):
        if self.current_target is not None and self.current_target.get("working_dir"):
            return self.current_target["working_dir"]
        else:
            return self._working_dir

    @working_dir.setter
    def working_dir(self, value):
        self._working_dir = value

    def normalize_path(self, path, working_dir=None, ignore_working_dir=False):
        result = None
        if not ignore_working_dir:
            if working_dir is None:
                working_dir = self.working_dir
            cache = self._path_normalizer_cache[0]
            if working_dir not in cache:
                cache[working_dir] = {}
            cache = cache[working_dir]
            result = cache.get(path)
            if result is not None:
                return result
            result = self.platform.normalize_path(
                self.platform.path_join(working_dir, path)
            )
            cache[path] = result
        else:
            cache = self._path_normalizer_cache[1]
            result = cache.get(path)
            if result is not None:
                return result
            result = self.platform.normalize_path(path)
            cache[path] = result

        return result


    def _select_parent_dir(self, path, cwd=None):
        if cwd is None:
            cwd = self.working_dir
        result = path_ext.closest_dir(
            path,
            self.dir_mapping.keys(),
            max_relpath_level=self.max_relpath_level,
            cwd=cwd,
        )
        return result if result else None

    class _PathArg:
        def __init__(self, full, relocatable, argument, dependencies):
            self.full = full
            self.relocatable = relocatable
            self.argument = argument
            self.dependencies = dependencies

    def _construct_path_arg(
        self,
        path,
        relative_arg=False,
        capture_parent_dir=False,
        capture_file=False,
        capture_dir=False,
    ):
        if capture_file and capture_dir:
            raise ValueError(
                "Incompatible arguments: capture_file=True, capture_dir=True"
            )
        path = self.normalize_path(path)
        relocatable_path = None
        if self.path_aliases:
            # apply path aliases
            for src, dest in self.path_aliases:
                if path.startswith(src):
                    if len(path) == len(src) or path[len(src)] == "/":
                        relocatable_path = dest + path[len(src):]
                        break

        if relocatable_path is None:
            result = self._select_parent_dir(path)
            if result is not None:
                parent_dir, relpath = result[0], result[1]
                if relpath != ".":
                    relocatable_path = self.platform.path_join(
                        self.dir_mapping[parent_dir], relpath
                    ).replace("\\", "/")
                else:
                    relocatable_path = self.dir_mapping[parent_dir]

        dependencies = []
        if relocatable_path is None:
            logger.warn("Path not under source or build directory: {}".format(path))
            relocatable_path = path
            target = self.target_index.get(relocatable_path)
            if target:
                dependencies.append(target)
            # Don't capture files not under build or source directory yet
        else:
            for _output, _ in self._variable_targets.items():
                if _output in relocatable_path:
                    dependencies.append(_output)
            if capture_parent_dir:
                parent = self._construct_path_arg(os.path.split(path)[0])
                target = self._get_directory_target(parent.full, parent.relocatable)
                if target:
                    dependencies.append(target)
            if capture_dir:
                target = self._get_directory_target(path, relocatable_path)
                if target:
                    dependencies.append(target)
            if capture_file:
                target = self._get_file_target(path, relocatable_path)
                if target:
                    dependencies.append(target)

        argument_path = relocatable_path
        if relative_arg:
            relpath = os.path.relpath(path, self.working_dir)
            if path_ext.relpath_level(relpath) == 0:
                argument_path = self.platform.normalize_path(relpath)

        return self._PathArg(path, relocatable_path, argument_path, dependencies)

    def _get_target_name(self, target):
        name = target.get("name")
        relocatable_path = target.get("output")
        if relocatable_path:
            custom_name = self.force_target_name.get(relocatable_path)
            if custom_name:
                return custom_name
        if name is not None:
            return name
        name = relocatable_path[relocatable_path.rfind("@") + 2:]
        assert name, relocatable_path
        target_type = target.get("type")
        target_module_type = target.get("module_type")
        if target_type == "module" and target_module_type == "object_lib":
            name_without_ext, ext = os.path.splitext(name)
            if ext != ".o":
                # make sure that object libraries have consistent target name
                # on Windows and Linux
                name = name_without_ext + ".o"
        return name.replace("/", "_").replace(".", "_")

    def apply_path_aliases(self, path):
        for src, dest in self.path_aliases:
            if path.startswith(src):
                if len(path) == len(src) or path[len(src)] == "/":
                    path = dest + path[len(src):]
                    break
        return path

    def get_file_arg(self, path, dependencies=None, relative=False):
        path_arg = self._construct_path_arg(
            path, relative_arg=relative, capture_file=True
        )
        if dependencies is not None:
            for dep in path_arg.dependencies:
                if dep not in dependencies:
                    dependencies.append(dep)
        return path_arg.argument

    def get_dir_arg(self, path, dependencies=None, relative=False):
        path_arg = self._construct_path_arg(
            path, relative_arg=relative, capture_dir=True
        )
        if dependencies is not None:
            for dep in path_arg.dependencies:
                if dep not in dependencies:
                    dependencies.append(dep)
        return path_arg.argument

    def get_lib_arg(
        self, lib, dependencies=None, lib_dirs=None, relative=False, **kwargs
    ):
        if lib_dirs is None:
            lib_dirs = []
        full_path = self.platform.resolve_lib(
            lib,
            lib_dirs,
            self.working_dir,
            check_file=self.find_target_by_path,
            **kwargs
        )
        if full_path is None:
            # prebuilt library?
            full_path = self.platform.resolve_lib(
                lib, lib_dirs, self.working_dir, **kwargs
            )
        if full_path is None:
            # system library
            return lib
        argument_path = self.get_file_arg(full_path, dependencies, relative=relative)
        lib_target = self.find_target(argument_path)
        if lib_target and lib_target["output"] != argument_path:
            # lib is an import library
            return lib_target["output"]
        return argument_path

    def get_executable_arg(self, path, dependencies=None, relative=False):
        path_arg = self._construct_path_arg(
            path, relative_arg=relative, capture_file=True
        )
        if dependencies is not None:
            for dep in path_arg.dependencies:
                if dep not in dependencies:
                    dependencies.append(dep)
        return path_arg.argument

    def get_output(self, path, dependencies=None, relative=False):
        path_arg = self._construct_path_arg(
            path, relative_arg=relative, capture_parent_dir=True
        )
        if dependencies is not None:
            for dep in path_arg.dependencies:
                if dep not in dependencies:
                    dependencies.append(dep)
        return path_arg.relocatable

    def _force_capture_source_file(self, path):
        path_arg = self._construct_path_arg(path)
        if not self.is_in_source_dir(path_arg.relocatable):
            raise ValueError(
                "File is not in source directory: {} ({})".format(
                    path_arg.full, path_arg.relocatable
                )
            )
        return self._get_file_target(
            path_arg.full, path_arg.relocatable, capture_source=True
        )

    def _get_file_target(self, full_path, relocatable_path, capture_source=None):
        if relocatable_path in self.target_index:
            return relocatable_path

        if self.is_in_source_dir(relocatable_path):
            if capture_source is None:
                capture_source = self.capture_sources
            if not capture_source:
                return relocatable_path
        elif self.is_in_build_dir(relocatable_path):
            pass
        else:
            logger.debug(
                "Path not under build or source directory, ignoring: {}".format(
                    full_path
                )
            )
            return None

        parent_dir_found = self._select_parent_dir(full_path)
        if parent_dir_found is None:
            raise ValueError(
                "Cannot resolve build or source dir for path {}. Try increasing --max_relpath_level.".format(
                    full_path
                )
            )

        content = None
        try:
            with open(full_path, "rb") as f:
                content = f.read()
        except IOError:
            logging.error(traceback.format_exc())
            return None

        dependencies = None
        parent_dir = self._construct_path_arg(os.path.split(full_path)[0])
        parent_dir_target = self._get_directory_target(
            parent_dir.full, parent_dir.relocatable
        )
        if parent_dir_target:
            dependencies = [parent_dir_target]

        return get_file_target(
            content, output=relocatable_path, dependencies=dependencies
        )

    def _get_directory_target(self, full_path, relocatable_path):
        if relocatable_path in self.target_index:
            return relocatable_path

        root_dir_variable = None
        split_result = relocatable_path.split("@", 2)
        if len(split_result) == 3:
            var_name = split_result[1]
            var_placeholder = "@" + var_name + "@"
            if var_placeholder in self.target_index:
                root_dir_variable = var_placeholder

        if root_dir_variable:
            # directory contains user-provided variable
            # target shouldn't be created for this directory
            return root_dir_variable

        in_src_dir = relocatable_path.startswith(self.source_dir_placeholder)
        if in_src_dir:
            # There's no case for creating directories in source directory, unless
            # source directory is modified during build, and that's not supported.
            return None
        in_build_dir = relocatable_path.startswith(self.build_dir_placeholder)
        if in_build_dir:
            if len(relocatable_path) == len(self.build_dir_placeholder):
                # build directory root should be created automatically anyway
                return None
        else:
            logger.debug(
                "Path not under build or source directory, ignoring: {}".format(
                    full_path
                )
            )
            return None

        dependencies = [root_dir_variable] if root_dir_variable else None
        return get_directory_target(output=relocatable_path, dependencies=dependencies)

    def _collect_file_targets(self, dir_path):
        targets = []
        for file_path in self._list_files(dir_path):
            file_path = self._construct_path_arg(file_path)
            target = self._get_file_target(file_path.full, file_path.relocatable)
            targets.append(target)
        return targets

    def process_target_copy(self, source, output, dependencies):
        if output == source:
            return None

        source_target = self.find_target(source)
        if source_target and source_target["type"] in ["module", "module_copy"]:
            target_descr = None
            if self.platform.is_static_lib(output):
                target_descr = self.platform.parse_static_lib(output)
            elif self.platform.is_shared_lib(output):
                target_descr = self.platform.parse_shared_lib(output)
            else:
                target_descr = self.platform.parse_executable(output)
            target_name = target_descr["target_name"]
            # Make sure that target's name doesn't clash with existing targets
            conflicting_targets = list(self.find_targets_by_name(target_name))
            if conflicting_targets:
                assert len(conflicting_targets) == 1
                conflicting_target = conflicting_targets[0]
                if os.path.basename(conflicting_target["output"]) == os.path.basename(
                    output
                ):
                    # /liba.so.1 => /a/liba.so.1
                    # Apply general target naming rules that rely on output path
                    target_name = None
                else:
                    # If we're here, versions MUST be different
                    ctgt_descr = self.platform.parse_shared_lib(
                        conflicting_target["output"]
                    )
                    assert ctgt_descr["version"] != target_descr["version"]
                    if ctgt_descr["version"]:
                        conflicting_target["name"] += "." + ctgt_descr["version"]
                    if target_descr["version"]:
                        target_name += "." + target_descr["version"]
            return get_module_copy(
                target_name,
                source,
                output,
                dependencies=dependencies,
            )
        elif source_target and source_target["type"] == "directory":
            target_copy = copy.deepcopy(source_target)
            target_copy["output"] = output
            return target_copy

        return get_copy_target(None, source, output, dependencies)

    def find_target(self, output):
        if output in self.target_index:
            return self.target_index[output]
        return None

    def find_targets_by_name(self, name):
        for target in self.targets:
            if target.get("name") == name:
                yield target

    def find_target_by_path(self, path):
        path = self._construct_path_arg(path)
        return self.find_target(path.relocatable)

    def is_in_build_dir(self, relocatable_path):
        if relocatable_path.startswith(self.build_dir_placeholder):
            return True
        return False

    def is_in_source_dir(self, relocatable_path):
        if relocatable_path.startswith(self.source_dir_placeholder):
            return True
        return False

    def is_in_build_or_source_dir(self, relocatable_path):
        return self.is_in_build_dir(relocatable_path) or self.is_in_source_dir(
            relocatable_path
        )

    def _find_free_target_index(self, output):
        for idx in range(1, 65535):
            output_with_idx = output + "#" + str(idx)
            if output_with_idx not in self.target_index:
                return idx
        raise ValueError("free target index not found")

    def _change_target_output(self, target, output):
        old_output = target["output"]
        for tgt in self.targets:
            deps = tgt.get("dependencies")
            if deps:
                tgt["dependencies"] = [
                    output if dep == old_output else dep for dep in deps
                ]
            deps = tgt.get("objects")
            if deps:
                tgt["objects"] = [output if dep == old_output else dep for dep in deps]
        del self.target_index[old_output]
        target["output"] = output
        self.target_index[output] = target

    # overwrite old_target's output by new_target,
    # but keep existing references to old_target
    # currently only objects targets are supported
    def _overwrite_target_output(self, old_target, new_target):
        output = old_target["output"]
        if output != new_target["output"]:
            raise ValueError("target output must be the same")
        idx = self._find_free_target_index(output)
        self._change_target_output(old_target, output + "#" + str(idx))

    @staticmethod
    def _is_object_lib(target):
        if target.get("type") != "module":
            return False
        if target.get("module_type") != "object_lib":
            return False
        return True

    def register_target(self, target):
        assert target["output"]
        registered_targets = []

        if "dependencies" not in target:
            target["dependencies"] = []
        target, dependencies = self.split_target_dependencies(target, log=False)

        existing_target = self.find_target(target["output"])
        if existing_target:
            if existing_target != target:
                logger.warn(
                    "Target's output is already registered, but with different definition"
                )
                existing_target_is_file = existing_target.get("type") == "file"
                new_target_is_not_file = target.get("type") != "file"
                if existing_target_is_file and new_target_is_not_file:
                    logger.warning("Replacing existing file target")
                    del self.target_index[existing_target["output"]]
                    self.targets.remove(existing_target)
                elif self._is_object_lib(existing_target) and self._is_object_lib(
                    target
                ):
                    self._overwrite_target_output(existing_target, target)
                else:
                    logger.error(
                        "Only targets with type=module and module_type=object_lib are allowed to have the same output path"
                    )
                    logger.info("Old target:")
                    logger.info(pformat(get_minified_target(existing_target)))
                    logger.info("New target:")
                    logger.info(pformat(get_minified_target(target)))
                    return registered_targets
            else:
                return registered_targets

        if "name" in target:
            target["name"] = self._get_target_name(target)

        working_dir = target.get("working_dir")
        if working_dir:
            target["working_dir"] = self.get_dir_arg(working_dir)

        logger.info(" > Registering new target:")
        logger.info(pformat(get_minified_target(target)))
        self.targets.append(target)
        self._add_target_to_index(target)
        registered_targets.append(target)

        for dep_target in dependencies:
            registered_targets.extend(self.register_target(dep_target))

        return registered_targets

    def split_target_dependencies(self, target, log=True):
        dependencies = []
        for idx, dep in enumerate(target["dependencies"] or []):
            if type(dep) is dict:
                dependencies.append(dep)
                target["dependencies"][idx] = dep["output"]
        return target, dependencies

    def _add_target_to_index(self, target):
        if "output" in target:
            self.target_index[target["output"]] = target
            for output in target.get("msvc_import_lib") or []:
                self.target_index[output] = target
        else:
            logger.warn("Target has no output:")
            logger.warn(pformat(get_minified_target(target)))
        if target["type"] == "variable":
            self._variable_targets[target["output"]] = target

    def get_implicit_include_dirs(
        self,
        sources,
        include_dirs,
        dependencies,
    ):
        if not (dependencies and sources):
            return include_dirs

        include_dirs = set(include_dirs)
        implicit_include_dirs = []

        for dep in dependencies:
            if (
                os.path.splitext(dep)[-1] not in [".h", ".hpp", ".inc", ".ipp"]
                or not dep.startswith((BuildLogParserContext.build_dir_placeholder, BuildLogParserContext.source_dir_placeholder))  # skip if dependency in /usr....
            ):
                continue

            declare_include_dir = False

            for i_d in include_dirs:
                if path_ext.is_subpath(i_d, os.path.dirname(dep)):
                    declare_include_dir = True
                    break
            if not declare_include_dir:
                for s_d in map(lambda x: os.path.dirname(x['path']), sources):
                    if s_d not in include_dirs:
                        implicit_include_dirs.append(s_d)

        return implicit_include_dirs


def _group_by_duplicate_names(targets):
    name_groups = {}
    duplicate_name_groups = []
    for t in targets:
        if "name" not in t:
            continue
        name = t["name"]
        if name not in name_groups:
            name_groups[name] = []
        elif len(name_groups[name]) == 1:
            duplicate_name_groups.append(name_groups[name])
        name_groups[name].append(t)
    return duplicate_name_groups


def parse_targets(targets, context, parsers, log_type=None):
    result_targets = []

    for target in targets:
        logger.debug(" > Parsing target:")
        logger.debug(pformat(get_minified_target(target)))

        for idx, parser in enumerate(parsers):
            is_applicable = getattr(parser, "is_applicable", None)
            if is_applicable is None or is_applicable(log_type=log_type):
                logger.debug(type(parser).__name__)
                try:
                    context.current_target = target
                    result = parser.parse(target)
                    if isinstance(
                        result, list
                    ):  # parser is allowed to return multiple targets
                        target = None
                        result_targets += parse_targets(
                            result,
                            context,
                            parsers[idx + 1:],
                            log_type=log_type,
                        )
                        break
                    else:
                        if target != result:
                            logger.debug(" > Modified target:")
                            logger.debug(pformat(get_minified_target(result)))
                        target = result
                except Exception:
                    logging.error(traceback.format_exc())

        if target and "output" in target:
            result_targets.append(target)
            context.register_target(target)

    return result_targets


def deduplicate_target_names(targets):
    duplicates_found = True
    while duplicates_found:
        duplicates_found = False
        for dups_by_name in _group_by_duplicate_names(targets):
            duplicates_found = True
            group_by_basename = {}
            for t in dups_by_name:
                basename = os.path.basename(t["output"])
                if basename in group_by_basename:
                    group_by_basename[basename].append(t)
                else:
                    group_by_basename[basename] = [t]

            for basename, dups_by_basename in group_by_basename.items():
                if len(dups_by_basename) > 1:
                    for t in dups_by_basename:
                        # If duplicate targets have the same basename (filename), but reside
                        # in different directories, prepend directory to their names
                        path = t["output"]
                        path = path.replace(
                            BuildLogParserContext.build_dir_placeholder + "/", ""
                        )
                        path = path.replace(
                            BuildLogParserContext.source_dir_placeholder + "/", ""
                        )
                        path = os.path.dirname(path)
                        if path:
                            path = "".join([c if c.isalnum() else "_" for c in path])
                            t["name"] = path + "_" + t["name"]
                else:
                    # If duplicate targets have different basenames (filenames),
                    # change their names to actual filenames
                    t = dups_by_basename[0]
                    t["name"] = os.path.basename(t["output"]).replace(".", "_")


def provide_required_targets(context):
    # targets may have duplicate names, let's keep that in mind
    if context.required_targets:
        name_index = {}
        targets = []
        skip_set = set()
        for t in context.targets:
            if "name" not in t:
                continue
            lst = name_index.get(t["name"], [])
            lst.append(t)
            name_index[t["name"]] = lst
            if t.get("top_level"):
                targets += list(
                    get_target_and_dependencies(t, context.target_index, skip_set)
                )

        for key in context.required_targets:
            output = context.normalize_path(key)
            output = context._construct_path_arg(output).relocatable
            if key in name_index:
                # filter by name
                for t in name_index[key]:
                    targets += list(
                        get_target_and_dependencies(t, context.target_index, skip_set)
                    )
                    t["top_level"] = True
            elif key in context.target_index:
                # filter by output
                t = context.target_index[key]
                targets += list(
                    get_target_and_dependencies(t, context.target_index, skip_set)
                )
                t["top_level"] = True
            elif output in context.target_index:
                # filter by output
                t = context.target_index[output]
                targets += list(
                    get_target_and_dependencies(t, context.target_index, skip_set)
                )
                t["top_level"] = True
            elif "*" in key:
                # glob output values
                found_targets = []
                fname_glob = os.path.basename(key)
                dir_glob = os.path.dirname(output)
                is_recurive_glob_ = "\\" not in key and "/" not in key
                for t in context.targets:
                    t_out = t.get("output")
                    if t_out is None:
                        continue
                    fname_ = os.path.basename(t_out)
                    if not fnmatch.fnmatch(fname_, fname_glob):
                        continue
                    dir_ = os.path.dirname(t_out)
                    if not is_recurive_glob_ and not fnmatch.fnmatch(dir_, dir_glob):
                        continue
                    found_targets.append(t)

                if found_targets:
                    for t in found_targets:
                        targets += list(
                            get_target_and_dependencies(
                                t, context.target_index, skip_set
                            )
                        )
                        t["top_level"] = True
                else:
                    raise ValueError(
                        "Required target not found: {}. Note: paths are evaluated relative to build directory.".format(
                            key
                        )
                    )
            else:
                # add some file/directory
                _targets = None
                for dir, placeholder in context.dir_mapping.items():
                    # there may be multiple build dirs, try all of them
                    path = key.replace(placeholder, dir)
                    path = context.normalize_path(path)
                    if os.path.exists(path):
                        path_arg = context._construct_path_arg(path)
                        if os.path.isdir(path):
                            _targets = context._collect_file_targets(path_arg.full)
                        else:
                            _targets = [
                                context._get_file_target(
                                    path_arg.full, path_arg.relocatable
                                )
                            ]
                        break

                if _targets is not None:
                    for _t in _targets:
                        _t["top_level"] = True
                        targets.extend(context.register_target(_t))
                else:
                    raise ValueError(
                        "Required target not found: {}. Note: paths are evaluated relative to build directory.".format(
                            key
                        )
                    )
        context.targets = targets


def check_target_outputs(targets):
    def _raise(output, tgt1, tgt2):
        raise ValueError(
            "Duplicate output: {}\nCompare:\n{}\nVersus:\n{}".format(
                output,
                pformat(get_minified_target(tgt1)),
                pformat(get_minified_target(tgt2)),
            )
        )

    index = {}
    for tgt in targets:
        if tgt["output"] in index:
            _raise(tgt["output"], tgt, index[tgt["output"]])
        index[tgt["output"]] = tgt
        for output in tgt.get("msvc_import_lib") or []:
            if output in index:
                _raise(output, tgt, index[output])
            index[output] = tgt


def finalize(context):
    provide_required_targets(context)
    deduplicate_target_names(context.targets)
    check_target_outputs(context.targets)


__all__ = ["BuildLogParserContext"]
