import fnmatch


class WildcardMatcher(object):
    # Pattern syntax:
    # *.cpp => matches a/b/file.cpp
    # *b*.* => matches a/b/c.d
    # !*.d  => does not match a/b/c.d
    # Matching is case-insensitive
    def __init__(self, patterns):
        self._negative = []
        self._positive = []
        for p in patterns:
            if p.startswith("!"):
                self._negative.append(p[1:].lower())
            else:
                self._positive.append(p.lower())

    def match(self, s):
        s = s.lower()
        for n in self._negative:
            if fnmatch.fnmatch(s, n):
                return False

        for p in self._positive:
            if fnmatch.fnmatch(s, p):
                return True

        if self._positive:
            return False

        if self._negative:
            return True

        return False
