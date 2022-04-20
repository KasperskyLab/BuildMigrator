from build_migrator.common.algorithm import flatten_list
from build_migrator.modules import Generator


command_tmpl = """
    COMMAND
        ${{CMAKE_COMMAND}} -E env{params}
        {command}"""

cmd_tmpl = """
add_custom_command(OUTPUT {output}{command}{depends}{working_dir}
    VERBATIM
)
add_custom_target({name} ALL DEPENDS {output})
"""

post_build_cmd_tmpl = """
add_custom_command(TARGET {target_name} POST_BUILD{command}{working_dir}
    VERBATIM
)
"""

find_program_tmpl = """
find_program({var} {name})
if(NOT {var})
    message(FATAL_ERROR "{name} not found")
endif()
"""


class CMakeCmd(Generator):
    priority = 1

    @staticmethod
    def add_arguments(arg_parser):
        pass

    def __init__(self, context, cmake_project_name=None):
        self.context = context
        if cmake_project_name is None:
            self.var_prefix = ""
        else:
            self.var_prefix = cmake_project_name.upper() + "_"
        self.found_programs = {"cmake": "CMAKE_COMMAND", "objcopy": "CMAKE_OBJCOPY"}

    def generate(self, target):
        if not target["type"] == "cmd":
            return False

        with self.context.open("CMakeLists.txt", "a") as f:
            program = target["program"]
            program_var = self.found_programs.get(program)
            if program_var is None:
                program_var = self.var_prefix + program.upper()
                s = self.context.format(
                    find_program_tmpl, name=program, var=program_var
                )
                f.write(s)
                self.found_programs[program] = program_var

            working_dir = target.get("working_dir")
            if working_dir is None:
                working_dir = ""
            else:
                working_dir = '\n    WORKING_DIRECTORY "{}"'.format(working_dir)

            object_lib_deps = []
            cmd_dependencies_str = ""
            dependencies = target.get("dependencies")
            if dependencies:
                cmd_dependencies_str = "\n    DEPENDS"
                for dep in dependencies:
                    _tgt = self.context.target_index.get(dep)
                    if _tgt:
                        if _tgt.get("type") == "module":
                            if _tgt["module_type"] == "object_lib":
                                object_lib_deps.append(_tgt)
                            dep = _tgt["name"]
                        elif _tgt.get("type") == "directory":
                            # Don't add directory dependencies, it's unnecessary
                            continue
                    cmd_dependencies_str += "\n        {}".format(dep)

            command_args = []
            for arg in flatten_list(target["args"]):
                if arg in self.context.target_index:
                    arg_target = self.context.target_index[arg]
                    if (
                        arg_target["type"] == "module"
                        and arg_target["module_type"] != "object_lib"
                    ):
                        arg = "$<TARGET_FILE:{}>".format(arg_target["name"])
                command_args.append(arg)
            command = ["${" + program_var + "}"] + command_args

            params = ""
            if target.get("parameters"):
                params = " " + " ".join(
                    "{}={}".format(k, v) for k, v in target["parameters"].items()
                )

            command_str = self.context.format(
                command_tmpl, params=params, command=" ".join(command),
            )
            # CMake doesn't provide built-in way to set object file path.
            # Explicitly copy object files to expected locations
            for _tgt in object_lib_deps:
                cmd = '${{CMAKE_COMMAND}} -E copy_if_different "$<TARGET_OBJECTS:{name}>" "{output}"'.format(
                    name=_tgt["name"], output=_tgt["output"],
                )
                command_str = (
                    self.context.format(command_tmpl, params=params, command=cmd,)
                    + command_str
                )

            post_build_target_name = target.get("post_build")
            if post_build_target_name:
                s = self.context.format(
                    post_build_cmd_tmpl,
                    target_name=post_build_target_name,
                    command=command_str,
                    working_dir=working_dir,
                )
            else:
                output = target["output"]
                for o in target.get("msvc_import_lib") or []:
                    output += "\n    " + o
                name = target.get("name")
                if name is None:
                    name = output.split("@")[-1][1:].replace(".", "_").replace("/", "_")
                s = self.context.format(
                    cmd_tmpl,
                    name=name,
                    output=output,
                    command=command_str,
                    depends=cmd_dependencies_str,
                    working_dir=working_dir,
                )
            f.write(s)

        return True


__all__ = ["CMakeCmd"]
