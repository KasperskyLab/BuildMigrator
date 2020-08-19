import logging
import os
import copy
from build_migrator.helpers import ArgumentParserNoExit, get_module_target, ModuleTypes
from build_migrator.modules import Parser
from build_migrator.common.os_ext import get_platform


logger = logging.getLogger(__name__)


class GnuAr(Parser):
    class Modes:
        default = "default"
        after = "after"
        before = "before"

    priority = 7

    @staticmethod
    def add_arguments(arg_parser):
        pass

    @staticmethod
    def is_applicable(project=None, log_type=None):
        return True

    def __init__(self, context, platform=None):
        self.platform = get_platform(platform)
        self.program_re = self.platform.get_program_path_re("ar")
        self.context = context

        # see https://linux.die.net/man/1/ar
        self.parser = ArgumentParserNoExit(prog="ar")
        self.parser.add_argument("-q", action="store_true", dest="insert")
        self.parser.add_argument("-r", action="store_true", dest="replace")
        self.parser.add_argument("-c", action="store_true", dest="create")
        self.parser.add_argument("-s", action="store_true", dest="index")
        self.parser.add_argument("-v", action="store_true", dest="verbose")
        self.parser.add_argument("-N", action="store_true", dest="multiple")
        self.parser.add_argument("-u", action="store_true", dest="update")
        self.parser.add_argument("-x", action="store_true", dest="extract")
        self.parser.add_argument("-t", action="store_true", dest="table")
        parser_mode = self.parser.add_mutually_exclusive_group()
        parser_mode.set_defaults(mode=self.Modes.default)
        parser_mode.add_argument(
            "-a", action="store_const", const=self.Modes.after, dest="mode"
        )
        parser_mode.add_argument(
            "-b", "-i", action="store_const", const=self.Modes.before, dest="mode"
        )

    def parse(self, target):
        tokens = target.get("tokens")
        if not tokens:
            return target

        if not self.program_re.match(tokens[0]):
            return target

        tokens.pop(0)  # 'ar' location doesn't matter

        # ArgumentParser doesn't support flags without prefix
        if not tokens[0].startswith("-"):
            tokens[0] = "-" + tokens[0]

        namespace, tokens = self.parser.parse_known_args(tokens)

        if namespace.extract:
            # Extract objects from previously built archive
            return self.extract_targets_from_archive(namespace, tokens)

        if namespace.table:
            # skip listing content of archive
            return []

        if namespace.mode != self.Modes.default:
            tokens.pop(0)  # 'relpos' is unused
        if namespace.multiple:
            tokens.pop(0)  # 'count' is unused

        output = self.context.normalize_path(tokens.pop(0))

        dependencies = []
        objects = []
        for token in tokens:
            objects.append(
                self.context.get_file_arg(
                    self.context.normalize_path(token), dependencies
                )
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

    def extract_targets_from_archive(self, namespace, tokens):
        resulting_targets = list()
        for token in tokens:
            archive_target = self.context.find_target(self.context.get_output(token))
            if archive_target is None:
                logger.error("Cannot find target for archive file " + token)
                continue

            for object in archive_target["objects"]:
                object_target = self.context.find_target(object)
                new_object_target = copy.deepcopy(object_target)

                object_name = self.context.normalize_path(
                    os.path.basename(object_target["output"])
                )
                new_object_target["output"] = self.context.get_output(object_name)
                new_object_target["name"] = None

                resulting_targets.append(new_object_target)

        return resulting_targets


__all__ = ["GnuAr"]
