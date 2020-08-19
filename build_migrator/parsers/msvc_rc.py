from copy import copy
import re

import build_migrator.common.os_ext as os_ext

from build_migrator.common.argument_parser_ex import ArgumentParserEx
from build_migrator.helpers import (
    get_module_target,
    ModuleTypes,
    get_source_file_reference,
)
from build_migrator.parsers.msvc_ml import add_included_dependencies

from .base.compiler_parser import CompilerParser


# TODO: move to common, merge wuth yasm.ReplacePrefixArg
class ReplacePrefixArg(object):
    def __init__(self, replace_prefix_arg=None):
        self._replace_prefix_arg = replace_prefix_arg

    def __call__(self, args):
        if args and self._replace_prefix_arg:
            args = copy(args)
            if len(args) == 2:
                args[0] = self._replace_prefix_arg
            elif len(args) == 1:
                args[0] = (
                    self._replace_prefix_arg + args[0][len(self._replace_prefix_arg):]
                )
            else:
                assert False, args
        return "".join(args)


class MsvcRc(CompilerParser):
    filename_re = os_ext.Windows.get_program_path_re("rc")

    priority = 7

    def __init__(self, context, ignore_compile_flags=None):
        CompilerParser.__init__(
            self, context, ignore_compile_flags=ignore_compile_flags
        )

        # Visual Studio rc.exe arguments
        # https://docs.microsoft.com/en-us/windows/desktop/menurc/using-rc-the-rc-command-line-
        self.parser = ArgumentParserEx(prefix_chars="-/")
        self.parser.set_defaults(compile_flags=[], link_flags=[], include_dirs=[])
        # TODO: publish all meaningful flags
        self.parser.set(ignore_case=True, dest=None, raw_dest="compile_flags")
        self.parser.add_argument("/d", raw_format=ReplacePrefixArg("-D"))
        self.parser.add_argument("/u", raw_format=ReplacePrefixArg("-U"))
        self.parser.add_argument("/ln", raw_format=ReplacePrefixArg("/ln"))
        self.parser.add_argument("/l", raw_format=ReplacePrefixArg("/l"))
        self.parser.add_argument("/gn", raw_format=ReplacePrefixArg("/gn"))
        self.parser.add_argument("/g", raw_format=ReplacePrefixArg("/g"))
        self.parser.add_argument(
            "/i", action="append", dest="include_dirs", raw_dest=None
        )
        self.parser.add_argument("/nologo", action="store_true")
        self.parser.add_argument(
            "/w", action="store_true", raw_format=ReplacePrefixArg("/w")
        )
        self.parser.add_argument("/fo", prefix=True, dest="output", raw_dest=None)
        self.parser.add_argument("infiles", dest="infiles", nargs="*", raw_dest=None)

    include_re = re.compile(r'\s*#\s*include\s+["<](?P<path>[^\s][^<>"]*)[>"]')
    dependency_re = re.compile(
        r'\s*[_A-Za-z0-9]+\s+(?:BITMAP|CURSOR|FONT|HTML|ICON)\s+(?:DISCARDABLE\s+)?["<](?P<path>[^\s][^<>"]*)[>"]'
    )

    def parse(self, target):
        tokens = target.get("tokens") or []
        if not tokens:
            return target

        if not self.filename_re.match(tokens[0]):
            return target

        if len(tokens) < 2 or tokens[1] == ":":
            # skip warning message
            return target

        tokens.pop(0)

        namespace = self.parser.parse_args(tokens)

        dependencies = []

        self.process_namespace(namespace)

        # rc.exe doesn't support /showIncludes or anything similar
        add_included_dependencies(
            self.context,
            self.include_re,
            dependencies,
            namespace.include_dirs,
            namespace.infiles,
            self.context.working_dir,
            include_cwd=True,
            dependency_re=self.dependency_re,
        )

        sources = []
        for infile in namespace.infiles:
            sources.append(
                get_source_file_reference(
                    self.context.get_file_arg(
                        self.context.normalize_path(infile), dependencies
                    ),
                    "RC",
                )
            )

        output = self.context.get_output(self.context.normalize_path(namespace.output))

        include_dirs = []
        for dir in namespace.include_dirs:
            # include dir may not exist, it's normal
            dir = self.context.normalize_path(dir)
            arg = self.context.get_dir_arg(dir, dependencies)
            if arg:
                include_dirs.append(arg)

        return get_module_target(
            ModuleTypes.object_lib,
            None,
            output,
            include_dirs=include_dirs,
            compile_flags=namespace.compile_flags,
            dependencies=dependencies,
            sources=sources,
        )


__all__ = ["MsvcRc"]
