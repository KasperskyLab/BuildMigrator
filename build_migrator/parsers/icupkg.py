import logging
import platform
from build_migrator.helpers import get_command_target
from build_migrator.common.os_ext import get_platform
from build_migrator.common.argument_parser_ex import ArgumentParserEx
from .base.parser_base import ParserBase


logger = logging.getLogger(__name__)


class Icupkg(ParserBase):
    priority = 7

    def __init__(self, context, platform=platform.system().lower()):
        ParserBase.__init__(self, context)

        self.platform = get_platform(platform)
        self.program_re = self.platform.get_program_path_re("icupkg")

        # https://helpmanual.io/help/icupkg/
        self.parser = ArgumentParserEx()
        self.parser.set(dest=None, raw_dest="args")
        self.parser.add_argument("--type", "-t", choices=["l", "b", "e"])
        self.parser.add_argument("--copyright", "-c")
        self.parser.add_argument("--comment", "-C")
        self.parser.add_argument("--add", "-a")
        self.parser.add_argument("--remove", "-r")
        self.parser.add_argument("--extract", "-x")
        self.parser.add_argument("--writepkg", "-w", action="store_true")
        self.parser.add_argument("--matchmode", "-m")
        self.parser.add_argument("--auto_toc_prefix", action="store_true")
        self.parser.add_argument("--auto_toc_prefix_with_type", action="store_true")
        self.parser.add_argument("--sourcedir", "-s", raw_handler=self.input_dir)
        self.parser.add_argument("--destdir", "-d", raw_handler=self.input_dir)
        self.parser.add_argument("--list", "-l", action="store_true")
        self.parser.add_argument("--outlist", "-o", raw_handler=self.output_file)
        self.parser.add_argument("infilename", raw_handler=self.input_file)
        self.parser.add_argument("outfilename", nargs="?", raw_handler=self.output_file)

    def parse(self, target):
        tokens = target.get("tokens") or []
        if not tokens:
            return target

        if not self.program_re.match(tokens[0]):
            return target

        tokens.pop(0)
        namespace = self.parser.parse_args(tokens)
        return get_command_target(
            None,
            program="icupkg",
            args=namespace.args,
            output=namespace.output,
            dependencies=namespace.dependencies,
        )


__all__ = ["Icupkg"]
