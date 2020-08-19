from copy import copy
import logging
import subprocess
from build_migrator.helpers import (
    get_module_target,
    ModuleTypes,
    get_source_file_reference,
)
from build_migrator.common.argument_parser_ex import ArgumentParserEx
import build_migrator.common.os_ext as os_ext
from .base.compiler_parser import CompilerParser


logger = logging.getLogger(__name__)


class ReplacePrefixArg(object):
    def __init__(self, replace_prefix_arg=None):
        # prefix_arg: -D, -I, etc
        assert len(replace_prefix_arg) == 2, replace_prefix_arg
        self._replace_prefix_arg = replace_prefix_arg

    def __call__(self, args):
        # 1. _replace_prefix_arg=-a, args=[--arch=value], result=-avalue
        # 2. _replace_prefix_arg=-a, args=[-A, value], result=-avalue
        # 3. _replace_prefix_arg=-a, args=[-Avalue], result=-avalue
        if args and self._replace_prefix_arg:
            if len(args) == 1:
                args = args[0].split("=")
            else:
                args = copy(args)
            if len(args) == 2:
                args[0] = self._replace_prefix_arg
            elif len(args) == 1:
                args[0] = self._replace_prefix_arg + args[0][2:]
            else:
                assert False, args
        return "".join(args)


# 1. [-d, A=1] => -DA=1
# 1. [-dA=1] => -DA=1
def prefix_arg_toupper(args):
    if args:
        args = copy(args)
        if len(args) == 1:
            args[0] = args[0][0:2].upper() + args[0][2:]
        else:
            args[0] = args[0].upper()
    return "".join(args)


class Yasm(CompilerParser):
    filename_re = os_ext.Windows.get_program_path_re("yasm")

    priority = 7

    def __init__(self, context, ignore_compile_flags=None):
        CompilerParser.__init__(
            self, context, ignore_compile_flags=ignore_compile_flags
        )

        # YASM arguments
        # http://www.tortall.net/projects/yasm/manual/html/yasm-options.html
        self.parser = ArgumentParserEx()
        self.parser.set_defaults(compile_flags=[], include_dirs=[])
        self.parser.set(dest=None, raw_dest="compile_flags")
        # select architecture
        self.parser.add_argument("--arch", "-a", raw_format=ReplacePrefixArg("-a"))
        # select parser
        self.parser.add_argument("--parser", "-p", raw_format=ReplacePrefixArg("-p"))
        # select preprocessor
        self.parser.add_argument("--preproc", "-r", raw_format=ReplacePrefixArg("-r"))
        # object format
        self.parser.add_argument("--oformat", "-f", raw_format=ReplacePrefixArg("-f"))
        # debugging format
        self.parser.add_argument("--dformat", "-g", raw_format=ReplacePrefixArg("-d"))
        # name of object-file output
        self.parser.add_argument("--objfile", "-o", dest="output", raw_dest=None)
        # select machine
        self.parser.add_argument("--machine", "-m", raw_format=ReplacePrefixArg("-m"))
        # treat all sized operands as if `strict' was used
        self.parser.add_argument("--force-strict", action="store_true")
        # add include path
        self.parser.add_argument(
            "-I", action="append", dest="include_dirs", ignore_case=True, raw_dest=None
        )
        # pre-include file
        self.parser.add_argument(
            "-P", action="append", dest="preinclude_files", default=[], raw_dest=None
        )
        # pre-define a macro
        self.parser.add_argument("-D", ignore_case=True, raw_format=prefix_arg_toupper)
        # undefine a macro
        self.parser.add_argument("-U", ignore_case=True, raw_format=prefix_arg_toupper)
        # disable all warnings
        self.parser.add_argument("-w", action="store_true")
        # enables/disables warning
        self.parser.add_argument("-W", prefix=True)
        # redirect error messages to file
        self.parser.add_argument("-E")
        # redirect error messages to stdout
        self.parser.add_argument("-s", action="store_true")
        # select error/warning message style (`gnu' or `vc')
        self.parser.add_argument("-X")
        # prepend argument to name of all external symbols
        self.parser.add_argument("--prefix")
        # append argument to name of all external symbols
        self.parser.add_argument("--suffix", "--postfix")
        self.parser.add_argument("file", dest="file", raw_dest=None)

    # TODO: this function is mostly the same for GCC, NASM, YASM. Make a base class.
    def _add_implicit_dependencies(
        self,
        compiler,
        dependencies,
        compile_flags,
        include_dirs,
        preinclude_files,
        source,
        cwd,
    ):
        include_dir_args = ["-I" + d for d in include_dirs]
        preinclude_args = ["-P" + p for p in preinclude_files]
        cmd = (
            [compiler, "--preproc-only", "-M"]
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
            for f in files:
                if not f or f.endswith(":") or f == source:
                    continue
                implicit_dependencies.append(f)
        return [
            self.context.get_file_arg(self.context.normalize_path(dep), dependencies)
            for dep in implicit_dependencies
        ]

    # TODO: this function is mostly the same for all compiler parsers. Make a base class.
    def parse(self, target):
        tokens = target.get("tokens") or []
        if not tokens:
            return target

        if not self.filename_re.match(tokens[0]):
            return target

        compiler = tokens.pop(0)
        compiler_nrm = self.context.platform.normalize_path(compiler)
        if compiler_nrm in self.context.path_aliases:
            compiler = self.context.path_aliases[compiler_nrm]

        namespace = self.parser.parse_args(tokens)

        dependencies = []

        output = self.context.get_output(self.context.normalize_path(namespace.output))

        self.process_namespace(namespace)

        self._add_implicit_dependencies(
            compiler,
            dependencies,
            namespace.compile_flags,
            namespace.include_dirs,
            namespace.preinclude_files,
            namespace.file,
            self.context.working_dir,
        )

        compile_flags = namespace.compile_flags
        for preinclude in namespace.preinclude_files:
            path = self.context.get_file_arg(
                self.context.normalize_path(preinclude), dependencies
            )
            compile_flags.append("-P" + path)

        source = get_source_file_reference(
            self.context.get_file_arg(
                self.context.normalize_path(namespace.file), dependencies
            ),
            "YASM",
            compile_flags=compile_flags,
        )
        self.process_namespace(source)

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
            dependencies=dependencies,
            compile_flags=[],
            sources=[source],
            include_dirs=include_dirs,
        )


__all__ = ["Yasm"]
