import operator

from build_migrator.common.algorithm import join_nested_lists
from build_migrator.common.os_ext import Windows
from build_migrator.generators._cmake.cmake_cmd import CMakeCmd
from build_migrator.helpers import flatten_list, ModuleTypes, get_target_output_dir
from build_migrator.modules import Generator


system_library_map = {
    "dl": "${CMAKE_DL_LIBS}",
    "pthread": "Threads::Threads",
    "advapi32": "",  # MSBuild adds Windows system libs automatically
    "comdlg32": "",
    "gdi32": "",
    "kernel32": "",
    "ole32": "",
    "oleaut32": "",
    "shell32": "",
    "user32": "",
    "uuid": "",
    "winspool": "",
    "c": "",
    "gcc_s": "",
}


class CMakeModule(Generator):
    priority = 1

    @staticmethod
    def add_arguments(arg_parser):
        pass

    def __init__(self, context):
        self.context = context
        self.empty_source_path = None
        if not hasattr(self.context, "cmake_module_source_compile_flags_"):
            self.context.cmake_module_source_compile_flags_ = {}
        if not hasattr(self.context, "cmake_module_source_include_dirs_"):
            self.context.cmake_module_source_include_dirs_ = {}
        self.cmd_generator = CMakeCmd(context)

    _extensions = {
        "C": ".c",
        "CXX": ".cpp",
        "ASM": ".S",
        "ASM_MASM": ".asm",
        "ASM_NASM": ".asm",
        "ASM_YASM": ".asm",
    }

    def create_empty_source_arg(self, f):
        if self.empty_source_path is None:
            file_extension = ""
            # `C` should be first since it has less runtime dependencies than C++
            if "C" in self.context.languages:
                file_extension = self._extensions["C"]
            elif "CXX" in self.context.languages:
                file_extension = self._extensions["CXX"]
            else:
                file_extension = self._extensions[self.context.languages[0]]

            f.write(
                "# Workaround for CMake error: 'No SOURCES given to target' / 'no source files for target'\n"
            )
            self.empty_source_path = (
                "${CMAKE_CURRENT_BINARY_DIR}/empty" + file_extension
            )
            f.write(
                'if(NOT EXISTS {filename})\n    file(WRITE {filename} "")\nendif()\n'.format(
                    filename=self.empty_source_path
                )
            )

        return [self.empty_source_path]

    def generate(self, target):
        if not target["type"] == "module":
            return False

        with self.context.open("CMakeLists.txt", "a") as f:
            pthread_found = False
            if "-pthread" in target.get("link_flags", []):
                target["link_flags"].remove("-pthread")
                pthread_found = True
            if "-pthread" in target.get("compile_flags", []):
                target["compile_flags"].remove("-pthread")
                pthread_found = True
            if pthread_found:
                if "libs" not in target:
                    target["libs"] = []
                target["libs"].append("Threads::Threads")

            # Additional newline between targets
            f.write("\n")

            cmake_supported_srcs = list(
                filter(lambda t: t["language"] != "YASM", target["sources"])
            )
            specify_linker_language = False
            if (
                "ASM_MASM" in self.context.languages
                and "ASM_NASM" in self.context.languages
            ):
                masm_srcs = [
                    x["path"] for x in cmake_supported_srcs if x["language"] == "MASM"
                ]
                if masm_srcs:
                    # TODO: use set_language()
                    s = self.context.format_call(
                        "set_source_files_properties",
                        [],
                        masm_srcs,
                        ["PROPERTIES", "LANGUAGE", "ASM_MASM"],
                    )
                    f.write(s)
                nasm_srcs = [
                    x["path"] for x in cmake_supported_srcs if x["language"] == "NASM"
                ]
                if nasm_srcs:
                    # TODO: use set_language()
                    s = self.context.format_call(
                        "set_source_files_properties",
                        [],
                        nasm_srcs,
                        ["PROPERTIES", "LANGUAGE", "ASM_NASM"],
                    )
                    f.write(s)
                if len(nasm_srcs) + len(masm_srcs) == len(cmake_supported_srcs):
                    # CMake gets confused if target has only ASM files
                    specify_linker_language = True

            for source in target["sources"]:
                compile_flags = join_nested_lists(source.get("compile_flags"))
                if compile_flags:
                    compile_flags = self.context.process_compile_flags(compile_flags)
                    # TODO: use source_compile_options()
                    path_ = source["path"]
                    value_ = self.context.join_property_values(compile_flags)
                    # If COMPILE_OPTIONS was previosly set for current source file,
                    # now it's going to be overwritted even for previosly created
                    # targets that use this source file.
                    # Make sure that COMPILE_OPTIONS is set only once.
                    validation_dict = self.context.cmake_module_source_compile_flags_
                    if path_ not in validation_dict:
                        validation_dict[path_] = value_
                        s = self.context.format_call(
                            "set_source_files_properties",
                            [path_, "PROPERTIES", "COMPILE_OPTIONS"],
                            [value_],
                        )
                        f.write(s)
                    elif validation_dict[path_] != value_:
                        prev_value = validation_dict[path_]
                        raise ValueError(
                            "{}: incompatible compile flags: {} vs {}.".format(
                                path_, prev_value, value_
                            )
                        )
                include_dirs = source.get("include_dirs")
                if include_dirs:
                    # TODO: use source_include_directories()
                    path_ = source["path"]
                    value_ = self.context.join_property_values(include_dirs)
                    # If INCLUDE_DIRECTORIES was previosly set for current source file,
                    # now it's going to be overwritted even for previosly created
                    # targets that use this source file.
                    # Make sure that INCLUDE_DIRECTORIES is set only once.
                    validation_dict = self.context.cmake_module_source_include_dirs_
                    if path_ not in validation_dict:
                        validation_dict[path_] = value_
                        s = self.context.format_call(
                            "set_source_files_properties",
                            [path_, "PROPERTIES", "INCLUDE_DIRECTORIES"],
                            [value_],
                        )
                        f.write(s)
                    elif validation_dict[path_] != value_:
                        prev_value = validation_dict[path_]
                        raise ValueError(
                            "{}: incompatible include dirs: {} vs {}.".format(
                                path_, prev_value, value_
                            )
                        )

            sources_arg = list(map(lambda t: t["path"], cmake_supported_srcs))
            system_objects = []
            if target.get("objects"):
                object_targets = []
                external_objects = []
                for obj in target["objects"]:
                    object_target = self.context.target_index.get(obj)
                    if object_target:
                        if object_target["type"] in ("module", "module_copy"):
                            object_targets.append(object_target)
                        else:
                            external_objects.append(obj)
                    elif obj.startswith(self.context.source_dir_placeholder):
                        external_objects.append(obj)
                    else:
                        system_objects.append(obj)
                if (object_targets or external_objects) and not sources_arg:
                    # CMake gets confused if target has only object files
                    specify_linker_language = True
                for t in object_targets:
                    if t.get("post_build_commands"):
                        # OBJECT libraries don't support POST_BUILD commands.
                        # To work around that, we can use CMake knowledge:
                        # * OBJECT libraries don't support setting output location and
                        #   $<TARGET_OBJECTS:target> (CMake build path) != target['output'] (path expected by BOM).
                        # We can add a add_custom_command that processes $<TARGET_OBJECTS:target>
                        # and outputs processed object to target['output'].
                        # So instead of $<TARGET_OBJECTS:>, we should reference target['output'] here.
                        sources_arg.append(t["output"])
                    else:
                        sources_arg.append("$<TARGET_OBJECTS:{}>".format(t["name"]))
                if external_objects:
                    sources_arg += external_objects
                    s = self.context.format_call(
                        "set_source_files_properties",
                        [],
                        external_objects,
                        ["PROPERTIES", "EXTERNAL_OBJECT", "ON"],
                    )
                    f.write(s)

            yasm_srcs = list(
                filter(lambda t: t["language"] == "YASM", target["sources"])
            )
            # CMake targets cannot have no sources except interface libraries.
            # Sources can be specified during target definition 
            # (add_lirary, add_executable), or via target_sources() call.
            if not sources_arg and (
                target["module_type"] != ModuleTypes.object_lib or not yasm_srcs
            ):
                if target["module_type"] != ModuleTypes.interface:
                    sources_arg = self.create_empty_source_arg(f)

            format_target_func = {
                ModuleTypes.object_lib: self.context.format_object_library,
                ModuleTypes.static_lib: self.context.format_static_library,
                ModuleTypes.shared_lib: self.context.format_shared_library,
                ModuleTypes.executable: self.context.format_executable,
                ModuleTypes.interface: self.context.format_interface,
            }
            f.write(
                format_target_func[target["module_type"]](target["name"], sources_arg)
            )

            if specify_linker_language:
                assert (
                    len(self.context.languages) > 0
                ), "At least one language must be enabled"
                # Probably any other LINKER_LANGUAGE value will work as well
                s = self.context.format_call(
                    "set_target_properties",
                    [target["name"]],
                    ["PROPERTIES", "LINKER_LANGUAGE", self.context.languages[0]],
                )
                f.write(s)

            link_flags = system_objects
            if target.get("link_flags"):
                link_flags += target["link_flags"]

            if link_flags:
                f.write(self.context.format_link_flags(target["name"], link_flags))

            link_libraries = []
            if target.get("libs"):
                prev_gcc_whole_archive = False
                for lib in target["libs"]:
                    gcc_whole_archive = False
                    if isinstance(lib, dict):
                        gcc_whole_archive = bool(lib.get("gcc_whole_archive"))
                        value = lib["value"]
                    else:
                        value = lib
                    lib_target = self.context.target_index.get(value)
                    if lib_target:
                        if lib_target["type"] in ["module", "module_copy"]:
                            value = lib_target["name"]
                        elif value.endswith(".lib"):
                            value = value[:-4]  # remove .lib suffix
                    else:
                        if value.endswith(".lib"):
                            value = value[:-4]  # remove .lib suffix
                        if value in system_library_map:
                            value = system_library_map[value]
                    if value:
                        if gcc_whole_archive != prev_gcc_whole_archive:
                            if gcc_whole_archive:
                                link_libraries.append("-Wl,-whole-archive")
                            else:
                                link_libraries.append("-Wl,-no-whole-archive")
                            prev_gcc_whole_archive = gcc_whole_archive
                        link_libraries.append(value)
                if prev_gcc_whole_archive:
                    link_libraries.append("-Wl,-no-whole-archive")

            visibility = "PRIVATE"
            if target["module_type"] == ModuleTypes.interface:
                visibility = "INTERFACE"

            if link_libraries:
                s = self.context.format_call(
                    "target_link_libraries",
                    [target["name"], visibility],
                    link_libraries,
                )
                f.write(s)

            if target["compile_flags"]:
                values = target["compile_flags"]
                values = self.context.process_compile_flags(values)
                s = self.context.format_call(
                    "target_compile_options",
                    [target["name"], visibility],
                    join_nested_lists(values),
                )
                f.write(s)

            if target["include_dirs"]:
                s = self.context.format_call(
                    "target_include_directories",
                    [target["name"], visibility],
                    target["include_dirs"],
                )
                f.write(s)

            language_flag_properties = sorted(
                self.context.language_flag_properties.items(),
                key=operator.itemgetter(1),
            )
            for property, language in language_flag_properties:
                flags = target.get(property)
                if not flags:
                    continue
                flags = self.context.process_compile_flags(flags)
                s = self.context.format_call(
                    "target_language_compile_options",
                    [target["name"], language, "PRIVATE"],
                    flatten_list(flags),
                )
                f.write(s)

            language_include_properties = sorted(
                self.context.language_include_properties.items(),
                key=operator.itemgetter(1),
            )
            for property, language in language_include_properties:
                dirs = target.get(property)
                if not dirs:
                    continue
                s = self.context.format_call(
                    "target_language_include_directories",
                    [target["name"], language, "PRIVATE"],
                    dirs,
                )
                f.write(s)

            if yasm_srcs:
                yasm_sources_arg = list(map(lambda t: t["path"], yasm_srcs))
                s = self.context.format_call(
                    "target_yasm_sources", [target["name"], "PRIVATE"], yasm_sources_arg
                )
                f.write(s)

            if target["dependencies"]:
                s = self.context.format_dependencies(target)
                f.write(s)

            if target["module_type"] != ModuleTypes.interface:
                if target["module_name"] and target["module_name"] != target["name"]:
                    s = self.context.format_call(
                        "set_target_properties",
                        [target["name"], "PROPERTIES", "OUTPUT_NAME"],
                        [target["module_name"]],
                    )
                    f.write(s)

            msvc_import_lib = target.get("msvc_import_lib")
            if msvc_import_lib and self.context.platform == "windows":
                if isinstance(msvc_import_lib, list):
                    msvc_import_lib = msvc_import_lib[0]
                descr = Windows.parse_import_lib(msvc_import_lib)
                if descr["module_name"] != target["module_name"]:
                    # Custom import lib name
                    s = self.context.format_call(
                        "set_target_properties",
                        [target["name"], "PROPERTIES", "ARCHIVE_OUTPUT_NAME"],
                        [descr["module_name"]],
                    )
                    f.write(s)

            if (
                target["module_type"] != ModuleTypes.object_lib
                and not self.context.flat_build_dir
            ):
                output_dir = get_target_output_dir(target)
                if output_dir != self.context.build_dir_placeholder:
                    output_dir = output_dir.replace(
                        self.context.build_dir_placeholder + "/", ""
                    )
                    requires_archive_output_dir = False
                    requires_runtime_output_dir = False
                    if target["module_type"] == ModuleTypes.shared_lib:
                        if self.context.platform == "windows":
                            requires_runtime_output_dir = True
                            requires_archive_output_dir = True
                        else:
                            s = self.context.format_call(
                                "set_target_output_subdir",
                                [target["name"], "LIBRARY_OUTPUT_DIRECTORY"],
                                [output_dir],
                            )
                            f.write(s)
                    if target["module_type"] == ModuleTypes.static_lib:
                        requires_archive_output_dir = True
                    elif target["module_type"] != ModuleTypes.interface:
                        requires_runtime_output_dir = True
                    if requires_runtime_output_dir:
                        s = self.context.format_call(
                            "set_target_output_subdir",
                            [target["name"], "RUNTIME_OUTPUT_DIRECTORY"],
                            [output_dir],
                        )
                        f.write(s)
                    if requires_archive_output_dir:
                        s = self.context.format_call(
                            "set_target_output_subdir",
                            [target["name"], "ARCHIVE_OUTPUT_DIRECTORY"],
                            [output_dir],
                        )
                        f.write(s)

            version = target.get("version")
            if version is not None:
                s = self.context.format_call(
                    "set_target_properties",
                    [target["name"], "PROPERTIES", "VERSION"],
                    [version],
                )
                f.write(s)

            compatibility_version = target.get("compatibility_version")
            if compatibility_version is not None:
                s = self.context.format_call(
                    "set_target_properties",
                    [target["name"], "PROPERTIES", "SOVERSION"],
                    [compatibility_version],
                )
                f.write(s)

        post_build_commands = target.get("post_build_commands") or []
        for cmd_target in post_build_commands:
            cmd_target = cmd_target.copy()
            cmd_target["type"] = "cmd"
            if target["module_type"] == ModuleTypes.object_lib:
                # CMake doesn't support POST_BUILD commands for OBJECT libraries
                # See further explanation above (search POST_BUILD)
                cmd_target["name"] = target["name"] + "_post_build"
                cmd_target["dependencies"] = [target["output"]]
                cmd_target["output"] = target["output"]
                pass
            else:
                cmd_target["post_build"] = target["name"]
            self.cmd_generator.generate(cmd_target)

        return True


__all__ = ["CMakeModule"]
