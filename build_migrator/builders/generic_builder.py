import argparse
import logging
import os
import shlex
import subprocess

from build_migrator.builders._log_providers.console import ConsoleLogProvider
from build_migrator.builders._log_providers.strace import StraceLogProvider
from build_migrator.modules import Builder, EntryPoint


logger = logging.getLogger(__name__)


class GenericBuilder(Builder, EntryPoint):
    _log_providers = {
        ConsoleLogProvider.NAME: ConsoleLogProvider,
        StraceLogProvider.NAME: StraceLogProvider,
    }
    _default_log_provider = ConsoleLogProvider.NAME

    @classmethod
    def _get_log_providers_help_msg(cls):
        msgs = [
            "{}: {}".format(name, obj.HELP) for name, obj in cls._log_providers.items()
        ]
        return ", ".join(msgs)

    @classmethod
    def add_arguments(cls, arg_parser):
        arg_parser.add_argument(
            "--build_command",
            metavar="COMMAND [WORKING_DIR] [LOG]",
            nargs="+",
            action="append",
            help='COMMAND should be given as one argument, i.e. "make mytarget". '
            "COMMAND supports subsitutions: {{source_dir}}, {{out_dir}}. "
            "WORKING_DIR is optional, default value is taken from --out_dir. "
            "LOG is the optional path to the log file produced by COMMAND. "
            "LOG accepts special values: \n{}\n".format(
                cls._get_log_providers_help_msg()
            )
            + "If no LOG is specified for any given COMMAND, default value ({}) ".format(
                cls._default_log_provider
            )
            + "is automatically set for the last given COMMAND. Default value can be "
            "changed using --log_provider argument.",
            dest="build_commands",
        )
        arg_parser.add_argument(
            "--log_provider",
            choices=list(cls._log_providers.keys()),
            help="Default LOG value for --build_command",
        )
        try:
            arg_parser.add_argument(
                "--source_dir",
                help="Source directory of the project that you want to migrate.",
                metavar="DIR",
            )
        except argparse.ArgumentError:
            # Already added somewhere else
            pass

    def _get_log_provider(self, provider):
        if provider in self._log_providers:
            if provider not in self._log_provider_instances:
                self._log_provider_instances[provider] = self._log_providers[provider](
                    self
                )
            provider = self._log_provider_instances[provider]
        return provider

    def __init__(
        self,
        build_migrator,
        out_dir,
        source_dir,
        build_commands=None,
        log_provider=None,
    ):
        if not build_commands:
            raise ValueError("build_commands must be specified")
        if log_provider is not None:
            self._default_log_provider = log_provider
        if os.stat(out_dir) == os.stat(source_dir):
            raise ValueError("out_dir cannot be the same as source_dir")

        self.build_migrator = build_migrator
        self.out_dir = os.path.abspath(out_dir)
        self.source_dir = os.path.abspath(source_dir)
        self._log_idx = 1
        self._log_provider_instances = {}

        self._build_commands = []
        explicit_log_provider = False
        for cmd in build_commands:
            log_provider = None
            working_dir = os.path.join(self.out_dir, '_build')
            if not isinstance(cmd, str):
                if len(cmd) > 3:
                    raise ValueError(
                        'Invalid --build_command: {}. NOTE: COMMAND should be passed as one argument (i.e. "make mytarget"). LOG and WORKING_DIR are optional.'.format(
                            cmd
                        )
                    )
                for value in cmd[1:]:
                    value = value.format(source_dir=self.source_dir, out_dir=self.out_dir)
                    if os.path.isdir(value):
                        working_dir = value
                    else:
                        _, ext = os.path.splitext(value)
                        if not ext:
                            logger.info("This doesn't look like a log path: %s", value)
                        log_provider = value
                cmd = cmd[0]
                if log_provider is not None:
                    explicit_log_provider = True
            cmd = cmd.format(source_dir=self.source_dir, out_dir=self.out_dir)
            self._build_commands.append(
                [
                    shlex.split(cmd, posix=False),
                    working_dir,
                    self._get_log_provider(log_provider),
                ]
            )

        if not explicit_log_provider:
            self._build_commands[-1][-1] = self._get_log_provider(
                self._default_log_provider
            )

    def call_and_return_log(self, args, cwd=None, **kwargs):
        log_path = os.path.join(
            self.out_dir, "build_command_" + str(self._log_idx) + ".log"
        )
        with open(log_path, "w") as f:
            logger.info(
                'Command: "%s", cwd: %r, log: %s', " ".join(args), cwd, log_path
            )
            subprocess.check_call(
                args, stdout=f, stderr=subprocess.STDOUT, cwd=cwd, **kwargs
            )
        self._log_idx += 1
        return log_path

    def build(self, builders=None):
        if builders:
            raise ValueError("GenericBuilder doesn't support extensions")
        logs = []
        build_dirs = []
        for args, cwd, log_provider in self._build_commands:
            if cwd and not os.path.exists(cwd):
                os.makedirs(cwd)
            if isinstance(log_provider, str) or log_provider is None:
                self.call_and_return_log(args, cwd=cwd)
            else:
                log_provider = log_provider.call_and_return_log(args, cwd=cwd)
            if log_provider is not None:
                logs.append(log_provider)
                if cwd:
                    build_dirs.append(cwd)
                logger.info("Added to parser queue: %s", log_provider)
        self.build_migrator.set_global_settings("logs", logs)
        if self.build_migrator.get_global_settings("build_dirs") is None:
            self.build_migrator.set_global_settings("build_dirs", build_dirs)


__all__ = ["GenericBuilder"]
