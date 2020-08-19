import logging
from build_migrator.helpers import ArgumentParserNoExit, get_module_target, ModuleTypes
from build_migrator.modules import Parser
from build_migrator.common.os_ext import get_platform


logger = logging.getLogger(__name__)


class Libtool(Parser):
    priority = 7

    @staticmethod
    def add_arguments(arg_parser):
        pass

    @staticmethod
    def is_applicable(project=None, log_type=None):
        return True

    def __init__(self, context, project_version=None, platform=None):
        self.context = context
        self.platform = get_platform(platform)
        self.project_version = project_version
        self.program_re = self.platform.get_program_path_re("libtool")

        # see https://www.gnu.org/software/libtool/manual/libtool.html
        self.parser = ArgumentParserNoExit(prog="libtool")
        self.parser.add_argument("-static", action="store_true")
        self.parser.add_argument("objects", nargs="+")
        self.parser.add_argument("-o", dest="output")

    def parse(self, target):
        tokens = target.get("tokens")
        if not tokens:
            return target

        if not self.program_re.match(tokens[0]):
            return target

        tokens.pop(0)

        namespace = self.parser.parse_args(tokens)
        if not namespace.static:
            logger.error("libtool: only -static mode is supported")
            return target

        output = self.context.normalize_path(namespace.output)

        dependencies = []
        objects = []
        for o in namespace.objects:
            objects.append(
                self.context.get_file_arg(self.context.normalize_path(o), dependencies)
            )

        descr = self.platform.parse_static_lib(output)
        output = self.context.get_output(output)
        return get_module_target(
            ModuleTypes.static_lib,
            descr["target_name"],
            output,
            objects=objects,
            dependencies=dependencies,
            module_name=descr["module_name"],
        )


__all__ = ["Libtool"]
