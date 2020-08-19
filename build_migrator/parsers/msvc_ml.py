from copy import copy
import logging
import os
import re

import build_migrator.common.os_ext as os_ext

from build_migrator.common.argument_parser_ex import ArgumentParserEx
from build_migrator.common.encoding_detection import read_lines
from build_migrator.helpers import (
    get_module_target,
    ModuleTypes,
    get_source_file_reference,
    format_flag_gnu,
)

from .base.compiler_parser import CompilerParser

logger = logging.getLogger(__name__)


# TODO: move to common
def add_included_dependencies(
    context,
    include_re,
    dependencies,
    include_dirs,
    sources,
    cwd,
    include_src_dir=True,
    include_cwd=False,
    seen_src_set=None,
    dependency_re=None,
):
    if seen_src_set is None:
        seen_src_set = set()
    for src in sources:
        src = os.path.join(cwd, src)
        if not os.path.exists(src):
            logger.error(
                "File not found, unable to enumerate #included files: %r" % src
            )
            continue
        if src in seen_src_set:
            return
        if include_cwd or include_src_dir:
            include_dirs = copy(include_dirs)
        if include_cwd:
            include_dirs.insert(0, cwd)
        if include_src_dir:
            src_dir = os.path.dirname(src)
            include_dirs.insert(0, src_dir)
        seen_src_set.add(src)
        for line in read_lines(src):
            if dependency_re:
                m = dependency_re.match(line)
                if m:
                    rel_path = m.group("path").strip()
                    if include_cwd:
                        abs_path = context.normalize_path(os.path.join(cwd, rel_path))
                        if os.path.exists(abs_path):
                            context.get_file_arg(abs_path, dependencies)
                            continue
                    if include_src_dir:
                        abs_path = context.normalize_path(
                            os.path.join(src_dir, rel_path)
                        )
                        if os.path.exists(abs_path):
                            context.get_file_arg(abs_path, dependencies)
                            continue
                    logger.warn("Unable to resolve resource: " + rel_path)
                    continue
            m = include_re.match(line)
            if m:
                rel_path = m.group("path").strip()
                include_path = None
                for dir in include_dirs:
                    include_path = os.path.join(cwd, dir, rel_path)
                    if os.path.exists(include_path) and os.path.isfile(include_path):
                        add_included_dependencies(
                            context,
                            include_re,
                            dependencies,
                            include_dirs,
                            [include_path],
                            cwd,
                            include_src_dir,
                            include_cwd,
                            seen_src_set,
                        )
                        break
                    else:
                        include_path = None
                if include_path:
                    context.get_file_arg(
                        context.normalize_path(include_path), dependencies
                    )
                else:
                    logger.warn("Unable to resolve include: " + rel_path)


class MsvcMl(CompilerParser):
    filename_re = os_ext.Windows.get_program_path_re("ml", "ml64")

    priority = 7

    def __init__(self, context, ignore_compile_flags=None):
        CompilerParser.__init__(
            self, context, ignore_compile_flags=ignore_compile_flags
        )

        # Visual Studio ml.exe arguments
        # https://docs.microsoft.com/en-us/cpp/assembler/masm/ml-and-ml64-command-line-reference?view=vs-2017
        self.parser = ArgumentParserEx(prefix_chars="-/")
        self.parser.set_defaults(
            compile_flags=[], link_flags=[], include_dirs=[], infiles=[]
        )
        # TODO: publish all meaningful flags
        self.parser.set(dest=None, raw_dest="compile_flags")
        self.parser.add_argument(
            "/c", action="store_true", raw_dest=None, dest="compile_only"
        )
        # Generates common object file format (COFF) type of object module
        self.parser.add_argument("/coff", action="store_true")
        # Preserves case of all user identifiers
        self.parser.add_argument("/Cp", action="store_true")
        # Maps all identifiers to upper case
        self.parser.add_argument("/Cu", action="store_true")
        # Preserves case in public and extern symbols
        self.parser.add_argument("/Cx", action="store_true")
        self.parser.add_argument("/D", raw_format=format_flag_gnu)
        self.parser.add_argument(
            "/errorreport", prefix=True, nargs="?", ignore_case=True
        )
        self.parser.add_argument("/Fo", prefix=True, raw_dest=None, dest="output")
        # stack size
        self.parser.add_argument("/F", prefix=True)
        # Generates emulator fix-ups for floating-point arithmetic
        self.parser.add_argument("/FPi", action="store_true")
        # Specifies use of C-style function calling and naming conventions
        self.parser.add_argument("/Gd", action="store_true")
        # Specifies use of __stdcall function calling and naming conventions
        self.parser.add_argument("/GZ", action="store_true")
        self.parser.add_argument(
            "/I", action="append", raw_dest=None, dest="include_dirs"
        )
        self.parser.add_argument("/nologo", action="store_true", ignore_case=True)
        # Generates object module file format (OMF) type of object module
        self.parser.add_argument("/omf", action="store_true")
        self.parser.add_argument(
            "/Ta", prefix=True, action="append", raw_dest=None, dest="infiles"
        )
        self.parser.add_argument("/safeseh", action="store_true", ignore_case=True)
        # Warning flags
        self.parser.add_argument(flags=["/W", "/WX"], action="store_true")
        self.parser.add_argument("/W", choices="0123")
        # line-number information in object file
        self.parser.add_argument("/Zd", action="store_true")
        # Generate CodeView information in object file
        self.parser.add_argument("/Zi", action="store_true")
        # Makes all symbols public
        self.parser.add_argument("/Zf", action="store_true")
        # Packs structures on the specified byte boundary
        self.parser.add_argument("/Zp", prefix=True, type=int)
        self.parser.add_argument("infiles", nargs="*", dest="infiles", raw_dest=None)

    include_re = re.compile(r"(?:\b|%)include\s+(?P<path>[^\s\n][^\n]*)", re.IGNORECASE)

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
        assert namespace.compile_only

        dependencies = []

        self.process_namespace(namespace)

        # ml.exe doesn't support /showIncludes or anything similar
        add_included_dependencies(
            self.context,
            self.include_re,
            dependencies,
            namespace.include_dirs,
            namespace.infiles,
            self.context.working_dir,
        )

        include_dirs = []
        for dir in namespace.include_dirs:
            dir = self.context.normalize_path(dir)
            arg = self.context.get_dir_arg(dir, dependencies)
            if arg:
                include_dirs.append(arg)

        sources = []
        for infile in namespace.infiles:
            sources.append(
                get_source_file_reference(
                    self.context.get_file_arg(
                        self.context.normalize_path(infile), dependencies
                    ),
                    "MASM",
                )
            )

        output = self.context.get_output(self.context.normalize_path(namespace.output))

        return get_module_target(
            ModuleTypes.object_lib,
            None,
            output,
            compile_flags=namespace.compile_flags,
            include_dirs=include_dirs,
            dependencies=dependencies,
            sources=sources,
        )


__all__ = ["MsvcMl"]
