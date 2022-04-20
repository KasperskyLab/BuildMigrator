from copy import deepcopy
import os

import build_migrator.common.os_ext as os_ext

from build_migrator.common.argument_parser_ex import ArgumentParserEx
from build_migrator.helpers import (
    get_module_target,
    ModuleTypes,
    get_source_file_reference,
    filter_flags,
)

from .base.linker_parser import LinkerParser


def is_lib_shim(args):
    if len(args) > 1 and args[1].lower().replace("-", "/") == "/lib":
        # link.exe /lib = lib.exe
        return True
    return False


class MsvcLink(LinkerParser):
    filename_re = os_ext.Windows.get_program_path_re("link")
    lld_link_re = os_ext.Windows.get_program_path_re("lld-link")

    priority = 7

    def __init__(self, context, ignore_link_flags=None):
        LinkerParser.__init__(self, context, ignore_link_flags=ignore_link_flags)

        # Visual Studio link.exe arguments
        # https://docs.microsoft.com/en-us/cpp/build/reference/linker-options?view=vs-2017
        self.parser = ArgumentParserEx(prefix_chars="/-")
        self.parser.set_defaults(
            compile_flags=[], link_flags=[], include_dirs=[], infiles=[], lib_dirs=[]
        )
        # TODO: publish all meaningful flags
        self.parser.set(
            ignore_case=True,
            action="msvc_flag_with_value",
            raw_dest="link_flags",
            dest=None,
        )
        # TODO: handle /wholearchive
        self.parser.add_argument("/base", action="msvc_flag_with_value")
        self.parser.add_argument("/debug")
        self.parser.add_argument("/debug", action="store_true")
        self.parser.add_argument("/fixed", action="msvc_flag", msvc_false_suffix=":no")
        self.parser.add_argument("/delayload", action="msvc_flag_with_value")
        self.parser.add_argument("/def")
        self.parser.add_argument(
            "/dll", action="store_true", dest="is_dll", raw_dest=None
        )
        self.parser.add_argument(
            "/dynamicbase", action="msvc_flag", msvc_false_suffix=":no"
        )
        self.parser.add_argument("/errorreport")
        self.parser.add_argument("/fastfail", action="store_true")
        self.parser.add_argument("/guard", action="msvc_flag_with_value")
        # Ignore Specific Warnings
        self.parser.add_argument("/ignore", action="msvc_flag_with_value")
        self.parser.add_argument("/implib", dest="implib", raw_dest=None)
        self.parser.add_argument(
            "/incremental", action="msvc_flag", msvc_false_suffix=":no"
        )
        self.parser.add_argument(
            "/largeaddressaware", action="msvc_flag", msvc_false_suffix=":no"
        )
        self.parser.add_argument(
            "/libpath", append=True, dest="lib_dirs", raw_dest=None
        )
        self.parser.add_argument("/ltcg")
        self.parser.add_argument("/ltcg", action="store_true")
        self.parser.add_argument("/machine")
        self.parser.add_argument("/manifest")
        self.parser.add_argument("/manifest", action="store_true")
        self.parser.add_argument(
            "/manifestinput", raw_dest=None, dest="manifest_files", append=True
        )
        self.parser.add_argument(
            "/manifestfile", raw_dest=None, dest="manifest_files", append=True
        )
        self.parser.add_argument("/manifestuac")
        self.parser.add_argument("/manifestuac", action="store_true")
        self.parser.add_argument("/map")
        self.parser.add_argument("/map", action="store_true")
        self.parser.add_argument("/mapinfo")
        self.parser.add_argument("/noentry", action="store_true")
        self.parser.add_argument("/nologo", action="store_true")
        self.parser.add_argument("/natvis", action="msvc_flag_with_value")
        self.parser.add_argument(
            "/nxcompat", action="msvc_flag", msvc_false_suffix=":no"
        )
        self.parser.add_argument("/opt", append=True)
        self.parser.add_argument("/out", dest="output", raw_dest=None)
        self.parser.add_argument("/pdb")
        self.parser.add_argument("/pdbaltpath")
        self.parser.add_argument("/profile", action="store_true")
        self.parser.add_argument("/safeseh", action="store_true")
        self.parser.add_argument("/stack")
        self.parser.add_argument("/subsystem")
        self.parser.add_argument("/timestamp")
        self.parser.add_argument("/tlbid")
        self.parser.add_argument("/version")
        self.parser.add_argument("/wholearchive", append=True)
        self.parser.add_argument("/wholearchive", action="store_true")
        self.parser.add_argument("/WX", action="msvc_flag", msvc_false_suffix=":no")
        self.parser.set(action=None)
        self.parser.add_argument("infiles", nargs="*", raw_dest=None, dest="infiles")

        # lld-link.exe arguments
        # Cannot find documentation online
        self.lld_link_parser = deepcopy(self.parser)
        self.lld_link_parser.add_argument("/llvmlibthin", action="store_true")
        self.lld_link_parser.set(prefix_chars="-")
        self.lld_link_parser.add_argument("--color-diagnostics", action="store_true")

    def _process_link_flags(self, flags, dependencies):
        for idx, flag in enumerate(flags):
            flag_lower = flag.lower()
            if flag_lower[0] == "/":
                flag_lower = "-" + flag_lower[1:]
            if flag_lower.startswith("-def:"):
                flags[idx] = flag[:5] + self.context.get_file_arg(
                    flag[5:], dependencies
                )
        return flags

    def parse(self, target):
        tokens = target.get("tokens") or []
        if not tokens:
            return target

        if not self.filename_re.match(tokens[0]):
            return target
        else:
            if is_lib_shim(tokens):
                return target

        if len(tokens) < 2 or tokens[1] == ":":
            # skip warning message
            return target

        is_lld_link = bool(self.lld_link_re.match(tokens[0]))
        tokens.pop(0)

        if is_lld_link:
            namespace, _ = self.lld_link_parser.parse_known_args(
                tokens, unknown_dest=["compile_flags", "link_flags"]
            )
        else:
            namespace, _ = self.parser.parse_known_args(
                tokens, unknown_dest=["compile_flags", "link_flags"]
            )

        dependencies = []

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

        objects = []
        libs = []
        for infile in namespace.infiles:
            if os_ext.Windows.is_static_lib(infile):
                libs.append(self.context.get_lib_arg(infile, dependencies, lib_dirs))
            else:
                paths = os_ext.Windows.get_obj_file_locations(
                    infile, lib_dirs, self.context.working_dir
                )
                found = False
                for path in paths:
                    if self.context.find_target(
                        self.context.get_file_arg(path)
                    ) or os.path.exists(path):
                        objects.append(self.context.get_file_arg(path, dependencies))
                        found = True
                        break
                if not found:
                    # System object file, treat it as a linker flag
                    # https://docs.microsoft.com/en-us/cpp/c-runtime-library/link-options
                    objects.append(infile)

        namespace.link_flags = self._process_link_flags(
            namespace.link_flags, dependencies
        )

        sources = []
        for manifest in vars(namespace).get("manifest_files") or []:
            sources.append(
                get_source_file_reference(
                    self.context.get_file_arg(
                        self.context.normalize_path(manifest), dependencies
                    )
                )
            )

        import_lib = None
        if vars(namespace).get("implib"):
            import_lib = self.context.get_output(namespace.implib, dependencies)

        output = self.context.normalize_path(namespace.output)
        if os_ext.Windows.is_shared_lib(output):
            # DLL file is created if:
            # 1. /DLL flag was specified, or
            # 2. LIBRARY statement is present in provided .def file
            # TODO: validate these conditions here
            descr = os_ext.Windows.parse_shared_lib(output)
            module_type = ModuleTypes.shared_lib
            if not import_lib:
                import_lib = self.context.get_output(
                    os.path.splitext(namespace.output)[0] + ".lib", dependencies
                )
        else:
            descr = os_ext.Windows.parse_executable(output)
            module_type = ModuleTypes.executable

        name = descr["target_name"]
        version = descr["version"]
        output = self.context.get_output(output, dependencies)

        self.process_namespace(namespace)

        return get_module_target(
            module_type,
            name,
            output,
            msvc_import_lib=import_lib,
            dependencies=dependencies,
            objects=objects,
            libs=libs,
            link_flags=namespace.link_flags,
            sources=sources,
            version=version,
        )


def get_msvc_link_parser(*args, **kwargs):
    return MsvcLink(*args, **kwargs).parser


__all__ = ["MsvcLink"]
