from copy import deepcopy
import os
from build_migrator.helpers import get_module_target, ModuleTypes
from build_migrator.modules import Parser
from build_migrator.parsers.msvc_link import is_lib_shim
import build_migrator.common.os_ext as os_ext
from build_migrator.common.argument_parser_ex import ArgumentParserEx


class MsvcLib(Parser):
    filename_re = os_ext.Windows.get_program_path_re("lib")
    link_re = os_ext.Windows.get_program_path_re("link")
    lld_link_re = os_ext.Windows.get_program_path_re("lld-link")

    priority = 7

    @staticmethod
    def add_arguments(arg_parser):
        pass

    @staticmethod
    def is_applicable(project=None, log_type=None):
        return True

    def __init__(self, context, project_version=None):
        self.context = context
        self.project_version = project_version

        # Visual Studio lib.exe arguments
        # https://docs.microsoft.com/en-us/cpp/build/reference/running-lib?view=vs-2019
        self.parser = ArgumentParserEx(prefix_chars="-/")
        self.parser.set_defaults(
            compile_flags=[], link_flags=[], include_dirs=[], infiles=[]
        )
        # TODO: publish all meaningful flags
        self.parser.set(ignore_case=True, dest=None, raw_dest="link_flags")
        self.parser.add_argument("/ignore", action="msvc_flag_with_value")
        self.parser.add_argument(
            "/libpath", action="msvc_flag_with_value", append=True, raw_dest=None
        )
        self.parser.add_argument("/ltcg", action="store_true")
        self.parser.add_argument("/machine", action="msvc_flag_with_value")
        self.parser.add_argument(
            "/out", action="msvc_flag_with_value", dest="output", raw_dest=None
        )
        self.parser.add_argument("/nologo", action="store_true")
        self.parser.add_argument("/wx", action="msvc_flag", msvc_false_suffix=":no")
        self.parser.add_argument("infiles", dest="infiles", nargs="*", raw_dest=None)

        # lld-link.exe arguments (/lib mode)
        # Cannot find documentation online
        self.lld_link_parser = deepcopy(self.parser)
        self.lld_link_parser.add_argument("/llvmlibthin", action="store_true")
        self.lld_link_parser.set(prefix_chars="-")
        self.lld_link_parser.add_argument("--color-diagnostics", action="store_true")

    def parse(self, target):
        tokens = target.get("tokens") or []
        if not tokens:
            return target

        is_lld_link = False
        if self.link_re.match(tokens[0]) and is_lib_shim(tokens):
            is_lld_link = bool(self.lld_link_re.match(tokens[0]))
            tokens = tokens[2:]
        elif not self.filename_re.match(tokens[0]):
            return target
        else:
            tokens.pop(0)

        if len(tokens) > 0:
            if tokens[0] == ":":
                # skipping parsing output of utilities, like: `lib : warning ...`
                return target

        if is_lld_link:
            namespace = self.lld_link_parser.parse_args(tokens)
        else:
            namespace = self.parser.parse_args(tokens)

        dependencies = []

        libs = []
        objects = []
        for infile in namespace.infiles:
            if os_ext.is_static_lib(infile):
                libs.append(self.context.get_lib_arg(infile, dependencies, []))
            else:
                path = next(
                    os_ext.Windows.get_obj_file_locations(
                        infile, [], self.context.working_dir
                    )
                )
                if self.context.find_target(
                    self.context.get_file_arg(path)
                ) or os.path.exists(path):
                    objects.append(self.context.get_file_arg(path, dependencies))
                else:
                    # System object file, treat it as a linker flag
                    # https://docs.microsoft.com/en-us/cpp/c-runtime-library/link-options
                    objects.append(infile)

        output = self.context.normalize_path(namespace.output)
        descr = os_ext.parse_static_lib(output)
        module_name = descr["module_name"]
        name = descr["target_name"]
        version = descr["version"] or self.project_version
        output = self.context.get_output(output, dependencies)

        return get_module_target(
            ModuleTypes.static_lib,
            name,
            output,
            dependencies=dependencies,
            module_name=module_name,
            libs=libs,
            objects=objects,
            version=version,
            link_flags=namespace.link_flags,
        )


__all__ = ["MsvcLib"]
