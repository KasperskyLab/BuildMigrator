from copy import deepcopy
from itertools import chain
import logging
import os
import re
import subprocess
from build_migrator.common.algorithm import flatten_list
from build_migrator.helpers import (
    get_module_target,
    ModuleTypes,
    get_source_file_reference,
    filter_flags,
    format_flag_gnu,
)
from build_migrator.common.os_ext import get_host_system_name
from build_migrator.common.argument_parser_ex import ArgumentParserEx
from .base.compiler_parser import CompilerParser
from .base.linker_parser import LinkerParser


logger = logging.getLogger(__name__)


class Clang_Gcc(CompilerParser, LinkerParser):
    asm_exts = [".s", ".S"]
    c_exts = [".c", ".m"]
    cpp_exts = [".cc", ".cpp", ".cxx", ".mm"]
    source_exts = asm_exts + c_exts + cpp_exts

    class Mode:
        link = "link"
        assemble = "assemble"  # don't link
        compile = "compile"  # don't assemble & link
        preprocess = "preprocess"  # don't compile, assemble & link

    class WholeArchive:
        enable = "--whole-archive"
        disable = "--no-whole-archive"

    class LinkType:
        static = "-Bstatic"
        dynamic = "-Bdynamic"

    priority = 7

    @staticmethod
    def add_arguments(arg_parser):
        CompilerParser.add_arguments(arg_parser)
        LinkerParser.add_arguments(arg_parser)

    def __init__(
        self,
        context,
        ignore_link_flags=None,
        ignore_compile_flags=None,
    ):
        CompilerParser.__init__(
            self, context, ignore_compile_flags=ignore_compile_flags
        )
        LinkerParser.__init__(self, context, ignore_link_flags=ignore_link_flags)

        self.platform_name = context.platform_name
        self.platform = context.platform
        self.program_re = self.platform.get_program_path_re(
            "cc", "c++", "clang", "clang++", "gcc", "g++"
        )

        # Clang/GCC arguments
        # See https://linux.die.net/man/1/gcc
        # https://gcc.gnu.org/onlinedocs/gcc/Option-Summary.html
        # https://gcc.gnu.org/onlinedocs/gcc/Invoking-GCC.html
        # https://clang.llvm.org/docs/ClangCommandLineReference.html
        self.parser = ArgumentParserEx(prog="gcc")
        self.parser.set_defaults(
            mode=self.Mode.link,
            lib_dirs=[],
            libs=[],
            include_dirs=[],
            link_flags=[],
            compile_flags=[],
        )

        # control flags
        self.parser.set(dest=None)
        self.parser.add_argument(
            "-E", action="store_const", const=self.Mode.preprocess, dest="mode"
        )
        self.parser.add_argument("-MD", action="store_true")
        self.parser.add_argument("-MF")
        self.parser.add_argument("-MMD", action="store_true")
        self.parser.add_argument("-MP", action="store_true")
        self.parser.add_argument("-MT")
        self.parser.add_argument(
            "-S", action="store_const", const=self.Mode.compile, dest="mode"
        )
        self.parser.add_argument(
            "-c", action="store_const", const=self.Mode.assemble, dest="mode"
        )
        self.parser.add_argument("-o", dest="output")
        self.parser.add_argument("-pipe", action="store_true")

        # linker flags
        self.parser.set(raw_dest="link_flags")
        self.parser.add_argument("-L", action="append", dest="lib_dirs", raw_dest=None)
        self.parser.add_argument("-Q", dest="driver_arguments")
        self.parser.add_argument(prefixes=["-Wl,"])
        self.parser.add_argument("-all_load", action="store_true")
        self.parser.add_argument("-compatibility_version")
        self.parser.add_argument("-current_version")
        self.parser.add_argument("-version-info")
        self.parser.add_argument(
            "-dynamiclib",
            "-dynamic",
            action="store_true",
            raw_dest=None,
            dest="is_shared",
        )
        self.parser.add_argument("-exported_symbols_list")
        self.parser.add_argument("-framework")
        self.parser.add_argument("-rpath")
        self.parser.add_argument("-rpath-link")
        self.parser.add_argument("-headerpad_max_install_names", action="store_true")
        self.parser.add_argument("-no-undefined", action="store_true")
        self.parser.add_argument("-install_name")
        self.parser.add_argument(prefixes=["-l:", "-l"])
        self.parser.add_argument("-nolibc", action="store_true")
        self.parser.add_argument("-nostdlib++", action="store_true")
        self.parser.add_argument("-no-canonical-prefixes", action="store_true")
        self.parser.add_argument("-nostdlib", action="store_true")
        self.parser.add_argument("-single_module", action="store_true")
        self.parser.add_argument("-pie", action="store_true")
        self.parser.add_argument("-rdynamic", action="store_true")
        self.parser.add_argument(
            "-shared", action="store_true", raw_dest=None, dest="is_shared"
        )
        self.parser.add_argument("-static", action="store_true")
        self.parser.add_argument("-static-libgcc", action="store_true")
        self.parser.add_argument("-static-libstdc++", action="store_true")
        self.parser.add_argument("-stdlib")
        self.parser.add_argument(flags=["-z"])
        self.parser.add_argument(
            "static_libs", nargs="*", args_regexp=re.compile(r"^(?!-Wl).+\.a$")
        )
        if self.platform_name == "linux":
            self.parser.add_argument(
                "shared_libs",
                nargs="*",
                args_regexp=re.compile(r"^(?!-Wl).+\.so(?:\.\d+)*$"),
            )
        if self.platform_name == "darwin":
            self.parser.add_argument(
                "shared_libs", nargs="*", args_regexp=re.compile(r"^(?!-Wl).+\.dylib$"),
            )

        # compiler flags
        self.parser.set(raw_dest="compile_flags")
        self.parser.add_argument("-D", raw_format=format_flag_gnu)
        self.parser.add_argument(prefixes=["-B"])  # Aurora stuff
        self.parser.add_argument("--target", "-target")
        self.parser.add_argument("--gcc-toolchain", "-gcc-toolchain")
        self.parser.add_argument("--sysroot")
        self.parser.add_argument(
            "-I", action="append", dest="include_dirs", raw_dest=None
        )
        self.parser.add_argument(prefixes=["-O"])
        self.parser.add_argument("-Q")
        self.parser.add_argument("-U", raw_format=format_flag_gnu)
        self.parser.add_argument(prefixes=["-W"], args_regexp=re.compile("^(?!l,)"))
        self.parser.add_argument(prefixes=["-Wa,"])
        self.parser.add_argument("-arch")
        self.parser.add_argument("-w", action="store_true")
        self.parser.add_argument(prefixes=["-f"])
        self.parser.add_argument(prefixes=["-W"])
        self.parser.add_argument("-W", action="store_true")
        self.parser.add_argument("-pedantic", action="store_true")
        self.parser.add_argument(prefixes=["-std=", "--std="])
        self.parser.add_argument("-x", dest="language_mode")
        self.parser.add_argument("-isystem", action="append")

        # compiler + linker flags
        # TODO: HACK: list support in raw_dest is temporary until a better solution comes up
        self.parser.set(raw_dest=["compile_flags", "link_flags"])
        self.parser.add_argument("-g", nargs="?")
        self.parser.add_argument("-isysroot")
        self.parser.add_argument(prefixes=["-m"])
        self.parser.add_argument("-pthread", action="store_true")

        self.parser.add_argument("infiles", nargs="*", dest="infiles", raw_dest=None)

    # Split compile flag list with multiple -arch flags into multiple lists,
    # each with only one -arch.
    # This fixes clang preprocessor error: cannot use 'dependencies' output with multiple -arch options
    def _split_compile_flags_for_multiarch(self, compile_flags):
        arch_args = {
            idx: arg
            for idx, arg in enumerate(compile_flags)
            if isinstance(arg, list) and arg[0] == "-arch"
        }
        if len(arch_args) > 1:
            compile_flags = [
                arg for idx, arg in enumerate(compile_flags) if idx not in arch_args
            ]
            result = [compile_flags]
            for _ in range(0, len(arch_args) - 1):
                result.append(deepcopy(result[0]))
            compile_flags_iter = iter(result)
            for idx, arg in arch_args.items():
                next(compile_flags_iter).insert(idx, arg)
            return result
        else:
            return [compile_flags]

    def _add_implicit_dependencies(
        self,
        compiler,
        dependencies,
        compile_flags,
        include_dirs,
        sources,
        target_platform,
        cwd,
    ):
        if not sources:
            return

        include_dir_args = ["-I" + d for d in include_dirs]
        sources = [s for s in sources]

        host_system = get_host_system_name()
        if compiler.find("clang") != -1:
            if host_system == "windows" and target_platform != host_system:
                # to avoid errors like:
                # * clang++.exe: error: unsupported option '-fPIC' for target 'x86_64-pc-windows-msvc'
                if target_platform == "linux":
                    compile_flags = compile_flags + ["--target=i686-pc-linux-gnu"]
                if target_platform == "darwin":
                    compile_flags = compile_flags + ["--target=i686-apple-darwin10"]

        implicit_dependencies = []
        implicit_dependencies_set = set()
        for compile_flags in self._split_compile_flags_for_multiarch(compile_flags):
            cmd = (
                [compiler, "-M"]
                + flatten_list(compile_flags)
                + include_dir_args
                + sources
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
                cmd_str = " ".join(cmd)
                logger.error(
                    "Command '{}' returned non-zero exit code {}\n{}".format(
                        cmd_str, retcode, stderr
                    )
                )

            for line in stdout.splitlines():
                files = line.rstrip("\\").lstrip().split(" ")
                for f in files:
                    if not f or f.endswith(":") or f in sources:
                        continue
                    if f not in implicit_dependencies_set:
                        implicit_dependencies.append(f)
                        implicit_dependencies_set.add(f)

        return [
            self.context.get_file_arg(self.context.normalize_path(dep), dependencies)
            for dep in implicit_dependencies
        ]

    # filter libs from linker flags
    def _filter_lib_args(self, ns, dependencies):
        libs = []
        remaining_flags = []
        whole_archive = False
        static_only = False
        for arg in ns.link_flags:
            skip = False
            is_lib = False
            if not isinstance(arg, str):
                pass
            elif arg.endswith(self.WholeArchive.enable):
                whole_archive = True
                skip = True
            elif arg.endswith(self.WholeArchive.disable):
                whole_archive = False
                skip = True
            elif arg.endswith(self.LinkType.static):
                static_only = True
                skip = True
            elif arg.endswith(self.LinkType.dynamic):
                static_only = False
                skip = True
            else:
                if arg.startswith("-l"):
                    arg = arg[2:]
                    if arg[0] == ":":
                        arg = self.context.get_file_arg(arg[1:], dependencies)
                    else:
                        arg = self.context.get_lib_arg(
                            arg, dependencies, ns.lib_dirs, static_only=static_only
                        )
                    is_lib = True
                    skip = True
                elif arg.startswith("-Wl,"):
                    pass
                elif self.platform.is_static_lib(arg) or self.platform.is_shared_lib(
                    arg
                ):
                    arg = self.context.get_file_arg(arg, dependencies)
                    is_lib = True
                    skip = True

            if is_lib:
                if whole_archive:
                    libs.append({"gcc_whole_archive": True, "value": arg})
                else:
                    libs.append(arg)

            if not skip:
                remaining_flags.append(arg)

        ns.link_flags = remaining_flags
        ns.libs.extend(libs)

    _capture_next_arg = {
        "-Wl,-soname",
        "-Wl,-compatibility_version",
        "-Wl,-current_version",
        "-Wl,-z",
        "-Wl,-version-script",
        "-Wl,--version-script",
        "-Wl,-rpath-link",
        "-Wl,--rpath-link",
        "-Wl,-rpath",
        "-Wl,--rpath",
    }
    _file_arg = {
        "-exported_symbols_list": "",
        "-Wl,-version-script": "-Wl,",
        "-Wl,--version-script": "-Wl,",
    }
    _dir_arg = {
        "-Wl,-rpath-link": "-Wl,",
        "-Wl,--rpath-link": "-Wl,",
        "-rpath-link": "",
        "-Wl,-rpath": "-Wl,",
        "-Wl,--rpath": "-Wl,",
        "-rpath": "",
    }
    _args_prefixes = [s for s in chain(_file_arg.keys(), _dir_arg.keys())]

    def _process_link_flags(self, flags, dependencies):
        result = []
        it = iter(flags)
        for f in it:
            if isinstance(f, str):
                if f in self._capture_next_arg:
                    f = [f, next(it)]
                else:
                    for s in self._args_prefixes:
                        if f.startswith(s):
                            delim = f[len(s)]
                            if delim not in ('=', ','):
                                continue
                            tmp = f.split(delim)
                            if s in self._file_arg:
                                tmp[-1] = self.context.get_file_arg(
                                    tmp[-1], dependencies
                                )
                            else:
                                tmp[-1] = self.context.get_dir_arg(
                                    tmp[-1], dependencies
                                )
                            f = delim.join(tmp)
                            break

            if isinstance(f, list):
                prefix = None
                get_arg_func = None
                if f[0] in self._file_arg:
                    prefix = self._file_arg[f[0]]
                    get_arg_func = self.context.get_file_arg
                if f[0] in self._dir_arg:
                    prefix = self._dir_arg[f[0]]
                    get_arg_func = self.context.get_dir_arg
                if get_arg_func:
                    if not f[-1].startswith(prefix):
                        prefix = ""
                    else:
                        f[-1] = f[-1][len(prefix) :]
                    f[-1] = prefix + get_arg_func(f[-1], dependencies)
            result.append(f)
        return result

    def parse(self, target):
        tokens = target.get("tokens")
        if not tokens:
            return target

        # .strip('{}$') is a workaround for paths like ${LDCMD:-gcc}
        # TODO: parameter expansion parser: http://wiki.bash-hackers.org/syntax/pe
        if not self.program_re.match(tokens[0].strip("{}$")):
            return target

        gcc = tokens.pop(0)
        gcc = self.context.apply_path_aliases(self.context.normalize_path(gcc, ignore_working_dir=True))

        namespace, _ = self.parser.parse_known_args(
            tokens, unknown_dest=["compile_flags", "link_flags"]
        )
        if namespace.mode not in [self.Mode.link, self.Mode.assemble]:
            return target

        if namespace.mode != self.Mode.link:
            namespace.link_flags = []
            namespace.lib_dirs = []
            namespace.libs = []

        dependencies = []
        namespace.lib_dirs = list(
            map(
                lambda p: p[2:],
                filter_flags(
                    self.ignore_link_flags_rxs, ["-L" + d for d in namespace.lib_dirs]
                ),
            )
        )
        LinkerParser.process_namespace(self, namespace)
        self._filter_lib_args(namespace, dependencies)
        namespace.link_flags = self._process_link_flags(
            namespace.link_flags, dependencies
        )

        original_srcs = []
        objects = []
        sources = []
        for infile in namespace.infiles:
            infile = self.context.normalize_path(infile)
            assert not (
                self.platform.is_static_lib(infile)
                or self.platform.is_shared_lib(infile)
            ), infile
            language = None
            ext = os.path.splitext(infile)[1]
            if ext in self.c_exts:
                language = "C"
            elif ext in self.cpp_exts:
                language = "C++"
            elif ext in self.asm_exts:
                language = "GASM"

            if language is None:
                objects.append(self.context.get_file_arg(infile, dependencies))
            else:
                original_srcs.append(infile)
                sources.append(
                    get_source_file_reference(
                        self.context.get_file_arg(infile, dependencies), language
                    )
                )

        if not sources:
            # Ignore compiler flags if no source files specified
            namespace.compile_flags = []
            namespace.include_dirs = []

        CompilerParser.process_namespace(self, namespace)

        include_dirs_not_relocatable = namespace.include_dirs

        namespace.include_dirs = [
            self.context.get_dir_arg(self.context.normalize_path(d), dependencies)
            for d in include_dirs_not_relocatable
        ]

        if namespace.mode == self.Mode.assemble:
            if namespace.output is None:
                namespace.output = (
                    os.path.basename(os.path.splitext(namespace.infiles[0])[0]) + ".o"
                )
            module_type = ModuleTypes.object_lib
            name = None
            version = None
        elif namespace.mode == self.Mode.link:
            if namespace.output is None:
                namespace.output = "a.out"
            descr = None
            if namespace.is_shared:
                descr = self.platform.parse_shared_lib(namespace.output)
                module_type = ModuleTypes.shared_lib
            else:
                descr = self.platform.parse_executable(namespace.output)
                module_type = ModuleTypes.executable
            if descr:
                name = descr["target_name"]
                version = descr["version"]
            else:
                name = None
                version = None

        namespace.output = self.context.normalize_path(namespace.output)
        normalize_implicit_dependencies = self._add_implicit_dependencies(
            gcc,
            dependencies,
            namespace.compile_flags,
            include_dirs_not_relocatable,
            original_srcs,
            self.platform_name,
            self.context.working_dir,
        )
        namespace.output = self.context.get_output(namespace.output, dependencies)

        namespace.include_dirs.extend(
            self.context.get_implicit_include_dirs(
                sources,
                namespace.include_dirs,
                normalize_implicit_dependencies,
            )
        )

        target = get_module_target(
            module_type,
            name,
            namespace.output,
            compile_flags=namespace.compile_flags,
            dependencies=dependencies,
            include_dirs=namespace.include_dirs,
            link_flags=namespace.link_flags,
            libs=namespace.libs,
            objects=objects,
            sources=sources,
            version=version,
        )

        return target


__all__ = ["Clang_Gcc"]
