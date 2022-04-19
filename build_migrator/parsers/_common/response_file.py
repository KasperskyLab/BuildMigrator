import logging
import os
from build_migrator.modules import Parser
from build_migrator.parsers._common.command_tokenizer import CommandTokenizer


logger = logging.getLogger(__name__)


class ResponseFile(Parser):
    priority = 5

    @staticmethod
    def add_arguments(arg_parser):
        pass

    def __init__(self, context):
        self.context = context
        self.rspfiles = {}
        self.tokenizer = CommandTokenizer(context)

    def _get_args(self, cmdline):
        return self.tokenizer.cmdline_split(cmdline.replace("\n", " "))

    def parse(self, target):
        tokens = target.get("tokens")
        if not tokens:
            return target

        for idx in reversed(range(len(tokens))):
            if tokens[idx].startswith("@"):
                path = self.context.normalize_path(tokens[idx][1:])
                if os.path.exists(path):
                    with open(path, "rt") as f:
                        tokens[idx:idx+1] = self._get_args(f.read())
                else:
                    output = self.context.get_output(path)
                    response_file_target = self.context.target_index.get(output)
                    if response_file_target is not None:
                        tokens[idx:idx+1] = self._get_args(
                            response_file_target["content"]
                        )
                    else:
                        logger.error(
                            "Response file not found: %s. Log may be parsed incorrectly.",
                            path,
                        )

        return target


__all__ = ["ResponseFile"]
