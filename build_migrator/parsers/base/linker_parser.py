import argparse
import re

from build_migrator.helpers import filter_flags
from .parser_base import ParserBase


class LinkerParser(ParserBase):
    @staticmethod
    def add_arguments(arg_parser):
        try:
            arg_parser.add_argument(
                "--ignore_link_flags",
                metavar="REGEX",
                nargs="+",
                help="Omit link flags matching specified regular expression.\n"
                "Parser will behave as if flags weren't present "
                "in the build log.",
            )
        except argparse.ArgumentError:
            # Already added by other LinkerParser subclass
            pass

    def __init__(self, context, ignore_link_flags=None):
        ParserBase.__init__(self, context)

        self.ignore_link_flags_rxs = []
        for s in ignore_link_flags or []:
            self.ignore_link_flags_rxs.append(re.compile(s))

    def process_namespace(self, namespace):
        namespace.link_flags = filter_flags(
            self.ignore_link_flags_rxs, namespace.link_flags
        )
