from copy import copy
import logging
import subprocess

from build_migrator.common.argument_parser_ex import ArgumentParserEx
import build_migrator.common.os_ext as os_ext
from build_migrator.helpers import (
    get_module_target,
    ModuleTypes,
    get_source_file_reference,
    format_flag_gnu,
)

from .base.compiler_parser import CompilerParser

logger = logging.getLogger(__name__)


class Nasm(CompilerParser):
    filename_re = os_ext.Windows.get_program_path_re("nasm")

    priority = 7

    def __init__(self, context, ignore_compile_flags=None):
        CompilerParser.__init__(
            self, context, ignore_compile_flags=ignore_compile_flags
        )

        # NASM arguments
        # https://www.nasm.us/doc/nasmdoc2.html#section-2.1
        self.parser = ArgumentParserEx()
        self.parser.set_defaults(compile_flags=[], include_dirs=[])
        # TODO: publish all meaningful flags
        self.parser.set(dest=None, raw_dest="compile_flags")
        # Define a Macro
        self.parser.add_argument("-D", raw_format=format_flag_gnu, ignore_case=True)
        # Select Debug Information Format
        self.parser.add_argument(
            "-F", raw_format=format_flag_gnu,
        )
        # Output File Format
        self.parser.add_argument("-f", required=True, raw_format=format_flag_gnu)
        # Enabling Debug Information
        self.parser.add_argument("-g", action="store_true")
        # Include File Search Directories
        self.parser.add_argument(
            "-I", action="append", dest="include_dirs", ignore_case=True, raw_dest=None
        )
        # Assemble and Generate Dependencies
        self.parser.add_argument("-MD", raw_dest=None)
        # Multipass Optimization
        self.parser.add_argument("-O")
        # Output File Name
        self.parser.add_argument("-o", dest="output", raw_dest=None)
        # Pre-Include a File
        self.parser.add_argument(
            "-P",
            "--include",
            action="append",
            default=[],
            dest="preincludes",
            raw_dest=None,
        )
        # Undefine a Macro
        self.parser.add_argument("-U", raw_format=format_flag_gnu, ignore_case=True)
        # Warnings
        self.parser.add_argument("-W", "-w")
        self.parser.add_argument("infile", dest="infile", raw_dest=None)

    def _add_implicit_dependencies(
        self,
        compiler,
        dependencies,
        compile_flags,
        include_dirs,
        preincludes,
        source,
        cwd,
    ):
        include_dir_args = ["-I" + d for d in include_dirs]
        preinclude_args = ["-P" + p for p in preincludes]
        cmd = (
            [compiler, "-E", "-M"]
            + compile_flags
            + preinclude_args
            + include_dir_args
            + [source]
        )
        p = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd
        )
        stdout, stderr = p.communicate()
        if type(stdout) is not str:
            stdout = stdout.decode("utf-8", "replace")
        if type(stderr) is not str:
            stderr = stderr.decode("utf-8", "replace")
        retcode = p.poll()
        if retcode:
            logger.error(
                "Command '{}' returned non-zero exit code {}\n{}".format(
                    " ".join(cmd), retcode, stderr
                )
            )

        implicit_dependencies = []
        for line in stdout.splitlines():
            files = line.rstrip("\\").lstrip().split(" ")
            if len(files) > 1 and files[1] == ":":
                files = [files[0] + files[1]] + files[2:]
            for f in files:
                if not f or f.endswith(":") or f == source:
                    continue
                implicit_dependencies.append(f)
        return [
            self.context.get_file_arg(self.context.normalize_path(dep), dependencies)
            for dep in implicit_dependencies
        ]

    def parse(self, target):
        tokens = target.get("tokens") or []
        if not tokens:
            return target

        if not self.filename_re.match(tokens[0]):
            return target

        compiler = tokens.pop(0)

        namespace = self.parser.parse_args(tokens)

        dependencies = []

        infile = namespace.infile
        if not infile:
            assert len(namespace.preincludes) > 0
            infile = namespace.preincludes.pop()

        self.process_namespace(namespace)

        source_compile_flags = copy(namespace.compile_flags)
        for preinclude in namespace.preincludes:
            path = self.context.get_file_arg(
                self.context.normalize_path(preinclude), dependencies
            )
            source_compile_flags.append("-P" + path)
        source = get_source_file_reference(
            self.context.get_file_arg(
                self.context.normalize_path(infile), dependencies
            ),
            "NASM",
            compile_flags=source_compile_flags,
        )
        self.process_namespace(source)

        output = self.context.get_output(self.context.normalize_path(namespace.output))

        include_dirs = []
        for dir in namespace.include_dirs:
            # include dir may not exist, it's normal
            dir = self.context.normalize_path(dir)
            arg = self.context.get_dir_arg(dir, dependencies)
            if arg:
                include_dirs.append(arg)

        self._add_implicit_dependencies(
            compiler,
            dependencies,
            namespace.compile_flags,
            namespace.include_dirs,
            namespace.preincludes,
            infile,
            self.context.working_dir,
        )

        return get_module_target(
            ModuleTypes.object_lib,
            None,
            output,
            dependencies=dependencies,
            sources=[source],
            include_dirs=include_dirs,
        )


__all__ = ["Nasm"]
