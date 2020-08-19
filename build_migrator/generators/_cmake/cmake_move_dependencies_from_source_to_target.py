from build_migrator.modules import Generator
from build_migrator.common.algorithm import add_unique_stable


# CMake doesn't support adding dependencies to source files,
# move source file dependencies to parent targets.
class CMakeMoveDependenciesFromSourceToTarget(Generator):
    priority = -1

    @staticmethod
    def add_arguments(arg_parser):
        pass

    def __init__(self, context):
        self.context = context

    def optimize(self, targets):
        for t in targets:
            for s in t.get("sources") or []:
                s_deps = s.get("dependencies")
                if s_deps:
                    t["dependencies"] = add_unique_stable(t["dependencies"], *s_deps)
                    del s["dependencies"]

        return targets


__all__ = ["CMakeMoveDependenciesFromSourceToTarget"]
