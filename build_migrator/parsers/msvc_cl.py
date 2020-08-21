from copy import deepcopy
import logging
import os
import re

from build_migrator.common.algorithm import flatten_list
from build_migrator.common.argument_parser_ex import ArgumentParserEx
import build_migrator.common.os_ext as os_ext
from build_migrator.common import subprocess_ex
from build_migrator.helpers import (
    get_module_target,
    ModuleTypes,
    get_source_file_reference,
    format_flag_msvc_lowercase,
    format_flag_gnu,
    format_flag_msvc,
    filter_flags,
)
from .msvc_link import get_msvc_link_parser

from .base.compiler_parser import CompilerParser
from .base.linker_parser import LinkerParser

logger = logging.getLogger(__name__)


def get_gcc_toolchain_include_dirs(compiler, context, language="c"):
    cmd = [compiler, "-x" + language, "-E", "-v", os.devnull]
    stdout, stderr = subprocess_ex.check_output(cmd)

    parse_dirs = False
    dirs = []
    for line in (stderr + "\n" + stdout).splitlines():
        if line.startswith("#include"):
            parse_dirs = True
        elif line.startswith("End of search list"):
            parse_dirs = False
        elif parse_dirs:
            line = line.strip()
            if line:
                dirs.append(line)
    return prepare_toolchain_include_dirs(dirs, context)


# Normalize paths, remove build and source directories,
# add '/' at the end to make sure its treated as directory
# when calling some_path.startswith(toolchain_include_dir)
def prepare_toolchain_include_dirs(dirs, context):
    dirs = [context.normalize_path(tid) + "/" for tid in dirs if len(tid) > 0]
    ignore_dirs = [d + "/" for d in (context.build_dirs + [context.source_dir])]
    return [tid for tid in dirs if not any([d.startswith(tid) for d in ignore_dirs])]


