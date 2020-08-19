import re
from build_migrator.modules import Optimizer
from build_migrator.common.encoding_detection import (
    detect_encoding_by_bom,
    read_lines_from_binary,
    convert_lines_to_binary,
)
from build_migrator.common.wildcard_matcher import WildcardMatcher


class FileTargetGsub(Optimizer):
    priority = 3

    @staticmethod
    def add_arguments(arg_parser):
        arg_parser.add_argument(
            "--file_target_gsub",
            metavar=("PATHMASK", "REGEX", "REPL"),
            nargs=3,
            action="append",
            dest="file_target_gsubs",
            help="Substitute content for files matching specified mask.",
        )

    def __init__(self, context, file_target_gsubs=None):
        self.is_disabled = not file_target_gsubs
        if self.is_disabled:
            return

        self.file_target_gsubs = []
        for mask, regex, repl in file_target_gsubs:
            self.file_target_gsubs.append(
                (WildcardMatcher([mask]), re.compile(regex), repl)
            )
        self.context = context

    def optimize(self, targets):
        if self.is_disabled:
            return targets

        files = []
        for t in targets:
            if t["type"] == "file":
                files.append(t)

        for file in files:
            for mask, regex, repl in self.file_target_gsubs:
                path = file.get("output")
                if path is None:
                    path = file.get("location")
                if path.endswith(".rc"):
                    path = path
                    pass
                if not mask.match(path):
                    continue

                encoding = detect_encoding_by_bom(data=file["content"])[0]
                lines = []
                for line in read_lines_from_binary(file["content"], encoding=encoding):
                    line = regex.sub(repl, line)
                    lines.append(line)

                data = convert_lines_to_binary(lines, encoding=encoding)
                file["content"] = data

        return targets


__all__ = ["FileTargetGsub"]
