import logging
import re

from build_migrator.helpers import get_command_target
from build_migrator.common.os_ext import get_platform
from build_migrator.common.argument_parser_ex import ArgumentParserEx
from .base.parser_base import ParserBase


logger = logging.getLogger(__name__)


class Objcopy(ParserBase):
    def __init__(self, context):
        ParserBase.__init__(self, context)

        self.platform = context.platform
        self.program_re = self.platform.get_program_path_re("objcopy")

        # https://sourceware.org/binutils/docs/binutils/objcopy.html
        self.parser = ArgumentParserEx()
        self.parser.set(dest=None, raw_dest="args")
        self.parser.add_argument(
            "--redefine-syms", raw_handler=self.input_file_after_equals_sign
        )
        self.parser.add_argument(
            "--keep-symbols", raw_handler=self.input_file_after_equals_sign
        )
        self.parser.add_argument(
            "--strip-symbols", raw_handler=self.input_file_after_equals_sign
        )
        self.parser.add_argument(
            "--strip-unneeded-symbols", raw_handler=self.input_file_after_equals_sign
        )
        self.parser.add_argument(
            "--keep-global-symbols", raw_handler=self.input_file_after_equals_sign
        )
        self.parser.add_argument(
            "--keep-global-symbols", raw_handler=self.input_file_after_equals_sign
        )
        self.parser.add_argument(
            "--localize-symbols", raw_handler=self.input_file_after_equals_sign
        )
        self.parser.add_argument(
            "--globalize-symbols", raw_handler=self.input_file_after_equals_sign
        )
        self.parser.add_argument(
            "--weaken-symbols", raw_handler=self.input_file_after_equals_sign
        )
        obj_re = re.compile(r"^[^-=+:]+$")
        self.parser.add_argument(
            "infile", dest="infile", raw_handler=self.input_file, args_regexp=obj_re
        )
        self.parser.add_argument(
            "outfile",
            dest="outfile",
            nargs="?",
            raw_handler=self.output_file,
            args_regexp=obj_re,
        )

    def parse(self, target):
        tokens = target.get("tokens") or []
        if not tokens:
            return target

        if not self.program_re.match(tokens[0]):
            return target

        tokens.pop(0)
        namespace, _ = self.parser.parse_known_args(tokens, unknown_dest="args")
        inplace = False
        if namespace.outfile:
            if namespace.outfile[0] == namespace.infile:
                inplace = True
        else:
            inplace = True
        if inplace:
            namespace.infile = self.context.get_file_arg(namespace.infile)
            infile_target = self.context.target_index.get(namespace.infile)
            if infile_target and infile_target["type"] == "module":
                if infile_target.get("post_build_commands") is None:
                    infile_target["post_build_commands"] = []
                infile_target["post_build_commands"].append(
                    {"program": "objcopy", "args": namespace.args}
                )
                infile_target["dependencies"].extend(namespace.dependencies)
                infile_target["dependencies"].remove(infile_target["output"])
                _, dependencies = self.context.split_target_dependencies(infile_target)
                for dep_target in dependencies:
                    self.context.register_target(dep_target)
                return []
        return get_command_target(
            None,
            program="objcopy",
            args=namespace.args,
            output=namespace.output,
            dependencies=namespace.dependencies,
        )


__all__ = ["Objcopy"]