# TODO: put all unknown flags into compile_flags?
class MsvcCl(CompilerParser, LinkerParser):
    filename_re = os_ext.Windows.get_program_path_re("cl")
    clang_cl_re = os_ext.Windows.get_program_path_re("clang-cl")

    c_exts = [".c"]
    cpp_exts = [".cc", ".cpp", ".cxx"]
    source_exts = c_exts + cpp_exts

    priority = 7

    @staticmethod
    def add_arguments(arg_parser):
        CompilerParser.add_arguments(arg_parser)
        LinkerParser.add_arguments(arg_parser)

    def __init__(self, context, ignore_compile_flags=None, ignore_link_flags=None):
        CompilerParser.__init__(
            self, context, ignore_compile_flags=ignore_compile_flags
        )
        LinkerParser.__init__(self, context, ignore_link_flags=ignore_link_flags)

        # /showIncludes flag doesn't allow filtering toolchain includes,
        # se we have to do that ourselves.
        msvc_include_dirs = os.environ.get("INCLUDE", [])
        if msvc_include_dirs:
            self.msvc_include_dirs = prepare_toolchain_include_dirs(
                msvc_include_dirs.split(";"), context
            )
        else:
            self.msvc_include_dirs = []
        logger.debug("MSVC include dirs: %r" % self.msvc_include_dirs)
        self.clang_cl_include_dirs = None

        # Visual Studio cl.exe arguments
        # https://docs.microsoft.com/en-us/cpp/build/reference/compiler-options-listed-alphabetically?view=vs-2017
        self.parser = ArgumentParserEx(prefix_chars="-/")
        self.parser.set_defaults(
            compile_flags=[], link_flags=[], include_dirs=[], infiles=[]
        )
        # TODO: publish all meaningful flags
        # TODO: specify raw_format= for each argument
        self.parser.set(dest=None, raw_dest="compile_flags")
        # Enables code analysis and control options
        self.parser.add_argument("/analyze", prefix=True)
        self.parser.add_argument("/arch", action="msvc_flag_with_value")
        self.parser.add_argument(
            "/bigobj",
            action="store_true",
            raw_format=format_flag_msvc_lowercase,
            ignore_case=True,
        )
        # Emit an object file which can be reproduced over time
        self.parser.add_argument("/Brepro", action="msvc_flag")
        self.parser.add_argument(
            "/c", action="store_true", dest="compile_only", raw_dest=None
        )
        self.parser.add_argument("/D", raw_format=format_flag_gnu)
        # /d1xxx = undocumented frontend options
        self.parser.add_argument(prefixes=["/d1", "-d1"])
        # /d2xxx = undocumented backend options
        self.parser.add_argument(prefixes=["/d2", "-d2"])
        self.parser.add_argument("/diagnostics", action="msvc_flag_with_value")
        # Exception Handling Model
        self.parser.add_argument(prefixes=["/EH", "-EH"])
        self.parser.add_argument(
            "/errorreport", action="msvc_flag_with_value", ignore_case=True
        )
        self.parser.add_argument("/favor", action="msvc_flag_with_value")
        self.parser.add_argument("/FC", action="store_true")
        # Force include
        # TODO: process path arg declaratively (type= argument?)
        self.parser.add_argument("/FI", prefix=True)
        self.parser.add_argument("/FR", prefix=True)
        # IDE minimal rebuild
        self.parser.add_argument("/FD", action="store_true")
        # Detect 64-Bit Portability Issues
        self.parser.add_argument("/Wp64", action="store_true")
        # Floating point behavior
        self.parser.add_argument("/fp", action="msvc_flag_with_value")
        # Force Synchronous PDB Writes
        self.parser.add_argument("/FS", action="store_true")
        # Program Database File Name
        self.parser.add_argument("/Fd", prefix=True)
        # Output: exe, dll
        self.parser.add_argument("/Fe", prefix=True, dest="output", raw_dest=None)
        # Output: obj
        self.parser.add_argument("/Fo", prefix=True, dest="output", raw_dest=None)
        # Precompiled header (.pch) file name
        # TODO: process path arg
        self.parser.add_argument("/Fp", prefix=True)
        # Eliminate Duplicate Strings
        self.parser.add_argument("/GF", action="store_true")
        # Whole Program Optimization
        self.parser.add_argument("/GL", action="msvc_flag")
        # Full path of source code file in diagnostics
        self.parser.add_argument("/FC", action="msvc_flag")
        # Runtime Type Information
        self.parser.add_argument("/GR", action="msvc_flag", raw_format=format_flag_msvc)
        # Calling convention
        self.parser.add_argument("/Gd", "/Gr", "/Gv", "/Gz", action="store_true")
        # Minimal rebuild
        self.parser.add_argument("/Gm", action="msvc_flag", raw_dest=None)
        # /sdl - Enable additional security check
        self.parser.add_argument("/sdl-", action="msvc_flag")
        # Buffer Security Check
        self.parser.add_argument("/GS", action="msvc_flag")
        # Control Stack Checking Calls
        self.parser.add_argument("/Gs", action="store_true")
        self.parser.add_argument(prefixes=["/Gs", "-Gs"], type=int)
        # Control Flow Guard
        self.parser.add_argument("/guard:cf", action="msvc_flag")
        # Optimize Global Data
        self.parser.add_argument("/Gw", action="msvc_flag")
        # Enable Function-Level Linking
        self.parser.add_argument("/Gy", action="msvc_flag")
        # TODO: process path arg
        self.parser.add_argument(
            "/I", action="append", dest="include_dirs", raw_dest=None
        )
        # Create dll
        self.parser.add_argument(
            "/LD", "/LDd", action="store_true", raw_dest=None, dest="is_dll"
        )
        # Passes one or more linker options to the linker
        # The /link option and its linker options must appear after
        # any file names and CL options
        self.parser.add_argument("/link", nargs="+", raw_dest="link_flags")
        # Dynamic runtime
        self.parser.add_argument("/MD", "/MDd", action="store_true")
        self.parser.add_argument("/MP", action="store_true")
        self.parser.add_argument(prefixes=["/MP", "-MP"], type=int)
        # Static runtime
        self.parser.add_argument("/MT", "/MTd", action="store_true")
        self.parser.add_argument("/nologo", action="store_true", ignore_case=True)
        # Optimize Code
        self.parser.add_argument(prefixes=["/O", "-O"], choices="12bdgistxy")
        # Inline Function Expansion
        self.parser.add_argument(prefixes=["/Ob", "-Ob"], choices="012")
        # Frame-Pointer Omission
        self.parser.add_argument("/Oy", action="msvc_flag")
        self.parser.add_argument("/showIncludes", action="store_true")
        self.parser.add_argument("/source-charset", action="msvc_flag_with_value")
        self.parser.add_argument("/std", action="msvc_flag_with_value")
        self.parser.add_argument("/TC", action="store_true")
        self.parser.add_argument("/TP", action="store_true")
        # C file
        # TODO: process path arg
        self.parser.add_argument("/Tc")
        # C++ file
        # TODO: process path arg
        self.parser.add_argument("/Tp")
        self.parser.add_argument("/utf-8", action="store_true")
        self.parser.add_argument("/U", raw_format=format_flag_gnu)
        # Ignore system PATH and INCLUDE
        self.parser.add_argument("/X", action="store_true")
        # Create Precompiled Header File
        self.parser.add_argument("/Yc", action="store_true")
        self.parser.add_argument("/Yc", prefix=True)
        # Use Precompiled Header File
        self.parser.add_argument("/Yu", action="store_true")
        self.parser.add_argument("/Yu", prefix=True)
        # Debug Information Format
        self.parser.add_argument("/Z7", "/Zi", "/Zl", action="store_true")
        # Conformance
        self.parser.add_argument("/Zc", action="msvc_flag_with_value")
        # Syntax Check Only
        self.parser.add_argument(
            "/Zs", dest="syntax_check_only", raw_dest=None, action="store_true"
        )
        # Precompiled Header Memory Allocation Limit
        self.parser.add_argument("/Zm", prefix=True)
        self.parser.add_argument(
            "/w", "/W0", "/W1", "/W2", "/W3", "/W4", "/Wall", action="store_true"
        )
        self.parser.add_argument("/WX", action="msvc_flag")
        self.parser.add_argument(
            prefixes=[
                "/Wv",
                "/w1",
                "/w2",
                "/w3",
                "/w4",
                "/wd",
                "/we",
                "/wo",
                "-Wv",
                "-w1",
                "-w2",
                "-w3",
                "-w4",
                "-wd",
                "-we",
                "-wo",
            ]
        )
        # TODO: process path arg
        self.parser.add_argument("infiles", nargs="*", dest="infiles", raw_dest=None)

        # clang-cl.exe arguments
        # https://clang.llvm.org/docs/UsersManual.html#id9
        self.clang_cl_parser = deepcopy(self.parser)
        self.clang_cl_parser.set(prefix_chars="-")
        self.clang_cl_parser.add_argument("-imsvc", prefix=True)
        self.clang_cl_parser.add_argument("-Xclang")
        self.clang_cl_parser.add_argument(prefixes=["-f"])
        # Processor options
        self.clang_cl_parser.add_argument(prefixes=["-m"])
        self.clang_cl_parser.add_argument("-no-canonical-prefixes", action="store_true")
        self.clang_cl_parser.add_argument(prefixes=["-std="])
        self.clang_cl_parser.add_argument(prefixes=["-W"])

        self.link_parser = get_msvc_link_parser(
            context, ignore_link_flags=ignore_link_flags
        )

    re_str = r"^Note: including file:\s+(?P<path>[^\s].*)$"
    include_note_re = re.compile(re_str, re.IGNORECASE)

    def _add_implicit_dependencies(
        self,
        compiler,
        dependencies,
        compile_flags,
        include_dirs,
        sources,
        cwd,
        is_clang_cl=False,
    ):
        if not sources:
            return

        _compiler = os.path.join(cwd, compiler)
        if os.path.exists(_compiler):
            compiler = _compiler

        cmd = [compiler, "/Zs", "/showIncludes"]
        cmd += ["-I" + d for d in include_dirs] + flatten_list(compile_flags) + sources
        try:
            stdout, stderr = subprocess_ex.check_output(cmd, cwd=cwd)
        except subprocess_ex.CalledProcessError as e:
            logger.error("{}\nstderr:\n{}stdout:\n{}".format(e, e.stderr, e.stdout))
            return

        toolchain_include_dirs = self.msvc_include_dirs
        if is_clang_cl and self.clang_cl_include_dirs:
            toolchain_include_dirs = self.clang_cl_include_dirs
        for line in stdout.splitlines():
            m = self.include_note_re.match(line.strip())
            if m:
                try:
                    path = self.context.normalize_path(m.group("path"))
                    is_toolchain_header = False
                    for d in toolchain_include_dirs:
                        if path.startswith(d):
                            is_toolchain_header = True
                            break
                    if not is_toolchain_header:
                        self.context.get_file_arg(path, dependencies)
                except ValueError:
                    # Path is on drive c:, build dir on drive d:
                    pass

    def _get_clang_cl_toolchain_include_dirs(self, compiler):
        try:
            clang_cl_include_dirs_c = get_gcc_toolchain_include_dirs(
                compiler, self.context, "c"
            )
        except subprocess_ex.CalledProcessError as e:
            logger.error("{}\nstderr:\n{}stdout:\n{}".format(e, e.stderr, e.stdout))
            return []
        try:
            clang_cl_include_dirs_cpp = get_gcc_toolchain_include_dirs(
                compiler, self.context, "c++"
            )
        except subprocess_ex.CalledProcessError as e:
            logger.error("{}\nstderr:\n{}stdout:\n{}".format(e, e.stderr, e.stdout))
            return []
        include_dirs = set(clang_cl_include_dirs_c)
        include_dirs.update(clang_cl_include_dirs_cpp)
        return [self.context.normalize_path(d) for d in include_dirs]

    def parse(self, target):
        tokens = target.get("tokens")
        if not tokens:
            return target

        if not self.filename_re.match(tokens[0]):
            return target

        if len(tokens) < 2 or tokens[1] == ":":
            # skip warning message
            return target

        compiler = tokens.pop(0)
        compiler_nrm = self.context.platform.normalize_path(compiler)
        is_clang_cl = bool(self.clang_cl_re.match(compiler))
        if compiler_nrm in self.context.path_aliases:
            compiler = self.context.path_aliases[compiler_nrm]

        if not is_clang_cl:
            namespace, _ = self.parser.parse_known_args(
                tokens, unknown_dest="compile_flags"
            )
        else:
            namespace, _ = self.clang_cl_parser.parse_known_args(
                tokens, unknown_dest="compile_flags"
            )
            if self.clang_cl_include_dirs is None:
                self.clang_cl_include_dirs = self._get_clang_cl_toolchain_include_dirs(
                    compiler
                )
                logger.debug("clang-cl include dirs: %r" % self.clang_cl_include_dirs)

        lib_dirs = []
        dependencies = []
        if namespace.link_flags:
            link_flags = namespace.link_flags[0]
            namespace.link_flags = []
            namespace, _ = self.link_parser.parse_known_args(
                link_flags[1:], namespace, unknown_dest=["link_flags"]
            )

            # Copied from msvc_link.py
            # TODO: unify msvc_cl.py, msvc_link.py, msvc_lib.py
            lib_dirs = list(
                map(
                    lambda p: p[len("/LIBPATH:"):],
                    filter_flags(
                        self.ignore_link_flags_rxs,
                        ["/LIBPATH:" + d for d in namespace.lib_dirs],
                    ),
                )
            )
            for d in lib_dirs:
                d = self.context.normalize_path(d)
                relocatable_path = self.context.get_dir_arg(d)
                if relocatable_path.startswith("@"):
                    # ignore non-relocatable lib dirs
                    self.context.get_dir_arg(d, dependencies)

        if namespace.syntax_check_only:
            return target

        sources = []
        src_info = {}
        objects = []
        libs = []
        for infile in namespace.infiles:
            ext = os.path.splitext(infile)[1].lower()
            language = None
            if ext in self.c_exts:
                language = "C"
            elif ext in self.cpp_exts:
                language = "C++"

            if language:
                src_deps = []
                relocatable_path = self.context.get_file_arg(
                    self.context.normalize_path(infile), src_deps
                )
                src_info[relocatable_path] = {
                    "unmodified_path": infile,
                    "dependencies": src_deps,
                }
                sources.append(get_source_file_reference(relocatable_path, language))
            else:
                # Copied from msvc_link.py
                # TODO: unify msvc_cl.py, msvc_link.py, msvc_lib.py
                if os_ext.Windows.is_static_lib(infile):
                    libs.append(
                        self.context.get_lib_arg(infile, dependencies, lib_dirs)
                    )
                else:
                    paths = os_ext.Windows.get_obj_file_locations(
                        infile, lib_dirs, self.context.working_dir
                    )
                    found = False
                    for path in paths:
                        if self.context.find_target(
                            self.context.get_file_arg(path)
                        ) or os.path.exists(path):
                            objects.append(
                                self.context.get_file_arg(path, dependencies)
                            )
                            found = True
                            break
                    if not found:
                        # System object file, treat it as a linker flag
                        # https://docs.microsoft.com/en-us/cpp/c-runtime-library/link-options
                        objects.append(infile)

        CompilerParser.process_namespace(self, namespace)

        include_dirs_not_relocatable = namespace.include_dirs

        include_dirs = list(
            map(
                lambda d: self.context.get_dir_arg(
                    self.context.normalize_path(d), dependencies
                ),
                include_dirs_not_relocatable,
            )
        )
        namespace.include_dirs = list(filter(lambda d: bool(d), include_dirs))

        output = None
        if namespace.output[-1] in ["/", "\\"]:
            # output is a directory
            output_dir = self.context.normalize_path(namespace.output)
        else:
            output = self.context.normalize_path(namespace.output)

        output_dict = {}
        if output:
            output_dict[output] = sources
        else:
            assert namespace.compile_only
            # put .obj files in output_dir
            # separate .obj file for each source
            for s in sources:
                basename = os.path.basename(s["path"])
                objfile = os.path.splitext(basename)[0] + ".obj"
                cur_output = os.path.join(output_dir, objfile)
                output_dict[cur_output] = [s]

        targets = []
        for output, sources in output_dict.items():
            deps_local = deepcopy(dependencies)
            original_sources = []
            for s in sources:
                deps_local.extend(src_info[s["path"]]["dependencies"])
                original_sources.append(src_info[s["path"]]["unmodified_path"])
            self._add_implicit_dependencies(
                compiler,
                deps_local,
                namespace.compile_flags,
                include_dirs_not_relocatable,
                original_sources,
                self.context.working_dir,
                is_clang_cl=is_clang_cl,
            )
            import_lib = None
            descr = {}
            if namespace.compile_only:
                module_type = ModuleTypes.object_lib
            elif namespace.is_dll:
                assert os_ext.Windows.is_shared_lib(output), output
                module_type = ModuleTypes.shared_lib
                descr = os_ext.Windows.parse_shared_lib(output)
                import_lib = self.context.get_output(
                    os.path.splitext(output)[0] + ".lib", deps_local
                )
            else:
                module_type = ModuleTypes.executable
                descr = os_ext.Windows.parse_executable(output)

            output = self.context.get_output(output, deps_local)
            module_name = descr.get("module_name")
            name = descr.get("target_name")

            LinkerParser.process_namespace(self, namespace)

            targets.append(
                get_module_target(
                    module_type,
                    name,
                    output,
                    msvc_import_lib=import_lib,
                    module_name=module_name,
                    compile_flags=namespace.compile_flags,
                    dependencies=deps_local,
                    include_dirs=namespace.include_dirs,
                    link_flags=namespace.link_flags,
                    objects=objects,
                    libs=libs,
                    sources=sources,
                )
            )
        return targets


__all__ = ["MsvcCl"]
