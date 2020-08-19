import logging
import os


logger = logging.getLogger(__name__)


class StraceLogProvider(object):
    NAME = "STRACE"
    HELP = (
        "Using strace, log syscalls made during build (strace output path chosen automatically)."
    )

    def __init__(self, context):
        self.context = context
        self.strace_out_idx = 1

    def call_and_return_log(self, args, **kwargs):
        strace_out_path = os.path.join(
            self.context.out_dir, "strace" + str(self.strace_out_idx) + ".log"
        )
        self.strace_out_idx += 1
        strace_prefix = [
            "strace",
            "-f",
            "-e",
            "process,chdir",
            "-s",
            "65535",
            "-o",
            strace_out_path,
        ]
        self.context.call_and_return_log(strace_prefix + args, **kwargs)
        return strace_out_path
