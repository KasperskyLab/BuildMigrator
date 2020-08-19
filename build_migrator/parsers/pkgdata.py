import logging
import os
from build_migrator.helpers import get_command_target, get_copy_target
from build_migrator.common.os_ext import get_platform, Windows
from build_migrator.common.argument_parser_ex import ArgumentParserEx
from .base.parser_base import ParserBase


logger = logging.getLogger(__name__)


class Pkgdata(ParserBase):
    # Should be lower than MsvcRc (because we expect that rc target should present)
    priority = 7.1

    def __init__(self, context, platform=None):
        ParserBase.__init__(self, context)

        self.platform = get_platform(platform)
        self.program_re = self.platform.get_program_path_re("pkgdata")

        # https://helpmanual.io/help/icupkg/
        self.parser = ArgumentParserEx()
        self.parser.set(raw_dest="args")
        self.parser.add_argument("--name", "-p")
        self.parser.add_argument("--bldopt", "-O", raw_handler=self.input_file)
        self.parser.add_argument(
            "--mode",
            "-m",
            choices=["files", "dll", "library", "common", "archive", "static"],
        )
        self.parser.add_argument("--verbose", "-v", action="store_true")
        self.parser.add_argument("--copyright", "-c", action="store_true")
        self.parser.add_argument("--comment", "-C", action="store_true")
        self.parser.add_argument("--destdir", "-d", raw_handler=self.input_dir)
        self.parser.add_argument("--rebuild", "-F", action="store_true")
        self.parser.add_argument("--tempdir", "-T", raw_handler=self.input_dir)
        self.parser.add_argument("--install", "-I")
        self.parser.add_argument("--sourcedir", "-s", raw_handler=self.input_dir)
        self.parser.add_argument("--entrypoint", "-e")
        self.parser.add_argument("--revision", "-r")
        self.parser.add_argument("--force-prefix", "-f")
        self.parser.add_argument("--libname", "-L")
        self.parser.add_argument("--quiet", "-q", action="store_true")
        self.parser.add_argument("--without-assembly", "-w", action="store_true")
        self.parser.add_argument("--zos-pds-build", "-z", action="store_true")
        self.parser.add_argument("packageFile", raw_handler=self.input_file)

    def parse(self, target):
        tokens = target.get("tokens") or []
        if not tokens:
            return target

        if not self.program_re.match(tokens[0]):
            return target

        tokens.pop(0)
        namespace = self.parser.parse_args(tokens)
        create_symlinks = False
        base_target_name = None
        main_target_name = None
        if namespace.name is not None and namespace.libname is None:
            namespace.libname = namespace.name
        if namespace.mode in ["dll", "library"]:
            output = self.platform.get_library_filenames(
                namespace.libname,
                shared=True,
                static=False,
                revision=namespace.revision,
            )
            base_target_name = self.platform.parse_shared_lib(output[0])["target_name"]
            main_target_name = base_target_name
            if namespace.revision:
                if self.platform != Windows:
                    create_symlinks = True
                else:
                    idx = -len(self.platform.shared_lib_ext)
                    # add revision to .dll only
                    output[0] = output[0][:idx] + namespace.revision + output[0][idx:]
                main_target_name += "." + namespace.revision

            if self.platform == Windows:
                rc_output_filename = os.path.join(namespace.tempdir, "icudata.res")
                rc_target = self.context.find_target_by_path(rc_output_filename)
                namespace.dependencies.append(rc_target["output"])
        elif namespace.mode in ["static"]:
            prefix = ""
            if self.platform == Windows and namespace.libname[0] != "s":
                prefix = "s"
            output = self.platform.get_library_filenames(
                prefix + namespace.libname, shared=False, static=True
            )
            base_target_name = self.platform.parse_static_lib(output[0])["target_name"]
            main_target_name = base_target_name
        else:
            output = [namespace.name + ".dat"]

        for idx, o in enumerate(output):
            o = output[idx]
            o = os.path.join(namespace.destdir, o)
            o = self.context.get_output(
                self.context.normalize_path(o), namespace.dependencies
            )
            output[idx] = o

        symlink_targets = []
        if create_symlinks:
            major = namespace.revision.split(".")[0]
            for rev in [major, None]:
                destination = self.platform.get_library_filenames(
                    namespace.libname, shared=True, static=False, revision=rev
                )[0]
                destination = os.path.join(namespace.destdir, destination)
                dependencies = [output[0]]
                destination = self.context.get_output(
                    self.context.normalize_path(destination), dependencies
                )
                name = base_target_name
                if rev:
                    name += "." + rev
                symlink_targets.append(
                    get_copy_target(
                        name, output[0], destination, dependencies=dependencies
                    )
                )
        self.platform.get_library_filenames
        target = get_command_target(
            main_target_name, "pkgdata", namespace.args, output, namespace.dependencies
        )
        return [target] + symlink_targets


__all__ = ["Pkgdata"]
