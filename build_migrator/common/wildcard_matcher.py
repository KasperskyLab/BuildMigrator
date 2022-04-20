import fnmatch
import re


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
                re_str = fnmatch.translate(p[1:].lower())
                self._negative.append(re.compile(re_str))
            else:
                re_str = fnmatch.translate(p.lower())
                self._positive.append(re.compile(re_str))

    def match(self, s):
        s = s.lower()
        for n in self._negative:
            if n.match(s):
                return False

        for p in self._positive:
            if p.match(s):
                return True

        if self._positive:
            return False

        if self._negative:
            return True

        return False
