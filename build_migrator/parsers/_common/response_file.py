import logging
import os
from build_migrator.modules import Parser
from build_migrator.parsers._common.command_tokenizer import cmdline_split


logger = logging.getLogger(__name__)


class ResponseFile(Parser):
    priority = 5

    @staticmethod
    def add_arguments(arg_parser):
        pass

    @staticmethod
    def is_applicable(project=None, log_type=None):
        return True

    def __init__(self, context, platform=None):
        self.context = context
        self.platform = platform
        self.rspfiles = {}

    def _get_args(self, cmdline):
        cmdline = cmdline.replace("\n", " ")
        platform = 0 if self.platform == "windows" else 1
        return cmdline_split(cmdline, platform=platform)

    def parse(self, target):
        tokens = target.get("tokens")
        if not tokens:
            return target

        if tokens[-1].startswith("@"):
            path = self.context.normalize_path(target["tokens"][-1][1:])
            if os.path.exists(path):
                with open(path, "rt") as f:
                    target["tokens"][-1:] = self._get_args(f.read())
            else:
                output = self.context.get_output(path)
                response_file_target = self.context.target_index.get(output)
                if response_file_target is not None:
                    target["tokens"][-1:] = self._get_args(
                        response_file_target["content"]
                    )
                else:
                    logger.error(
                        "Response file not found: %s. Log may be parsed incorrectly.",
                        path,
                    )

        return target


__all__ = ["ResponseFile"]
