import logging
import os

from build_migrator.common.os_ext import get_platform
from build_migrator.common.argument_parser_ex import ArgumentParserEx
from build_migrator.helpers import get_command_target

from .base.parser_base import ParserBase

logger = logging.getLogger(__name__)


class MsvcMc(ParserBase):
    priority = 7

    @staticmethod
    def add_arguments(arg_parser):
        pass

    def __init__(self, context, platform=None):
        ParserBase.__init__(self, context)

        self.platform = get_platform(platform)
        self.program_re = self.platform.get_program_path_re("mc")

        # https://docs.microsoft.com/en-us/windows/windows/wes/message-compiler--mc-exe-
        # Currently, only small subset of flags is supported
        self.parser = ArgumentParserEx()
        self.parser.set(raw_dest="args")
        self.parser.add_argument("-h", raw_handler=self.input_dir, dest="header_dir")
        self.parser.add_argument("-r", raw_handler=self.input_dir, dest="resource_dir")
        self.parser.add_argument(
            "manifest_file", raw_handler=self.input_file, dest="manifest_file"
        )

    def parse(self, target):
        tokens = target.get("tokens") or []
        if not tokens:
            return target

        if not self.program_re.match(tokens[0]):
            return target

        tokens.pop(0)
        namespace = self.parser.parse_args(tokens)

        if namespace.header_dir is None:
            namespace.header_dir = target["working_dir"]
        header_dir = self.context.get_dir_arg(
            self.context.normalize_path(namespace.header_dir)
        )

        if namespace.resource_dir is None:
            namespace.resource_dir = target["working_dir"]
        resource_dir = self.context.get_dir_arg(
            self.context.normalize_path(namespace.resource_dir)
        )

        filename_no_ext = os.path.basename(namespace.manifest_file)
        filename_no_ext = os.path.splitext(filename_no_ext)[0]

        output = [
            header_dir + "/" + filename_no_ext + ".h",
            resource_dir + "/" + filename_no_ext + ".rc",
        ]

        return get_command_target(
            None, "mc", namespace.args, output, namespace.dependencies
        )


__all__ = ["MsvcMc"]
