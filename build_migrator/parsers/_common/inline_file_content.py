import logging
import os
from build_migrator.helpers import get_file_target
from build_migrator.modules import Parser


logger = logging.getLogger(__name__)


# Log example:
# echo line1 > C:\Temp\nm16A5.tmp
# echo line2 >> C:\Temp\nm16A5.tmp
# echo line3 >> C:\Temp\nm16A5.tmp
class InlineFileContent(Parser):
    priority = 4

    def __init__(self, context, platform=None):
        self.context = context
        self.platform = platform

    def parse(self, target):
        tokens = target.get("tokens")
        if not tokens:
            return target

        redirections = target.get("redirection") or []
        for redirection in redirections:
            dst_path = redirection.get("dst")
            if dst_path:
                dst_path = self.context.normalize_path(dst_path)
            op = redirection.get("op")
            if (
                dst_path
                and not os.path.exists(dst_path)
                and tokens[0] == "echo"
                and op in (">", ">>")
            ):
                output = self.context.get_output(dst_path)
                # parse `nmake /U` output
                line = " ".join(tokens[1:]) + "\n"
                file_target = self.context.target_index.get(output)
                if file_target is None:
                    logger.info("Found inline file: %s", dst_path)
                    file_target = get_file_target("", output)
                    file_target = self.context.register_target(file_target)[0]
                if op == ">":
                    file_target["content"] = line
                else:
                    file_target["content"] += line

        return target


__all__ = ["InlineFileContent"]
