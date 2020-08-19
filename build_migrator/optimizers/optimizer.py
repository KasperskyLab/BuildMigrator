import logging
from pprint import pformat
import traceback
from build_migrator.helpers import get_minified_targets
from build_migrator.modules import EntryPoint, Optimizer

logger = logging.getLogger(__name__)


class OptimizerContext(Optimizer, EntryPoint):
    @staticmethod
    def add_arguments(arg_parser):
        arg_parser.add_argument(
            "--dont_optimize",
            action="store_true",
            help="Disable optimizations. Not recommended, "
            "some generators may produce unreadable results (cmake).",
        )

    def __init__(self, build_migrator, dont_optimize=False):
        self.dont_optimize = dont_optimize

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
