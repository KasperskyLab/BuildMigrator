import argparse
import logging
from pprint import pformat
import traceback
from build_migrator.helpers import get_minified_targets
from build_migrator.modules import EntryPoint, Optimizer
from build_migrator.common.os_ext import get_host_system_name

logger = logging.getLogger(__name__)


class OptimizerContext(Optimizer, EntryPoint):
    @staticmethod
    def add_arguments(arg_parser):
        try:
            arg_parser.add_argument(
                "--platform",
                choices=["linux", "windows", "darwin"],
                help="Platform under which the build log was obtained. "
                "Mac and Linux builds can be parsed on any platform. "
                "Windows build logs can be parsed only on Windows. "
                "Default: current platform.",
            )
        except argparse.ArgumentError:
            # Already added somewhere else
            # TODO: make a better solution for cases when multiple extensions require the same argument
            pass
        arg_parser.add_argument(
            "--dont_optimize",
            action="store_true",
            help="Disable optimizations. Not recommended, "
            "some generators may produce unreadable results (cmake).",
        )

    def __init__(self, build_migrator, platform=None, dont_optimize=False):
        if platform is None:
            platform = get_host_system_name()
        self.dont_optimize = dont_optimize
        self.platform_name = platform

    def optimize(self, targets, optimizers):
        if self.dont_optimize:
            logger.debug("Skipping optimizations due to --dont_optimize flag")
            return targets

        logger.debug(" > Begin optimizing:")
        logger.debug(pformat(get_minified_targets(targets)))
        for optimizer in optimizers:
            logger.debug(type(optimizer).__name__)
            try:
                result = optimizer.optimize(targets)
                if result != targets:
                    logger.debug(" > Optimized:")
                    logger.debug(pformat(get_minified_targets(result)))
                targets = result
            except Exception:
                logging.error(traceback.format_exc())

        return targets


__all__ = ["OptimizerContext"]
