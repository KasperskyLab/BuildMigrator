import logging


logger = logging.getLogger(__name__)


class ConsoleLogProvider(object):
    NAME = "CONSOLE"
    HELP = "Pipe console output to file (path chosen automatically)"

    def __init__(self, context):
        self.context = context

    def call_and_return_log(self, args, **kwargs):
        return self.context.call_and_return_log(args, **kwargs)
