import re
import copy
from build_migrator.modules import Parser


class ReplaceLine(Parser):
    priority = -1

    @staticmethod
    def add_arguments(arg_parser):
        arg_parser.add_argument(
            "--replace_line",
            metavar=("REGEX", "REPL"),
            nargs=2,
            action="append",
            dest="replace_line",
            help="Replaces occurences of regex in build log. "
            "Applicable for make, ninja or msbuild --log_type.",
        )

    def __init__(self, context, replace_line=None):
        self.replacements = []
        for pattern, repl in replace_line or []:
            self.replacements.append((re.compile(pattern), repl))
        self.context = context

    @staticmethod
    def is_applicable(log_type=None):
        return log_type in ["make", "ninja", "msbuild"]

    def __replace_line__(self, line):
        replaced_line = line
        for r, repl in self.replacements:
            replaced_line = r.sub(repl, replaced_line)
        return replaced_line

    def parse(self, target):
        if "line" in target:
            new_line = self.__replace_line__(target["line"])
            if new_line != target["line"]:
                target_with_replaced_line = copy.deepcopy(target)
                target_with_replaced_line["line"] = new_line
                return target_with_replaced_line

        return target


__all__ = ["ReplaceLine"]
