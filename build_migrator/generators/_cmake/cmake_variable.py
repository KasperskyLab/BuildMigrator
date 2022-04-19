from build_migrator.modules import Generator
from build_migrator.common.algorithm import join_nested_lists
from .cmake_module import system_library_map


class CMakeVariable(Generator):
    priority = 1

    @staticmethod
    def add_arguments(arg_parser):
        arg_parser.add_argument(
            "--default_var_value",
            metavar=("VAR_NAME", "VALUE"),
            nargs=2,
            action="append",
            dest="default_var_values",
            help="Change default value for generated CMake variable",
        )

    def __init__(self, context, default_var_values=None):
        self.context = context
        self.default_values = {}
        for key, value in default_var_values or []:
            self.default_values[key] = value

    def generate(self, target):
        if target["type"] == "variable":

            self.context.placeholders.append(target["placeholder"])
            self.context.values[target["placeholder"]] = "${" + target["name"] + "}"
            self.context.substitutions[target["placeholder"]] = (
                "@" + target["name"] + "@"
            )

            if target["name"] in self.default_values:
                target["value"] = self.default_values[target["name"]]

            if self.context.platform_name == "windows" and target["name"].startswith("libs"):
                # process MSVC library lists
                target["value"] = [
                    x[:-4] if x.endswith(".lib") else x for x in target["value"]
                ]
                # map to CMake-specific (or empty) names
                target["value"] = [
                    system_library_map.get(x, x) for x in target["value"]
                ]
                # skip empty
                target["value"] = [x for x in target["value"] if x]

            # Join link flags created by v1 optimizer into single string.
            # This is needed to avoid deviating from previously generated CMakeLists.txt content
            if self.context.project_name:
                link_flags_v1_var_name = self.context.project_name.upper() + "_LINK_FLAGS"
            else:
                link_flags_v1_var_name = "LINK_FLAGS"
            if target["name"] == link_flags_v1_var_name:
                target["value"] = " ".join(join_nested_lists(target["value"]))

            with self.context.open("CMakeLists.txt", "a") as f:
                flags = target["value"]
                flags = self.context.process_compile_flags(flags)
                if target["name"].lower() == target["name"]:
                    f.write(self.context.format_variable(target["name"], flags))
                else:
                    f.write(self.context.format_cache_variable(target["name"], flags))

            return True

        return False


__all__ = ["CMakeVariable"]
