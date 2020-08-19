import argparse
import re

from build_migrator.helpers import filter_flags
from .parser_base import ParserBase


class CompilerParser(ParserBase):
    @staticmethod
    def add_arguments(arg_parser):
        try:
            arg_parser.add_argument(
                "--ignore_compile_flags",
                metavar="REGEX",
                nargs="+",
                help="Omit compilation flags matching specified regular expression.\n"
                "Parser will behave as if flags weren't present "
                "in the build log.",
            )
        except argparse.ArgumentError:
            # Already added by other CompilerParser subclass
            pass

    def __init__(self, context, ignore_compile_flags=None):
        ParserBase.__init__(self, context)

        self.ignore_compile_flags_rxs = []
        for s in ignore_compile_flags or []:
            self.ignore_compile_flags_rxs.append(re.compile(s))

    def process_namespace(self, namespace):
        if hasattr(namespace, "include_dirs"):
            namespace.include_dirs = list(
                map(
                    lambda p: p[2:],
                    filter_flags(
                        self.ignore_compile_flags_rxs,
                        ["-I" + d for d in namespace.include_dirs],
                    ),
                )
            )
        if hasattr(namespace, "compile_flags"):
            namespace.compile_flags = filter_flags(
                self.ignore_compile_flags_rxs, namespace.compile_flags
            )
