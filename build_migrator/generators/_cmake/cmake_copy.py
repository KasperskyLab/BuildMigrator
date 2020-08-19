import os
from .cmake_cmd import CMakeCmd

copy_tmpl = "configure_file({input} {output} COPYONLY)\n"


class CMakeCopy(CMakeCmd):
    priority = 1

    @staticmethod
    def add_arguments(arg_parser):
        pass

    def __init__(self, context, project=None):
        CMakeCmd.__init__(self, context, project)

    @staticmethod
    def _create_symlink_cmd(name, source, output):
        source_rel = os.path.relpath(source, os.path.dirname(output)).replace("\\", "/")

        return {
            "name": name,
            "type": "cmd",
            "program": "cmake",
            "args": ["-E", "create_symlink", source_rel, output],
            "dependencies": [source],
            "output": output,
        }

    def generate(self, target):
        if target["type"] != "copy":
            return False

        source = target["source"]
        if not self.context.get_copy_origin(source):
            # origin is a file in source dir: configure_file
            with self.context.open("CMakeLists.txt", "a") as cmake_file:
                s = self.context.format(
                    copy_tmpl, input=target["source"], output=target["output"]
                )
                cmake_file.write(s)
        else:
            # origin is a file in build dir: add_custom_command
            target = self._create_symlink_cmd(target["name"], source, target["output"])
            CMakeCmd.generate(self, target)

        return True


__all__ = ["CMakeCopy"]
