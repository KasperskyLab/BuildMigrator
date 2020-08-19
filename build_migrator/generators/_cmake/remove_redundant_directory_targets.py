from build_migrator.modules import Generator


# configure_file(... ${DIR}/1/2/3/out.txt) creates ${DIR}/1/2/3 directory
# Which means:
# Target with 'type': 'directory' should be removed if there already exists
# target with 'type': 'file' that creates that directory.
class CMakeRemoveRedundantDirectoryTargets(Generator):
    priority = 0

    def __init__(self, context):
        self.context = context

    def _create_search_tree(self):
        return {}

    def _add_to_search_tree(self, tree, path):
        for leaf in path.split("/"):
            if leaf not in tree:
                tree[leaf] = {}
            tree = tree[leaf]

    def _search_tree_lookup(self, tree, path):
        for leaf in path.split("/"):
            if leaf not in tree:
                return False
            tree = tree[leaf]
        return True

    def _get_directories_created_by_file(self, output):
        accumulator = ""
        results = []
        for leaf in output.split("/")[:-1]:
            if accumulator:
                accumulator += "/"
            accumulator += leaf
            results.append(accumulator)
        return results

    def optimize(self, targets):
        tree = self._create_search_tree()
        index = {}
        for t in targets:
            if t["type"] != "file":
                continue
            self._add_to_search_tree(tree, t["output"])
            for output in self._get_directories_created_by_file(t["output"]):
                index[output] = t["output"]

        for t in targets:
            if t["type"] == "directory" and not t.get("top_level"):
                if self._search_tree_lookup(tree, t["output"]):
                    t["skip"] = True
                    dependencies = t.get("dependencies") or []
                    dependencies.append(index[t["output"]])
                    t["dependencies"] = dependencies

        return targets


__all__ = ["CMakeRemoveRedundantDirectoryTargets"]
