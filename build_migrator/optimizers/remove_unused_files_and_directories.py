import logging
from build_migrator.helpers import get_target_and_dependencies
from build_migrator.modules import Optimizer


logger = logging.getLogger(__name__)


class RemoveUnusedFilesAndDirectories(Optimizer):
    priority = 0

    def optimize(self, targets):
        index = {}
        for t in targets:
            if "output" in t:
                index[t["output"]] = t
            for o in t.get("msvc_import_lib") or []:
                index[o] = t

        skip_set = set()
        for t in targets:
            if t["type"] not in ("directory", "file"):
                # force execution of yield'ing function
                list(get_target_and_dependencies(t, index, skip_set))

        optimized_targets = []
        for t in targets:
            if t["type"] in ("directory", "file"):
                if t["output"] not in skip_set and not t.get("top_level"):
                    continue
            optimized_targets.append(t)

        return optimized_targets


__all__ = ["RemoveUnusedFilesAndDirectories"]
