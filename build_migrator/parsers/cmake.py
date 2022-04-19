from copy import copy
import logging
from build_migrator.helpers import get_copy_target
from build_migrator.modules import Parser
from build_migrator.common.argument_parser_ex import ArgumentParserEx
from build_migrator.common.os_ext import get_platform


logger = logging.getLogger(__name__)


class CMake(Parser):
    priority = 7

    @staticmethod
    def add_arguments(arg_parser):
        pass

    def __init__(self, context):
        self.context = context
        self.platform = context.platform
        self.program_re = self.platform.get_program_path_re("cmake")

        self.parser = ArgumentParserEx(prog="cmake")
        self.parser.add_argument("-E", dest="command", nargs="+")
        self.parser.add_argument("-f", action="append", dest="command", nargs="+")

    def parse(self, target):
        tokens = target.get("tokens")
        if not tokens:
            return target

        if not self.program_re.match(tokens[0]):
            return target

        namespace = self.parser.parse_args(tokens[1:])

        if not namespace.command:
            return target

        command = namespace.command[0]
        args = namespace.command[1:]

        dependencies = []
        targets = []
        if command == "cmake_symlink_library":
            # on Mac
            source = self.context.get_file_arg(
                self.context.normalize_path(args[0], ignore_working_dir=True), dependencies
            )
            destinations = args[1:]
            for dest in destinations:
                target_dependencies = copy(dependencies)
                output = self.context.get_output(dest, target_dependencies)
                targets.append(
                    get_copy_target(None, source, output, target_dependencies)
                )
        else:
            logger.warning("Unsupported CMake command: {}".format(command))

        return targets


__all__ = ["CMake"]
