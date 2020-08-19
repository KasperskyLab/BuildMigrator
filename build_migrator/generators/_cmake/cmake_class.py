from __future__ import absolute_import

from .cmake_module import system_library_map
from build_migrator.helpers import flatten_list
from build_migrator.modules import Generator


class CMakeClass(Generator):
    priority = 1

    @staticmethod
    def add_arguments(arg_parser):
        pass

    def __init__(self, context, platform=None):
        self.context = context
        self.platform = platform
        self.handlers = {
            "compile_flags": self._compile_flags,
            "include_dirs": self._include_dirs,
            "link_flags": self._link_flags,
            "libs": self._libs,
            "c_flags": self._language_flags,
            "cxx_flags": self._language_flags,
            "gasm_flags": self._language_flags,
            "masm_flags": self._language_flags,
            "nasm_flags": self._language_flags,
            "rc_flags": self._language_flags,
            "yasm_flags": self._language_flags,
            "c_include_dirs": self._language_include_dirs,
            "cxx_include_dirs": self._language_include_dirs,
            "gasm_include_dirs": self._language_include_dirs,
            "masm_include_dirs": self._language_include_dirs,
            "nasm_include_dirs": self._language_include_dirs,
            "rc_include_dirs": self._language_include_dirs,
            "yasm_include_dirs": self._language_include_dirs,
        }
        self.language_flag_properties = self.context.language_flag_properties
        self.language_include_properties = self.context.language_include_properties

    def _compile_flags(self, f, property, values, conditions):
        assert not conditions
        if values:
            values = self.context.process_compile_flags(values)
            s = self.context.format_call("add_compile_options", [], values)
            f.write(s)

    def _include_dirs(self, f, property, values, conditions):
        assert not conditions
        if values:
            s = self.context.format_call("include_directories", [], values)
            f.write(s)

    def _link_flags(self, f, property, values, conditions):
        if not values:
            return

        if not conditions:
            if self.context.platform == "windows":
                functions = ["add_link_options", "static_library_options"]
            else:
                functions = ["add_link_options"]
        elif conditions == {"module_type": "static_lib"}:
            functions = ["static_library_options"]
        elif conditions == {"module_type": "shared_lib"}:
            functions = ["shared_link_options"]
        elif conditions == {"module_type": "executable"}:
            functions = ["executable_link_options"]
        else:
            assert False, conditions

        for function in functions:
            s = self.context.format_call(function, [], values)
            f.write(s)

    def _libs(self, f, property, values, conditions):
        assert not conditions
        if not values:
            return

        # remove extension
        values = [x[:-4] if x.endswith(".lib") else x for x in values]
        # map to CMake-specific (or empty) names
        values = [system_library_map.get(x, x) for x in values]
        # skip empty
        values = [x for x in values if x]

        if not values:
            return

        s = self.context.format_call("link_libraries", [], values)
        f.write(s)

    def _language_flags(self, f, property, values, conditions):
        assert not conditions
        if not values:
            return
        language = self.language_flag_properties.get(property)
        if language:
            values = self.context.process_compile_flags(values)
            s = self.context.format_call("language_compile_options", [language], values)
        else:
            assert False, property
        f.write(s)

    def _language_include_dirs(self, f, property, values, conditions):
        assert not conditions
        if not values:
            return
        language = self.language_include_properties.get(property)
        if language:
            s = self.context.format_call(
                "language_include_directories", [language], values
            )
        else:
            assert False, property
        f.write(s)

    _flag_priority = {
        "compile_flags": 0,
        "include_dirs": 0,
        "link_flags": 4,
        "libs": 5,
    }

    @classmethod
    def property_sort_key(cls, p):
        # first compile_flags and include_dirs, then all the rest
        # alphabetically, then link_flags and libs
        return (cls._flag_priority.get(p[0], 1), p[0])

    def generate(self, target):
        if target["type"] != "class":
            return False

        with self.context.open("CMakeLists.txt", "a") as f:
            for name, values in sorted(
                target["properties"].items(), key=self.property_sort_key
            ):
                self.handlers[name](f, name, flatten_list(values), target["conditions"])

            return True


__all__ = ["CMakeClass"]
