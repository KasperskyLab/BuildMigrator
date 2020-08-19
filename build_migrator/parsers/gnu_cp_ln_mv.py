import logging
import os
from build_migrator.helpers import ArgumentParserNoExit
from build_migrator.modules import Parser
import build_migrator.common.os_ext as os_ext


logger = logging.getLogger(__name__)


class GnuCpLnMv(Parser):
    filename_re = os_ext.Unix.get_program_path_re("cp", "ln", "mv")

    priority = 7

    @staticmethod
    def add_arguments(arg_parser):
        pass

    @staticmethod
    def is_applicable(project=None, log_type=None):
        return True

    def __init__(self, context):
        self.context = context
        self.parser = ArgumentParserNoExit(prog="cp+ln+mv")
        self.parser.add_argument("-a", action="store_true", dest="archive")
        self.parser.add_argument("-f", action="store_true", dest="force")
        self.parser.add_argument("-s", action="store_true", dest="symbolic")
        self.parser.add_argument("infile")
        self.parser.add_argument("output")

    def parse(self, target):
        tokens = target.get("tokens")
        if not tokens:
            return target

        if not self.filename_re.match(tokens[0]):
            return target

        program = os.path.basename(tokens.pop(0))

        namespace = self.parser.parse_args(tokens)

        dependencies = []
        output_full = os.path.join(self.context.working_dir, namespace.output)
        output_full = self.context.platform.normalize_path(output_full)
        output = self.context.get_output(output_full)
        if not self.context.is_in_build_or_source_dir(output):
            logger.info(
                "Copy output not in build or source directory, ignoring: {}".format(
                    output
                )
            )
            return []
        if program == "ln" and namespace.symbolic:
            # infile is relative to output file
            namespace.infile = os.path.join(
                os.path.dirname(output_full), namespace.infile
            )
        source = self.context.get_file_arg(
            self.context.platform.normalize_path(namespace.infile), dependencies
        )

        return self.context.process_target_copy(source, output, dependencies) or []


__all__ = ["GnuCpLnMv"]
