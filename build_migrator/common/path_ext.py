import os


def closest_dir(path, dirs=None, max_relpath_level=-1, cwd=os.curdir):
    if dirs is None:
        dirs = []
    path = os.path.join(cwd, path)
    result = None
    for dir in dirs:
        try:
            relpath = os.path.relpath(path, os.path.join(cwd, dir))
        except ValueError:
            # path is on mount 'c:', start on mount 'd:'
            continue
        if max_relpath_level >= 0 and relpath_level(relpath) > max_relpath_level:
            continue
        if not result or len(relpath) < len(result[1]):
            result = (dir, relpath)

    return result


# count '../' at the beginning of path
def relpath_level(path):
    level = 0
    idx = 0
    while path[idx:].startswith(".."):
        level += 1
        idx += 3

    return level
