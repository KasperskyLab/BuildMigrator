import logging
from build_migrator.modules import Optimizer


logger = logging.getLogger(__name__)


class OrderTargetByDependency(Optimizer):
    def optimize(self, targets):
        output_index = {}
        order_index = {}
        for i in range(0, len(targets)):
            t = targets[i]
            if "output" in targets[i]:
                output_index[t["output"]] = t
                order_index[t["output"]] = i
            for o in t.get("msvc_import_lib") or []:
                output_index[o] = t
                order_index[o] = i

        # First, (stable) sort targets in order of dependency
        _targets_ready = set()
        _cycle_detector = set()
        i = 0
        while i < len(targets):
            deps = filter(order_index.get, targets[i].get("dependencies") or [])
            unordered_dependencies = []
            for d in deps:
                if d not in _targets_ready and d not in unordered_dependencies:
                    unordered_dependencies.append(d)
            if unordered_dependencies:
                unordered_dependencies = sorted(
                    unordered_dependencies, key=order_index.get, reverse=True
                )
                for d in unordered_dependencies:
                    pair = (targets[i].get("output"), d)
                    if pair in _cycle_detector:
                        logger.error("Cycle found: {}".format(pair))
                        _targets_ready.add(d)
                        continue
                    _cycle_detector.add(pair)
                    if d in output_index:
                        targets.remove(output_index[d])
                        targets.insert(i, output_index[d])
                    else:
                        _targets_ready.add(d)
            else:
                t = targets[i]
                if "output" in t:
                    _targets_ready.add(t["output"])
                for o in t.get("msvc_import_lib") or []:
                    _targets_ready.add(o)
                i += 1

        return targets


__all__ = ["OrderTargetByDependency"]
