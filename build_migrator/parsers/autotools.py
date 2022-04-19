import logging
import os
import re
import build_migrator.common.os_ext as os_ext
from build_migrator.modules import Parser
from ._common.command_tokenizer import CommandTokenizer
from ._common.replace_line import ReplaceLine
from ._common.response_file import ResponseFile
from ._common.inline_file_content import InlineFileContent


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)


class LineAccumulator(Parser):

    priority = 2

    @staticmethod
    def add_arguments(arg_parser):
        pass

    @staticmethod
    def is_applicable(log_type=None):
        return log_type in ["make", "ninja"]

    def __init__(self, context):
        self.context = context
        self.accumulator = ""

    def parse(self, target):
        line = target.get("line") or ""

        if line.endswith("\\"):
            target["line"] = ""
            self.accumulator += line[:-1]
        else:
            target["line"] = self.accumulator + line
            self.accumulator = ""

        return target


# Provides directory context for commands executing inside make
# See https://www.gnu.org/software/make/manual/html_node/_002dw-Option.html
class MakeLog(Parser):
    directory_re = re.compile(
        r"(?P<mode>Entering|Leaving) directory ['`](?P<path>[^'`]+)'"
    )

    priority = 0

    @staticmethod
    def add_arguments(arg_parser):
        pass

    @staticmethod
    def is_applicable(log_type=None):
        return log_type == "make"

    def __init__(self, context):
        self.context = context
        self.directory_stack = [context.working_dir]

    @property
    def working_dir(self):
        return self.directory_stack[-1]

    def enter(self, dir):
        logger.info("Changing current directory: '{}'".format(dir))
        self.directory_stack.append(dir)
        self.context.working_dir = self.working_dir

    def leave(self, dir):
        if self.working_dir == dir:
            self.directory_stack.pop()
            self.context.working_dir = self.working_dir
        else:
            fmt = (
                "Directory stack mismatch: expected to leave {!r}, but top dir is {!r}"
            )
            logger.error(fmt.format(dir, self.working_dir))

    def parse(self, target):
        line = target.get("line") or ""

        match = self.directory_re.search(line)
        if match:
            path = match.group("path")
            dir = self.context.normalize_path(path)

            if match.group("mode") == "Entering":
                self.enter(dir)
            else:
                self.leave(dir)

            target["line"] = ""

        target["working_dir"] = self.context.working_dir

        return target


__all__ = [
    "LineAccumulator",
    "MakeLog",
    "CommandTokenizer",
    "ReplaceLine",
    "ResponseFile",
    "InlineFileContent",
]
