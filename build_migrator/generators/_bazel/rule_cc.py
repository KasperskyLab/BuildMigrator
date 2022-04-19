import logging
import os
from build_migrator.common.algorithm import make_hashable
from build_migrator.helpers import (
    language_to_flags_property,
    language_to_includes_property,
    ModuleTypes,
)
from build_migrator.modules import Generator


logger = logging.getLogger(__name__)


class RuleCc(Generator):
    def __init__(self, context):
        self.context = context
        self.copts_attribute = "copts"
        self.linkopts_attribute = "linkopts"

    def generate(self, target):
        if not target["type"] == "module":
            return False
        if not self._validate_target(target):
            return False

        unhandled_files = []
        sources = []
        deps = []
        for src in target["dependencies"]:
            value = None
            src_target = self.context.target_index.get(src)
            if src_target is not None:
                src_type = src_target["type"]
                if src_type == "file":
                    value = src
                elif src_type == "module":
                    if src not in target["objects"]:
                        deps.append(":" + src_target["name"])
                elif src_type == "directory":
                    pass  # Ignore
                elif src_type == "copy":
                    value = src
                else:
                    raise ValueError(
                        "Cannot handle dependency: {}, type {}".format(src, src_type)
                    )
            else:
                raise ValueError("Unknown target: {}".format(src))

            if value is not None:
                if self._can_be_processed_as_source(value):
                    sources.append(value)
                else:
                    unhandled_files.append(value)

        self._write_preamble(target)

        self.context.write_line('    name = "{}",', target["name"])

        self.context.write_line("    srcs = [")
        for src in sources:
            self.context.write_line('        "{}",', src)
        self.context.write_line("    ],")

        self._write_copts(target)

        self._write_include_dirs(target)

        if self.context.for_windows:
            unhandled_files = self._process_win_def_files(
                unhandled_files, target["link_flags"]
            )
        else:
            unhandled_files = self._process_linker_scripts(
                unhandled_files, target["link_flags"], deps
            )

        self._write_linkopts(target.get("link_flags"), target.get("libs"))

        self.context.write_line("    deps = [")
        for item in deps:
            self.context.write_line('        "{}",', item)
        self.context.write_line("    ],")

        self.context.write_line(")")

        if unhandled_files:
            logger.error("Unhandled dependencies remaining: {}".format(unhandled_files))

        return True

    def _validate_target(self, target):
        for src in target["sources"]:
            for property in ["compile_flags", "include_dirs"]:
                if src.get(property):
                    logger.error(
                        "%s: source-local %s is not supported by Bazel",
                        src["path"],
                        property,
                    )

        object_files = target.get("objects")
        if target.get("objects"):
            logger.error("Object files are not supported: {}".format(object_files))

        return True

    def _can_be_processed_as_source(self, path):
        ext = os.path.splitext(path)[1].lower()
        return ext in {
            ".cc",
            ".cpp",
            ".cxx",
            ".c++",
            ".c",
            ".h",
            ".hh",
            ".hpp",
            ".ipp",
            ".hxx",
            ".h++",
            ".inc",
            ".inl",
            ".s",
            ".asm",
            ".a",
            ".lib",
            ".lo",
            ".so",
            ".dylib",
            ".dll",
            ".o",
            ".obj",
        }

    def _write_preamble(self, target):
        if target["type"] != "module":
            raise ValueError("Provided target is not a module")
        module_type = target["module_type"]
        linkshared = False
        linkstatic = False
        if module_type == ModuleTypes.executable:
            self.context.write_line("cc_binary(")
        elif module_type == ModuleTypes.shared_lib:
            self.context.write_line("cc_binary(")
            linkshared = True
        elif module_type == ModuleTypes.static_lib:
            linkstatic = True
            self.context.write_line("cc_library(")
        else:
            raise ValueError("Module type not supported: {}".format(module_type))

        if linkshared:
            self.context.write_line("    linkshared = {},".format(linkshared))
        self.context.write_line("    linkstatic = {},".format(linkstatic))

    def _format_copts_item(self, item):
        self.context.write_list_or_string(
            '        "{}",', item, formatter=self.context.format_location
        )

    def _write_copts(self, target):
        all_copts = set()
        self.context.write_line("    {} = [", self.copts_attribute)
        for f in target["compile_flags"]:
            all_copts.add(make_hashable(f))
            self._format_copts_item(f)
        value = target.get("compatibility_version")
        if value:
            self.context.write_line('        "-compatibility_version {}",', value)
        for _, prop in language_to_flags_property.items():
            flags = target.get(prop)
            if flags:
                logger.warn(
                    "Property '%s' is not fully supported yet. Language-specific flags are applied to all languages",
                    prop,
                )
                flag_group_header = False
                for f in flags:
                    if make_hashable(f) in all_copts:
                        continue
                    if not flag_group_header:
                        self.context.write_line("        # {}", prop)
                        flag_group_header = True
                    all_copts.add(make_hashable(f))
                    self._format_copts_item(f)
        self.context.write_line("    ],")

    def _write_include_dirs(self, target):
        self.context.write_line("    includes = [")
        all_includes = set()
        for f in target["include_dirs"]:
            all_includes.add(f)
            self.context.write_line('        "{}",', f)
        for _, prop in language_to_includes_property.items():
            flags = target.get(prop)
            if flags:
                logger.warn(
                    "Property '%s' is not fully supported yet. Language-specific include dirs are applied to all languages",
                    prop,
                )
                flag_group_header = False
                for f in flags:
                    if f in all_includes:
                        continue
                    if not flag_group_header:
                        self.context.write_line("        # {}", prop)
                        flag_group_header = True
                    all_includes.add(f)
                    self.context.write_line('        "{}",', f)
        self.context.write_line("    ],")

    def _write_linkopts(self, link_flags, libs):
        self.context.write_line("    {} = [", self.linkopts_attribute)
        for f in link_flags:
            self.context.write_list_or_string(
                '        "{}",', f, formatter=self.context.format_location
            )
        for lib in libs or []:
            if self.context.target_index.get(lib) is None:
                if lib.find("/") >= 0 or lib.find("\\") >= 0:
                    raise ValueError("Library name must not be a path: {}".format(lib))
                self.context.write_line(
                    '        "{}{}",', self.context.link_lib_prefix, lib
                )
            else:
                # Already handled by src attribute
                pass
        self.context.write_line("    ],")

    def _process_win_def_files(self, unhandled_files, link_flags):
        def_files = [
            path
            for path in unhandled_files
            if os.path.splitext(path)[1].lower() == ".def"
        ]
        link_flag_set = set(link_flags)
        if def_files:
            if len(def_files) > 1:
                raise ValueError("Target cannot have more than one .def file")
            for path in def_files:
                for flag_prefix in ["/def:", "-def:", "/DEF:", "-DEF:"]:
                    remove_flag = flag_prefix + path
                    if remove_flag in link_flag_set:
                        link_flags.remove(remove_flag)
                self.context.write_line('    win_def_file = "{}",', path)
                unhandled_files.remove(path)
        return unhandled_files

    def _process_linker_scripts(self, unhandled_files, link_flags, deps):
        linker_scripts = [
            path
            for path in unhandled_files
            if os.path.splitext(path)[1].lower() in {".map", ".ld", ".lds", ".ldscript"}
        ]
        deps.extend(linker_scripts)
        for path in linker_scripts:
            unhandled_files.remove(path)
        return unhandled_files
