from copy import deepcopy
from itertools import chain
from build_migrator.helpers import (
    get_class_target,
    get_source_with_inherited_flags,
    get_variable_target,
)
from build_migrator.modules import Optimizer
from build_migrator.common.algorithm import (
    add_unique_stable,
    find_best_common_set,
    intersect_unique_stable,
    FitnessByTotalStringLength,
    make_hashable,
)
from build_migrator.parsers.build_log_parser import (
    BuildLogParserContext as ParserContext,
)


# Warning for CMake:
# Optimized CMakeLists.txt may not represent actual compilation
# flags when building generated Visual Studio solution. This is
# due to MSBuild / VS pecularities and CMake bugs.
# If your CMakeLists.txt uses sources in multiple languages aside
# from C/C++, or if C and C++ sources may require different
# compilations flags, it's best to avoid building with Visual Studio.
# Ninja is recommended for cross-platform projects, or Unix Makefiles
# for Unix-only projects.
#
# However, there's a bug in CMake's RC implementation for Ninja:
# No matter which RC flags are set via *_compile_options($<$<COMPILE_LANGUAGE:RC>:flags>),
# only common_optimization_definitions (-D*) are passed to the actual compiler. We can
# work around that by setting CMAKE_RC_FLAGS, but it's better
# to wait for a fix, as RC rarely needs any flags at all.
#
# TODO: provide links to examples and CMake issues
class GroupCommonFlagsV2(Optimizer):
    priority = 5
    
    _predefined_variables = [
        ParserContext.build_dir_placeholder,
        ParserContext.source_dir_placeholder
    ]

    @staticmethod
    def add_arguments(arg_parser):
        arg_parser.add_argument(
            "--aggressive_optimization",
            action="store_true",
            help="Enable aggressive optimizations. This may greatly decrease "
            "resulting CMakeLists.txt size at the expense of its readability.",
        )
        arg_parser.add_argument(
            "--class_optimization_threshold",
            type=int,
            help="Move common flags and options to global scope "
            "if amount of targets is greater than given value",
        )
    
    @staticmethod
    def _is_predefined_variable(flag):
        for predefined_var in GroupCommonFlagsV2._predefined_variables:
            if flag.startswith(predefined_var):
                return True
        return False

    # TODO: keep 'platform' value inside targets?
    def __init__(
        self,
        context,
        flag_optimizer_ver=None,
        aggressive_optimization=None,
        class_optimization_threshold=None,
        generators=None,
    ):
        if generators is None:
            generators = []
        self.bazel_mode = len(generators) > 0 and "bazel" in generators[0]
        if flag_optimizer_ver is not None:
            flag_optimizer_ver = int(flag_optimizer_ver)
        self.is_disabled = flag_optimizer_ver != 2 and not self.bazel_mode
        if self.is_disabled:
            return
        self.platform = context.platform_name
        self.aggressive_optimization = aggressive_optimization
        self.class_optimization_threshold = class_optimization_threshold

    @staticmethod
    def _remove_property_values(targets, property, values):
        for t in targets:
            if t.get("type") == "class":
                t = t["properties"]
            if property not in t:
                continue
            for v in values:
                while v in t[property]:
                    t[property].remove(v)

    @staticmethod
    def _move_common_flags_to_target(
        target,
        target_dependencies,
        source_targets,
        property,
        target_property=None,
        flag_filter=None,
        source_filter=None,
        threshold=None,
    ):
        if threshold is None:
            threshold = 2
        if target_property is None:
            target_property = property
        source_targets = [
            c for c in source_targets if source_filter is None or source_filter(c)
        ]
        if len(source_targets) < threshold:
            # skip if optimization threshold isn't reached
            return None
        common_flags = intersect_unique_stable(
            *[src[property] for src in source_targets]
        )
        if common_flags is None:
            return None

        for flag in common_flags:
            if not isinstance(flag, list):
                # Sometimes flag may be list of subflag,
                # so we generate list of flags for most common case
                flag = [flag]
                for subflag in flag:
                    if GroupCommonFlagsV2._is_predefined_variable(subflag):
                        continue
                    if subflag.startswith("@"):
                        variable_name = subflag[:subflag.find("@", 1) + 1]
                        target_dependencies.append(variable_name)

        if target_property not in target:
            target[target_property] = []
        if flag_filter:
            common_flags = [f for f in common_flags if flag_filter(f)]
        add_unique_stable(target[target_property], *common_flags)
        for src in source_targets:
            src[property] = [f for f in src[property] if f not in common_flags]
        return common_flags

    class DefaultSourceFilter(object):
        def __init__(self, source_language):
            self.source_language = source_language

        def __call__(self, source_reference):
            return source_reference["language"] == self.source_language

    def optimize(self, targets):
        if self.is_disabled:
            return targets

        module_target_index = {}
        variable_target_index = {}
        targets = deepcopy(targets)
        linkable_targets = []
        nonstatic_linkable_targets = []
        for t in targets:
            if t["type"] == "variable":
                variable_target_index[t["output"]] = t
            if t["type"].startswith("module"):
                module_target_index[t["output"]] = t
            if t["type"] == "module":
                for o in t.get("msvc_import_lib") or []:
                    module_target_index[o] = t
                if (
                    t["module_type"] == "object_lib"
                    or t["module_type"] == "static_lib"
                    and self.platform != "windows"
                ):
                    # Target link flags can be ignored if:
                    # 1. target is an OBJECT library
                    # 2. target is a STATIC library assembled with 'ar'
                    t["link_flags"] = []
                    continue
                linkable_targets.append(t)
                if t["module_type"] != "static_lib":
                    nonstatic_linkable_targets.append(t)

        compileable_targets = []
        compileable_sources = []
        sources_by_target = {}
        target_by_source = {}
        for t in targets:
            if t["type"] == "module":
                compileable_targets.append(t)
                sources_by_target[t["output"]] = []
                for s in t["sources"]:
                    if s.get("language") is not None:
                        sources_by_target[t["output"]].append(s)
                        compileable_sources.append(s)
                        # One source file may compile under multiple targets
                        # with different flags. Distinguish such instances by
                        # a temporary identifier.
                        s["_id"] = len(compileable_sources)
                        target_by_source[s["_id"]] = t
                if not sources_by_target[t["output"]]:
                    # Ignore target compilation flags and include dirs if:
                    # * Target has no compileable sources (only object files, .def files, .manifests etc)
                    t["compile_flags"] = []

        src_copies_with_target_flags = []
        for t in compileable_targets:
            for s in sources_by_target[t["output"]]:
                s = get_source_with_inherited_flags(t, s)
                src_copies_with_target_flags.append(s)

        # Optimization is achieved by moving common flags to upper scope levels (examples in CMake):
        # * Global compiler flags for all languages: add_compile_options(flags)
        # * Global include directories for all languages: include_directories(dirs)
        # * Global link flags:
        #                     foreach(type EXE STATIC SHARED)
        #                         string(APPEND CMAKE_${type}_LINKER_FLAGS flags)
        #                     endforeach() [CMake < v3.13] or
        #                     add_link_options(flags) [CMake >= v3.13]
        # * Global link libraries:
        #                     link_libraries(libs)
        # * Global compiler flags for specific language:
        #                     add_compile_options($<$<COMPILE_LANGUAGE:xxx>:flags>)
        # * Global include directories for specific language:
        #                     include_directories($<$<COMPILE_LANGUAGE:xxx>:dirs>)
        # * Global static link flags:
        #                     string(APPEND CMAKE_STATIC_LINKER_FLAGS) [CMake < v3.13] or
        #                     add_link_options($<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,STATIC_LIBRARY>:flags>) [CMake >= v3.13]
        # * Global shared link flags:
        #                     string(APPEND CMAKE_SHARED_LINKER_FLAGS) [CMake < v3.13] or
        #                     add_link_options($<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:flags>) [CMake >= v3.13]
        # * Global exe link flags:
        #                     string(APPEND CMAKE_EXE_LINKER_FLAGS) [CMake < v3.13] or
        #                     add_link_options($<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:flags>) [CMake >= v3.13]
        # * Variables for some subset of source / target flags:
        #                     set(VARIABLE_NAME flags)
        #                     target_compile_options(target_name PRIVATE flags ${VARIABLE_NAME} flags) or
        #                     set_source_files_properties(file COMPILE_OPTIONS ${VARIABLE_NAME} flags)
        # * Target link flags:
        #                     set_target_properties(target PROPERTIES LINK_FLAGS "flags") [CMake < v3.13] or
        #                     target_link_options(flags) [CMake >= v3.13]
        # * Target compile flags for all languages: target_compile_options(flags)
        # * Target include dirs for all languages: target_include_directories(dirs)
        # * Target compile flags for specific language:
        #                     target_compile_options($<$<COMPILE_LANGUAGE:xxx>:flags>)
        # * Target include dirs for specific language:
        #                     target_include_directories($<$<COMPILE_LANGUAGE:xxx>:dirs>)
        # * Source compile flags: set_source_files_properties(COMPILE_OPTIONS flags)
        # * Source include dirs: set_source_files_properties(INCLUDE_DIRECTORIES dirs)
        #
        # Global scope is most optimal, source scope is least optimal.
        #
        # Global scope flags are expressed via 'class' targets:
        # - type: class
        #   properties:
        #     <property 1>: <a>
        #     <property 2>: [<b>, <c>]
        #   conditions:
        #     - <required property 1>: [<acceptable values>]
        #     - <required property 2>: <acceptable value>
        # If target contains all required properties (found in 'conditions')
        # and each property value is found in corresponding acceptable values, then
        # target inherits class' properties. Conditions may be empty, meaning that
        # class applies to all targets.
        # If a target changes single-value property inherited from class, inherited value
        # is overridden.
        # If a target changes inherited list property, target's values are appended at the
        # end of inherited values.
        # If a target inherits multiple classes and some classes set the same property, then
        # the last (by occurence in target list) class overrides single-value property,
        # or appends to a list property.
        # Some classes which are easily implemented in CMake (see examples above) may not
        # be possible in other build systems (and vice versa). Thus, the optimization
        # routines below must be reviewed and modified for each newly supported generator.

        # TODO: Don't do optimizations in predefined order, pick best
        #       optimization iteratively? Or maybe pick best optimization
        #       path dynamically to avoid greedy algorithm inoptimality?
        #       (it's probably an NP problem)

        # In general, we cannot merge same compilations flags from different languages
        # into global or target scope because they may mean different things. So, by
        # default we only merge definitions (-D).
        # However, it can be allowed for some combination of languages without introducing
        # too much confusion.
        only_definitions_in_global_scope = not self._is_safe_to_merge_nondefinitions(
            compileable_sources
        )

        # We currently cannot move YASM-only include dirs
        # (as opposed to include dirs that are common between YASM
        # and other languages) higher than source-level scope.
        # That's because the only way to do that is to use
        # include_directories() together with COMPILE_LANGUAGE
        # generator expression, but COMPILE_LANGUAGE doesn't
        # support custom languages.
        common_optimization_definitions = [
            ("compile_flags", None, "compile_flags"),
            ("include_dirs", None, "include_dirs"),
            ("c_flags", "C", "compile_flags"),
            # TODO: rename C++ to CXX (or CPP) for consistency?
            ("cxx_flags", "C++", "compile_flags"),
            ("gasm_flags", "GASM", "compile_flags"),
            ("nasm_flags", "NASM", "compile_flags"),
            ("yasm_flags", "YASM", "compile_flags"),
            ("masm_flags", "MASM", "compile_flags"),
            ("rc_flags", "RC", "compile_flags"),
            ("c_include_dirs", "C", "include_dirs"),
            ("cxx_include_dirs", "C++", "include_dirs"),
            ("gasm_include_dirs", "GASM", "include_dirs"),
            ("nasm_include_dirs", "NASM", "include_dirs"),
            ("masm_include_dirs", "MASM", "include_dirs"),
            ("rc_include_dirs", "RC", "include_dirs"),
        ]
        # Add global flags and include dirs to global class target
        class_targets = []
        if not self.bazel_mode:
            global_class = get_class_target("#global")
            for (
                target_property,
                source_language,
                source_property,
            ) in common_optimization_definitions:
                flag_filter = None
                source_filter = None
                if source_language is not None:
                    source_filter = self.DefaultSourceFilter(source_language)
                elif (
                    only_definitions_in_global_scope and source_property == "compile_flags"
                ):
                    flag_filter = self._definitions_only
                common_values = self._move_common_flags_to_target(
                    global_class["properties"],
                    global_class.setdefault("dependencies", []),
                    src_copies_with_target_flags,
                    source_property,
                    target_property=target_property,
                    source_filter=source_filter,
                    flag_filter=flag_filter,
                    threshold=self.class_optimization_threshold
                )
                if common_values is None:
                    continue
                self._remove_property_values(
                    compileable_targets, target_property, common_values
                )
                if target_property != source_property:
                    self._remove_property_values(
                        compileable_targets, source_property, common_values
                    )
                self._remove_property_values(
                    filter(source_filter, compileable_sources),
                    source_property,
                    common_values,
                )

            self._move_common_flags_to_target(
                global_class["properties"],
                global_class.setdefault("dependencies", []),
                linkable_targets,
                "link_flags",
                threshold=self.class_optimization_threshold
            )

            def lib_filter(flag):
                if isinstance(flag, str):
                    return flag not in module_target_index
                else:
                    return flag['value'] not in module_target_index

            self._move_common_flags_to_target(
                global_class["properties"],
                global_class.setdefault("dependencies", []),
                nonstatic_linkable_targets,
                "libs",
                flag_filter=lib_filter,
                threshold=self.class_optimization_threshold
            )

            for module_type in ["executable", "shared_lib", "static_lib"]:
                class_target = get_class_target(
                    "#" + module_type, conditions={"module_type": module_type}
                )
                self._move_common_flags_to_target(
                    class_target["properties"],
                    class_target.setdefault("dependencies", []),
                    filter(lambda t: t["module_type"] == module_type, linkable_targets),
                    "link_flags",
                    threshold=self.class_optimization_threshold
                )
                class_targets.append(class_target)

            class_targets.insert(0, global_class)

        # YASM sources are not natively supported by CMake and
        # current CMake design doesn't let us set target-wide
        # flags for custom languages without hacks.
        common_optimization_definitions = [
            d for d in common_optimization_definitions if not d[0].startswith("yasm")
        ]
        for t in compileable_targets:
            srcs = sources_by_target[t["output"]]
            for (
                target_property,
                source_language,
                source_property,
            ) in common_optimization_definitions:
                flag_filter = None
                source_filter = None
                if source_language is not None:
                    source_filter = self.DefaultSourceFilter(source_language)
                else:
                    if (
                        not self._is_safe_to_merge_nondefinitions(srcs)
                        and source_property == "compile_flags"
                    ):
                        flag_filter = self._definitions_only
                common_values = self._move_common_flags_to_target(
                    t,
                    t.setdefault("dependencies", []),
                    srcs,
                    source_property,
                    target_property=target_property,
                    source_filter=source_filter,
                    threshold=0 if self.bazel_mode else 1,
                    flag_filter=flag_filter,
                )

        variable_targets = []
        if not self.bazel_mode:

            # Aggressive optimizations: group leftover flags in
            # variables with not vague names like compile_flags_1,
            # compile_flags_2 etc.
            if self.aggressive_optimization:

                flag_props = [
                    "compile_flags",
                    "c_flags",
                    "cxx_flags",
                    "gasm_flags",
                    "masm_flags",
                    "nasm_flags",
                    "rc_flags",
                    "yasm_flags",
                ]
                include_props = [
                    "include_dirs",
                    "c_include_dirs",
                    "cxx_include_dirs",
                    "gasm_include_dirs",
                    "masm_include_dirs",
                    "nasm_include_dirs",
                    "rc_include_dirs",
                    "yasm_include_dirs",
                ]
                var_optimization_definitions = [
                    (
                        flag_props,
                        compileable_targets + compileable_sources + class_targets,
                        None,
                    ),
                    (
                        include_props,
                        compileable_targets + compileable_sources + class_targets,
                        None,
                    ),
                    (["link_flags"], compileable_targets + class_targets, None),
                    (["libs"], compileable_targets + class_targets, lib_filter),
                ]
                for properties, targets_, flag_filter in var_optimization_definitions:
                    increment = 1
                    flag_sets = []
                    for p in properties:
                        flag_sets.extend(
                            [
                                set(
                                    [
                                        make_hashable(f)
                                        for f in (self._get_property_values(t, p) or [])
                                        if flag_filter is None or flag_filter(f)
                                    ]
                                )
                                for t in targets_
                            ]
                        )
                    while flag_sets:
                        flags_length = sum(
                            [len(s) for s in set(chain.from_iterable(flag_sets))]
                        )
                        var_name = "{}_{}".format(properties[0], increment)
                        placeholder = "@{}@".format(var_name)
                        common_set, characters_saved = find_best_common_set(
                            flag_sets,
                            fitness_func=FitnessByTotalStringLength(len(placeholder)),
                        )
                        if characters_saved < 10:
                            break
                        ratio = float(characters_saved) / flags_length
                        # ensure that we save at least 5% text for current flag set
                        if ratio < 0.05:
                            break
                        flags = sorted(common_set, key=lambda f: f if isinstance(f, str) else " ".join(f))
                        dependencies = []
                        for f in flags:
                            if isinstance(f, str):
                                args = [f]
                            else:
                                args = f
                            for arg in args:
                                variable_name = arg
                                if arg.startswith("@") and not arg.endswith("@"):
                                    variable_name = arg[:arg.find("@", 1) + 1]
                                if variable_name in variable_target_index:
                                    dependencies.append(variable_name)
                        var_target = get_variable_target(
                            var_name, placeholder, flags, dependencies=dependencies
                        )
                        for idx, s in enumerate(flag_sets):
                            if common_set <= s:
                                s.difference_update(common_set)
                                t = targets_[idx % len(targets_)]
                                property = properties[idx // len(targets_)]
                                self._remove_property_values([t], property, common_set)
                                values = self._get_property_values(t, property)
                                values.insert(
                                    self._get_index_for_next_variable(values), placeholder
                                )
                                if "language" in t:
                                    # TODO: source objects should support dependencies
                                    #       add dependency to parent target
                                    t = target_by_source[t["_id"]]
                                if var_target["output"] not in t["dependencies"]:
                                    t["dependencies"].append(var_target["output"])
                        variable_targets.append(var_target)
                        variable_target_index[var_target["output"]] = var_target
                        increment += 1

        # Remove temp identifiers from sources
        for s in compileable_sources:
            del s["_id"]

        return variable_targets + class_targets + targets

    # get index of the first value that's not a variable
    @staticmethod
    def _get_index_for_next_variable(flags):
        for idx, f in enumerate(flags):
            if not isinstance(f, str):
                f = f[0]
            if not f.startswith("@"):
                return idx
        return len(flags)

    @staticmethod
    def _get_property_values(t, p):
        if t.get("type") == "class":
            return t["properties"].get(p)
        else:
            return t.get(p)

    @staticmethod
    def _definitions_only(f):
        return f.startswith("-D")

    def _is_safe_to_merge_nondefinitions(self, targets):
        if self.bazel_mode:
            return True
        languages = set([t["language"] for t in targets if "language" in t])
        if self.platform == "windows":
            # Allow merging all flags if only native VS languages are present
            return languages <= {"C", "C++", "MASM", "RC"}
        else:
            # Allow merging all flags if only native GCC languages are present
            return languages <= {"C", "C++", "GASM"}


__all__ = ["GroupCommonFlagsV2"]
