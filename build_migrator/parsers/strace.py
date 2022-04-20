from copy import deepcopy
import logging
import os
from pprint import pformat
import re
from build_migrator.modules import Parser
from build_migrator.parsers._common.context_working_dir_workaround import (
    ContextWorkingDirWorkaround,
)
from build_migrator.parsers._common.response_file import ResponseFile
from build_migrator.parsers._common.inline_file_content import InlineFileContent


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)


# Provides strace parser, log should be collected using strace parameter -o <filename>
# See https://linux.die.net/man/1/strace, https://strace.io/
# TODO: ignore syscalls that we don't support
# TODO: improve regexps, then we may remove strace_tokenizer.py
class StraceLog(Parser):
    # some commands are split over two lines in log, so we used to concatenate it
    unfinished_regex = re.compile(r"(\d+)\s+(\w+)(.*)\<unfinished ...\>$")
    resumed_regex = re.compile(r"(\d+)\s+\<... (\w+) resumed\>(.*)")
    complete_regex = re.compile(r"(\d+)\s+(\w+)(.*)")
    process_exit_regex = re.compile(
        r"^(\d+)\s+\+\+\+\s+exited\s+with\s+(\d+)\s+\+\+\+$"
    )

    priority = 0

    @staticmethod
    def add_arguments(arg_parser):
        pass

    @staticmethod
    def is_applicable(log_type=None):
        return log_type == "strace"

    def __init__(self, context):
        self.context = context
        # We should postpone target processing because some log entries may be incomplete and order of target is important (because of chdir)
        self.postponed_target_cache = list()

    # All needed log entries has following format:
    # PID SYSCALL...
    # We parse first two arguments and rest of line stored as raw argument
    def parse(self, target):
        line = None
        if "line" in target:
            line = target["line"]
            del target["line"]

        result = []

        if line:
            unfinished_entry = self.unfinished_regex.split(line)
            if len(unfinished_entry) > 1:
                result += self.parse_unfinished_entry(
                    deepcopy(target), *unfinished_entry[1:4]
                )
                line = ""

            resumed_entry = self.resumed_regex.split(line)
            if len(resumed_entry) > 1:
                result += self.parse_resumed_entry(
                    deepcopy(target), *resumed_entry[1:4]
                )
                line = ""

            complete_entry = self.complete_regex.split(line)
            if len(complete_entry) > 1:
                result += self.parse_complete_entry(
                    deepcopy(target), *complete_entry[1:4]
                )
                line = ""

            process_exit_entry = self.process_exit_regex.split(line)
            if len(process_exit_entry) > 1:
                result += self.parse_process_exit_entry(
                    deepcopy(target), *process_exit_entry[1:3]
                )
                line = ""

        at_eof = bool(target.get("eof"))
        if at_eof:
            result += self.postponed_target_cache
            result.append(target)  # append EOF target
            self.postponed_target_cache = []

        return result

    def parse_unfinished_entry(self, target, pid, syscall, raw_arguments):
        # TODO: filter out unfinished `wait4` syscall since it can postpone all targets processing

        target["strace.complete"] = False
        target["strace.pid"] = pid
        target["strace.syscall"] = syscall
        target["strace.raw_arguments"] = raw_arguments

        self.postponed_target_cache.append(target)
        # postpone target processing
        return []

    def parse_resumed_entry(self, target, pid, syscall, raw_arguments):
        for postponed_target in self.postponed_target_cache:
            if (
                (postponed_target["strace.syscall"] == syscall)
                and (postponed_target["strace.pid"] == pid)
                and (not postponed_target["strace.complete"])
            ):
                postponed_target["strace.raw_arguments"] += raw_arguments
                postponed_target["strace.complete"] = True
                break

        ready_to_publish_end_idx = -1
        for idx, postponed_target in enumerate(self.postponed_target_cache):
            if postponed_target["strace.complete"]:
                ready_to_publish_end_idx = idx
            else:
                break

        postponed_targets = self.postponed_target_cache[: ready_to_publish_end_idx + 1]
        self.postponed_target_cache = self.postponed_target_cache[
            ready_to_publish_end_idx + 1:
        ]
        return postponed_targets

    def parse_complete_entry(self, target, pid, syscall, raw_arguments):
        target["strace.complete"] = True
        target["strace.pid"] = pid
        target["strace.syscall"] = syscall
        target["strace.raw_arguments"] = raw_arguments

        if len(self.postponed_target_cache) > 0:
            self.postponed_target_cache.append(target)
            return []

        return [target]

    def parse_process_exit_entry(self, target, pid, exit_code):
        target["strace.pid"] = pid
        target["strace.raw_arguments"] = exit_code
        target["strace.syscall"] = "exit"
        target["strace.complete"] = True

        if len(self.postponed_target_cache) > 0:
            self.postponed_target_cache.append(target)
            return []

        return [target]


