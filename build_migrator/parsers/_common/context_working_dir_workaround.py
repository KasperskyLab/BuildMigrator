import logging
from build_migrator.modules import Parser


logger = logging.getLogger(__name__)


# See comment for target['context.working_dir'] in msbuild_log.py
# Also used by StraceTokenizer
class ContextWorkingDirWorkaround(Parser):
    priority = 2

    @staticmethod
    def add_arguments(arg_parser):
        pass

    @staticmethod
    def is_applicable(project=None, log_type=None):
        return True

    def __init__(self, context):
        self.context = context

    def parse(self, target):
        context_working_dir = target.get("context.working_dir")
        if not context_working_dir:
            return target

        if self.context.working_dir != context_working_dir:
            logger.info("Working directory: '{}'".format(context_working_dir))
            self.context.working_dir = context_working_dir

        del target["context.working_dir"]
        return target


__all__ = ["ContextWorkingDirWorkaround"]
