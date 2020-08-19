from build_migrator.helpers import get_minified_target
from build_migrator.modules import Generator


class CMakeModuleCopy(Generator):
    priority = 1

    @staticmethod
    def add_arguments(arg_parser):
        pass

    def __init__(self, context):
        self.context = context

    # recursively search for original 'module' target
    def _find_source_module_target(self, source):
        target = self.context.target_index.get(source)
        if target["type"] == "module":
            return target
        elif target["type"] == "module_copy":
            return self._find_source_module_target(target["source"])
        else:
            # unexpected target type
            assert False, get_minified_target(target)

    def generate(self, target):
        if not target["type"] == "module_copy":
            return False

        source_target = self._find_source_module_target(target["source"])
        if target["name"] != source_target["name"]:
            with self.context.open("CMakeLists.txt", "a") as f:
                # Additional newline between targets
                f.write("\n")

                cmake_function = "add_library"
                if source_target["module_type"] == "executable":
                    cmake_function = "add_executable"

                s = self.context.format_call(
                    cmake_function, [target["name"]], ["ALIAS", source_target["name"]]
                )
                f.write(s)

        return True


__all__ = ["CMakeModuleCopy"]
