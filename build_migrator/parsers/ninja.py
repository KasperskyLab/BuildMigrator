import re
from build_migrator.parsers.autotools import (
    MakeLog,
    LineAccumulator,
    CommandTokenizer,
    ReplaceLine,
    ResponseFile,
    InlineFileContent,
)


# Provides directory context for commands executing via ninja
# Strips prefix prefixes like '[1/999]' from command line messages
class NinjaLog(MakeLog):
    prefix_re = re.compile(r"^\[\d+/\d+\] ")

    priority = 0

    @staticmethod
    def add_arguments(arg_parser):
        pass

    @staticmethod
    def is_applicable(project=None, log_type=None):
        return log_type == "ninja"

    def __init__(self, context):
        MakeLog.__init__(self, context)
        self.context = context

    def parse(self, target):
        target = MakeLog.parse(self, target)

        if target is not None and target.get("line"):
            target["line"] = self.prefix_re.sub("", target["line"])

        return target


__all__ = [
    "NinjaLog",
    "LineAccumulator",
    "CommandTokenizer",
    "ReplaceLine",
    "ResponseFile",
    "InlineFileContent",
]