# Provides tokens from strace pid, syscall and raw arguments
class StraceTokenizer(Parser):
    execve_regex = re.compile(r'\(\s*("[^"]+",)\s+\[(.*)\],\s+[^,]*s*\)\s*=\s*(-?\d+)')
    clone_regex = re.compile(r"\(.*\)\s*=\s*(-?\d+)")
    vfork_regex = re.compile(r"\(\s*\)\s*=\s*(-?\d+)")
    # parse only success chdir calls (skip parsing nonexistent entries)
    chdir_regex = re.compile(r'\(\s*"(.*)"\s*\)\s*=\s*0$')

    priority = 1

    @staticmethod
    def add_arguments(arg_parser):
        pass

    @staticmethod
    def is_applicable(log_type=None):
        return log_type == "strace"

    def __init__(self, context):
        self.context = context
        self.working_dir_cache = {}  # pid => working_dir
        self.initial_working_dir = self.context.working_dir

    def parse(self, target):
        if target.get("strace.complete") is None:
            # skip non-strace or already processed targets
            return target

        assert "strace.complete" in target
        if not target["strace.complete"]:
            # incomplete target, we've probably reached EOF
            return []

        assert "strace.pid" in target
        assert "strace.raw_arguments" in target
        assert target["strace.syscall"]

        pid = target["strace.pid"]
        if target["strace.syscall"] == "exit":
            self.working_dir_cache.pop(pid, None)
            return []

        if pid not in self.working_dir_cache:
            self.working_dir_cache[pid] = self.initial_working_dir

        parsers = {
            "execve": self.parse_execve_syscall,
            "clone": self.parse_clone_syscall,
            "vfork": self.parse_vfork_syscall,
            "chdir": self.parse_chdir_syscall,
        }

        return self.finalize_strace_targets(
            parsers.get(target["strace.syscall"], lambda x: [])(target)
        )

    def parse_execve_syscall(self, target):
        execve_entry = self.execve_regex.split(target["strace.raw_arguments"])

        logger.info("execve_entry: " + pformat(execve_entry))
        if execve_entry[3] != "0":
            logger.debug("skipping execve with non-zero code")
            return []

        target["context.working_dir"] = (
            self.working_dir_cache[target["strace.pid"]] + "/"
        )
        target["tokens"] = list(eval(execve_entry[2]))

        logger.info("execve target: " + pformat(target))

        return [target]

    def parse_clone_syscall(self, target):
        clone_entry = self.clone_regex.split(target["strace.raw_arguments"])
        self.working_dir_cache[clone_entry[1]] = self.working_dir_cache[
            target["strace.pid"]
        ]

        return []

    def parse_vfork_syscall(self, target):
        vfork_entry = self.vfork_regex.split(target["strace.raw_arguments"])
        self.working_dir_cache[vfork_entry[1]] = self.working_dir_cache[
            target["strace.pid"]
        ]

        return []

    def parse_chdir_syscall(self, target):
        chdir_entry = self.chdir_regex.split(target["strace.raw_arguments"])
        if len(chdir_entry) > 1:
            path = chdir_entry[1].strip('",')
            working_dir = self.working_dir_cache[target["strace.pid"]]
            self.working_dir_cache[
                target["strace.pid"]
            ] = self.context.normalize_path(os.path.join(working_dir, path), ignore_working_dir=True)

        return []

    def finalize_strace_targets(self, targets):
        for target in targets:
            # disable duplicate processing
            del target["strace.complete"]
            del target["strace.pid"]
            del target["strace.raw_arguments"]
            del target["strace.syscall"]
        return targets


class ReplaceStrace(Parser):
    priority = 0.5

    @staticmethod
    def add_arguments(arg_parser):
        arg_parser.add_argument(
            "--replace_strace",
            metavar=("REGEX", "REPL"),
            nargs=2,
            action="append",
            dest="replace_strace",
            help="Replaces occurences of regex in syscall arguments in "
            "build log. Applicable only for --log_type strace.",
        )

    def __init__(self, context, replace_strace=None):
        self.replacements = []
        for pattern, repl in replace_strace or []:
            self.replacements.append((re.compile(pattern), repl))
        self.context = context

    @staticmethod
    def is_applicable(log_type=None):
        return log_type == "strace"

    def _replace(self, raw_arguments):
        for r, repl in self.replacements:
            raw_arguments = r.sub(repl, raw_arguments)
        return raw_arguments

    def parse(self, target):
        if "strace.raw_arguments" in target:
            raw_arguments = self._replace(target["strace.raw_arguments"])
            if raw_arguments != target["strace.raw_arguments"]:
                target = deepcopy(target)
                target["strace.raw_arguments"] = raw_arguments
                return target

        return target


__all__ = [
    "StraceLog",
    "ReplaceStrace",
    "StraceTokenizer",
    "ContextWorkingDirWorkaround",
    "ResponseFile",
    "InlineFileContent",
]
