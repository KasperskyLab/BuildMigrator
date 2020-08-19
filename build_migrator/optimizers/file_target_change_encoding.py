from build_migrator.modules import Optimizer
from build_migrator.common.encoding_detection import (
    read_lines_from_binary,
    convert_lines_to_binary,
)
from build_migrator.common.wildcard_matcher import WildcardMatcher


class FileTargetChangeEncoding(Optimizer):
    priority = 2

    @staticmethod
    def add_arguments(arg_parser):
        arg_parser.add_argument(
            "--file_target_change_encoding",
            metavar=("PATHMASK", "SOURCE_ENC", "DEST_ENC"),
            nargs=3,
            action="append",
            dest="file_target_change_encodings",
            help="Change encoding for files matching specified mask. "
            "Supported encoding names are the same as for io module.",
        )

    def __init__(self, context, file_target_change_encodings=None):
        self.is_disabled = not file_target_change_encodings
        if self.is_disabled:
            return

        self.file_target_change_encodings = []
        for mask, src_enc, dest_enc in file_target_change_encodings:
            self.file_target_change_encodings.append(
                (WildcardMatcher([mask]), src_enc, dest_enc)
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
            for mask, src_enc, dest_enc in self.file_target_change_encodings:
                path = file.get("output")
                if path is None:
                    path = file.get("location")
                if not mask.match(path):
                    continue
                lines = read_lines_from_binary(file["content"], encoding=src_enc)
                data = convert_lines_to_binary(lines, encoding=dest_enc)
                file["content"] = data

        return targets


__all__ = ["FileTargetChangeEncoding"]
