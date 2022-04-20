import logging
from build_migrator.generators._bazel.rule_cc import RuleCc


logger = logging.getLogger(__name__)


class CopyFile(RuleCc):
    def __init__(self, context):
        self.context = context
        self._function_loaded = False

    def generate(self, target):
        if target["type"] != "copy":
            return False

        self._write_preamble()

        logger.debug(' > Copy "{}" to "{}"'.format(target["source"], target["output"]))
        self.context.write_line(
            'copy_file("{}", "{}", "{}", allow_symlink=True)',
            target["name"],
            target["source"],
            target["output"],
        )

        return True

    def _write_preamble(self):
        if not self._function_loaded:
            self.context.write_line(
                'load("@bazel_skylib//rules:copy_file.bzl", "copy_file")'
            )
            self._function_loaded = True
