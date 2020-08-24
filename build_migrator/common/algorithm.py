from copy import deepcopy

try:
    # Python 3
    from collections.abc import Hashable, Iterable
except ImportError:
    # Python 2
    from collections import Hashable, Iterable


# Explanation by example:
# A = 1 2 3 4 5
# B = 2 3 4 5
#
# Optimized:
# common_set C = 2 3 4 5 (+4)
# A = 1 C (-3)
# B = C (-3)
# Shaved off 2 items, hence fitness = 2
def fitness_by_set_length(candidate, sets):
    return len(sets) * (len(candidate) - 1) - len(candidate)


# Explanation by example:
# A = abc def 1234567890
# B = abc def
# C = 1234567890
#
# Optimized 1:
# common_set (D): 1234567890 (+10)
# A = abc def D (-9)
# B = abc def
# C = D (-9)
# Shaved off 9 characters, hence fitness = 9
#
# Optimized 2:
# common_set (E): abc def (+6)
# A = E 1234567890 (-5)
# B = E (-5)
# C = 1234567890
# Shaved off 4 characters, hence fitness = 4
#
# Best common_set is D (maximum fitness)
class FitnessByTotalStringLength(object):
    def __init__(self, placeholder_length=1):
        self._placeholder_length = placeholder_length

    def __call__(self, candidate, sets):
        candidate_length = sum([len(s) for s in candidate])
        return (
            len(sets) * (candidate_length - self._placeholder_length) - candidate_length
        )


# TODO: describe algorithm?
# Best case compexity: len(union(sets)) * len(sets)
# Worst case compexity: len(union(sets)) ^ 2 * len(sets)
def find_best_common_set(sets, fitness_func=None):
    if fitness_func is None:
        fitness_func = fitness_by_set_length
    sets_with_value = {}
    for set_ in sets:
        for value in set_:
            if value not in sets_with_value:
                sets_with_value[value] = [set_]
            else:
                sets_with_value[value].append(set_)

    common_set = None
    fitness = 0
    for value, sets_ in sorted(
        sets_with_value.items(), key=lambda kv: len(kv[1]), reverse=True
    ):
        candidate_set = set.intersection(*sets_)
        candidate_fitness = fitness_func(candidate_set, sets_)
        if common_set is None or candidate_fitness > fitness:
            common_set = candidate_set
            fitness = candidate_fitness
        if fitness >= fitness_func(sets_with_value.keys(), sets_):
            # next iterations won't reach better fitness
            break

    return common_set, fitness


def join_nested_lists(flags, delim=" "):
    for idx, f in enumerate(flags):
        if isinstance(f, list):
            flags[idx] = delim.join(f)
    return flags


def flatten_list(lst):
    result = []
    for elem in lst:
        if isinstance(elem, list):
            result.extend(flatten_list(elem))
        else:
            result.append(elem)
    return result


# Replaces lists with tuples
def make_hashable(v):
    if isinstance(v, Hashable):
        return v
    if isinstance(v, Iterable):
        return tuple([make_hashable(i) for i in v])
    raise ValueError("Unsupported type: %r", type(v))


def add_unique_stable(l1, *l2):
    seen = set(make_hashable(l1))
    for x in l2:
        hashable_x = make_hashable(x)
        if not (hashable_x in seen or seen.add(hashable_x)):
            l1.append(x)
    return deepcopy(l1)


def add_unique_stable_by_key(l1, key, *l2):
    seen = set([x[key] for x in l1])
    for x in l2:
        if x[key] not in seen:
            seen.add(x[key])
            l1.append(x)
    return deepcopy(l1)


def intersect_unique_stable(*lists):
    lists = list(lists)
    while len(lists) > 1:
        tmp = list()
        for x in lists[0]:
            if (x not in tmp) and (x in lists[1]):
                tmp.append(x)
        lists[0:2] = [tmp]

    return deepcopy(lists[0]) if len(lists) == 1 else None


def get_subdict(dictionary, *keys):
    return {key: dictionary[key] for key in set(dictionary.keys()) & set(keys)}
