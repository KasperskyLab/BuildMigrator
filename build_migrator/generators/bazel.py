import argparse
import logging
import os
from pprint import pformat
import re
import shutil
import sys
import traceback
from build_migrator.generators._bazel.rule_cc import RuleCc
from build_migrator.generators._bazel.skylib import CopyFile
from build_migrator.modules import EntryPoint, Generator
from build_migrator.parsers.build_log_parser import (
    BuildLogParserContext as ParserContext,
)
from build_migrator.common.os_ext import get_host_system_name, get_platform
from build_migrator.helpers import (
    get_minified_target,
    get_target_outputs,
    ModuleTypes,
)


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)


class BazelContext(EntryPoint, Generator):
    build_dir_placeholder = ParserContext.build_dir_placeholder
    source_dir_placeholder = ParserContext.source_dir_placeholder
    link_lib_prefix = "@link_lib_prefix@"

    @classmethod
    def add_arguments(cls, arg_parser):
        try:
            arg_parser.add_argument(
                "--platform",
                choices=["linux", "windows", "darwin"],
                help="Platform under which the build log was obtained. "
                "Mac and Linux builds can be parsed on any platform. "
                "Windows build logs can be parsed only on Windows. "
                "Default: current platform.",
            )
        except argparse.ArgumentError:
            # Already added somewhere else
            # TODO: make a better solution for cases when multiple extensions require the same argument
            pass
        arg_parser.add_argument(
            "--prebuilt_subdir",
            metavar="DIRNAME",
            help="Directory for files that were generated during original build, "
            "but have no associated command line. Files like these may appear "
            "if there's no parser for command line that generates them, or "
            "command line is not listed in build logs. Default: prebuilt.",
        )
        arg_parser.add_argument(
            "--source_subdir",
            metavar="DIRNAME",
            help="Subdirectory for captured source files. Default: source.",
        )

    def __init__(
        self,
        build_migrator,
        out_dir,
        prebuilt_subdir=None,
        source_subdir=None,
        build_filename=None,
        platform=None,
    ):
        if prebuilt_subdir is None:
            prebuilt_subdir = "prebuilt"
        self.prebuilt_subdir = prebuilt_subdir.replace("\\", "/")
        if source_subdir is None:
            source_subdir = "source"
        self.source_subdir = source_subdir.replace("\\", "/")
        if build_filename is None:
            build_filename = "BUILD.bazel"
        self.build_filename = build_filename
        self.out_dir = out_dir
        if platform is None:
            platform = get_host_system_name()
        self.platform_name = platform
        self.platform = get_platform(platform)
        self.for_windows = platform.startswith("win")

        self.label_placeholders = [
            (self.link_lib_prefix, "-DEFAULTLIB:")
            if self.for_windows
            else (self.link_lib_prefix, "-l"),
            (self.build_dir_placeholder, self.prebuilt_subdir),
            (self.source_dir_placeholder, self.source_subdir),
        ]

        self.location_placeholders = [
            (self.link_lib_prefix, "-DEFAULTLIB:")
            if self.for_windows
            else (self.link_lib_prefix, "-l"),
            (
                re.compile(r'{}(/[^"\\]+)'.format(self.build_dir_placeholder)),
                r"$(location {}\1)".format(self.prebuilt_subdir),
            ),
            (
                re.compile(r'{}(/[^"\\]+)'.format(self.source_dir_placeholder)),
                r"$(location {}\1)".format(self.source_subdir),
            ),
        ]

        self._builtin_generators = {
            "file": self._generate_file,
            "directory": self._generate_directory,
            "module_copy": self._generate_module_copy,
        }

        self.apply_map_file_workaround = True
        self.workspace_template = os.path.join(SCRIPT_DIR, "_bazel/WORKSPACE")

    def format_target(self, format_, *args, **kwargs):
        s = format_.format(*args, **kwargs)
        for placeholder, replacement in self.label_placeholders:
            s = s.replace(placeholder, replacement)

        return s

    def format_location(self, format_, *args, **kwargs):
        s = format_.format(*args, **kwargs)
        for placeholder, replacement in self.location_placeholders:
            if isinstance(placeholder, str):
                s = s.replace(placeholder, replacement)
            else:
                s = placeholder.sub(replacement, s)
        return s

    def write_line(self, format_, *args, **kwargs):
        formatter = None
        if "formatter" in kwargs:
            formatter = kwargs.pop("formatter")
        if formatter is None:
            formatter = self.format_target
        self.file.write(formatter(format_, *args, **kwargs))
        self.file.write("\n")

    def quote(self, s):
        return s.replace("\\", "\\\\").replace('"', '\\"')

    def write_list_or_string(self, fmt, value, quote=True, formatter=None):
        if isinstance(value, str):
            if quote:
                value = self.quote(value)
            self.write_line(fmt, value, formatter=formatter)
        else:
            for s in value:
                if quote:
                    s = self.quote(s)
                self.write_line(fmt, s, formatter=formatter)

    def generate(self, targets, generators):
        targets = self.preprocess_targets(targets)

        self._create_target_index(targets)

        shutil.copy(self.workspace_template, self.out_dir)

        # shutil.copytree(
        #     os.path.join(SCRIPT_DIR, "_bazel/bazel_extensions"),
        #     os.path.join(self.out_dir, "bazel_extensions"),
        # )

        with open(os.path.join(self.out_dir, self.build_filename), "w") as f:
            self.file = f
            self.write_header(targets)
            for target in targets:
                logger.debug(" > Generate Bazel for target:")
                logger.debug(pformat(get_minified_target(target)))
                success = False
                builtin_generator = self._builtin_generators.get(target["type"])
                if builtin_generator:
                    builtin_generator(target)
                    success = True
                else:
                    for generator in generators:
                        logger.debug(type(generator).__name__)
                        try:
                            if generator.generate(target):
                                success = True
                                break
                        except Exception:
                            logger.error(traceback.format_exc())
                if not success:
                    raise ValueError("Generator not found")
            self.file = None

    def write_header(self, targets):
        # Write something at the beginning of build script
        pass

    def preprocess_targets(self, targets):
        # Bazel doesn't support setting output file name, files are names
        # the same as their target. Original filenames can be reproduced
        # if target names match sonames.

        name_set = set()
        for target in targets:
            if target["type"] == "module":
                name_set.add(target["name"])

        for target in targets:
            if target["type"] == "module":
                target_name = target["name"]
                if target["module_type"] == ModuleTypes.static_lib:
                    target_name = target["name"][
                        0 : len(target["name"]) - len(".static")
                    ]
                if target["name"] != target_name:
                    if target_name in name_set:
                        logger.error(
                            "Unable to change target {} name to it's output filename, name {} is already taken.".format(
                                target["name"], target_name
                            )
                        )
                    else:
                        target["name"] = target_name

        return targets

    def _create_target_index(self, targets):
        self.target_index = {}
        for target in targets:
            for output in get_target_outputs(target):
                self.target_index[output] = target

    def _target_is_in_source_dir(self, target):
        return target["output"].startswith(self.source_dir_placeholder)

    def _target_is_in_build_dir(self, target):
        return target["output"].startswith(self.build_dir_placeholder)

    def _generate_file(self, target):
        subdir = None
        if self._target_is_in_build_dir(target):
            location = target["output"][len(self.build_dir_placeholder) + 1 :]
            subdir = self.prebuilt_subdir
        elif self._target_is_in_source_dir(target):
            location = target["output"][len(self.source_dir_placeholder) + 1 :]
            subdir = self.source_subdir
        else:
            raise ValueError("External targets not allowed")
        if self.platform.is_absolute(location):
            raise ValueError("Absolute paths not allowed")
        if subdir is not None:
            location = os.path.join(subdir, location)

        if sys.version_info >= (3, 0) and isinstance(target["content"], str):
            mode = "wt"
        else:
            mode = "wb"
        location = os.path.join(self.out_dir, location)

        if self.apply_map_file_workaround and not self.for_windows:
            _, ext = os.path.splitext(location)
            if ext == ".map":
                # For some reason, Bazel doesn't allow .map extension for version scripts,
                # but we can use another compatible extension: .lds
                location = location + ".lds"
                self.label_placeholders.insert(
                    0, (target["output"], target["output"] + ".lds")
                )
                self.location_placeholders.insert(
                    0, (target["output"], target["output"] + ".lds")
                )

        parent_dir = os.path.dirname(location)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        with open(location, mode) as f:
            f.write(target["content"])

    def _generate_directory(self, target):
        # Do nothing
        pass

    def _generate_module_copy(self, target):
        # Do nothing
        pass


__all__ = [
    "BazelContext",
    "RuleCc",
    "CopyFile",
]
