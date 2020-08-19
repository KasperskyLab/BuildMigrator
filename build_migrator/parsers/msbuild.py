import logging
import os
import re
from build_migrator.modules import Parser
from build_migrator.parsers._common.command_tokenizer import CommandTokenizer
from build_migrator.parsers._common.context_working_dir_workaround import (
    ContextWorkingDirWorkaround,
)
from build_migrator.parsers._common.replace_line import ReplaceLine
from build_migrator.parsers._common.response_file import ResponseFile
from build_migrator.parsers._common.inline_file_content import InlineFileContent
import build_migrator.common.os_ext as os_ext


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)


class MSBuildLog(Parser):
    unquoted_executable_re = re.compile(
        r'^([a-z]:(?:[/\\][^/\\<>:"|?*]+)+\.exe) ', re.IGNORECASE
    )
    node_re = re.compile(r"^(?P<node>\d+)>")
    top_project_re = re.compile(
        r'^Project "(?P<project>[^"]+\.[A-Za-z_0-9]+)" on node 1'
    )
    project_re = re.compile(
        r'^Project "[^"]+\.[A-Za-z_0-9]+" \(\d+\) is building "(?P<project>[^"]+\.[A-Za-z_0-9]+)" \((?P<node>\d+)\)'
    )

    priority = 0

    @staticmethod
    def add_arguments(arg_parser):
        pass

    @staticmethod
    def is_applicable(project=None, log_type=None):
        return log_type == "msbuild"

    def __init__(self, context):
        self.context = context
        self._reset()

    def _reset(self):
        self.nodes = None
        self.deferred_target = None
        self.expect_node_markers = True

    def _change_current_node(self, node):
        assert node in self.nodes, "Unknown node: " + str(node)
        dir = self.nodes[node]
        if self.context.working_dir != dir:
            logger.info("Working directory: '{}'".format(dir))
            self.context.working_dir = dir

    def _add_node(self, node, dir):
        assert node not in self.nodes, "Duplicate node: " + str(node)
        self.nodes[node] = dir

    def _get_project_dir(self, path):
        return os_ext.normalize_path(self.context.normalize_path(os.path.dirname(path)))

    def parse(self, target):
        if self.nodes is None:
            self.nodes = {1: self.context.working_dir}

        line = target.get("line") or ""
        at_eof = bool(target.get("eof"))
        targets = []

        if line.startswith("Building the projects in this solution one at a time"):
            self.expect_node_markers = False

        if self.expect_node_markers:
            match = self.node_re.match(line)
            if match:
                # Handle 'num>' prefix
                node = int(match.group("node"))
                self._change_current_node(node)
                line = self.node_re.sub("", line)
                if self.deferred_target:
                    targets.append(self.deferred_target)
                self.deferred_target = None

        if line in ["Lib:", "Link:"]:
            # Lib and Link separate their arguments with newlines
            line = ""
            self.deferred_target = {}
        else:
            # stop deferred target processing at lines looking like these:
            # 'lib.vcxproj -> build\out_static.lib' (for lib.exe)
            # 'Creating library ' (for link.exe)
            # 'FinalizeBuildStatus:' (for both)
            if (
                line.find(" -> ") != -1
                or line.endswith(":")
                or line.startswith("Creating library ")
            ):
                line = ""
                if self.deferred_target:
                    targets.append(self.deferred_target)
                self.deferred_target = None

        match = self.top_project_re.search(line)
        if match:
            # Set top project working directory
            dir = self._get_project_dir(match.group("project"))
            self.nodes[1] = dir
            self._change_current_node(1)
            line = ""

        match = self.project_re.search(line)
        if match:
            # Set subproject working directory
            node = int(match.group("node"))
            dir = self._get_project_dir(match.group("project"))
            self._add_node(node, dir)
            line = ""

        # Put executable paths in quotes, or it may parse incorrectly if it contains spaces
        target["line"] = self.unquoted_executable_re.sub(r'"\1" ', line)
        target["working_dir"] = self.context.working_dir
        # Save original working directory value without substutions (@build_dir@ etc).
        # This is a hack for situations when MSBuildLog.parse()
        # returns multiple targets with different 'working_dir' keys.
        # Other parsers then start to resolve source etc paths for these targets
        # relative to self.context.working_dir property, but its value may not
        # match target['working_dir'], which will result in incorrect path resolution.
        # Two solutions exist:
        # 1. TODO: Get rid of context's state , put it entirely into target
        # 2. Current workaround: add a parser (ContextWorkingDirWorkaround)
        #    that modifies context.working_dir before passing down each
        #    target that was returned by MSBuildLog.parse to other parsers.
        target["context.working_dir"] = self.context.working_dir

        if self.deferred_target is not None:
            if "context.working_dir" not in self.deferred_target:
                self.deferred_target = target
            else:
                if not self.deferred_target["line"]:
                    self.deferred_target["line"] = target["line"]
                else:
                    self.deferred_target["line"] += " " + target["line"]
            if at_eof:
                targets.append(self.deferred_target)
        else:
            targets.append(target)

        if at_eof:
            self._reset()

        return targets


__all__ = [
    "MSBuildLog",
    "CommandTokenizer",
    "ContextWorkingDirWorkaround",
    "ReplaceLine",
    "ResponseFile",
    "InlineFileContent",
]
