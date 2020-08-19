import logging
import os
from build_migrator.helpers import (
    get_module_target,
    get_source_file_reference,
    get_source_with_inherited_flags,
    language_to_flags_property,
    language_to_includes_property,
)
from build_migrator.modules import Generator
from build_migrator.parsers.build_log_parser import (
    BuildLogParserContext as ParserContext,
)


logger = logging.getLogger(__name__)


language_specific_properties = set(
    list(language_to_flags_property.values())
    + list(language_to_includes_property.values())
)


def source_object_to_string(target):
    return (
        target["path"]
        + " ".join(target["compile_flags"])
        + " ".join(["-I" + d for d in target["include_dirs"]])
    )


# Consider following build object model:
# - target1:
#       sources:
#       - path: a.cpp, flags: -DABC
#       - ...
# - target1:
#       sources:
#       - path: a.cpp, flags: -DDEF
#       - ...
#
# Without any modification it will result in following CMake output:
#   set_source_files_properties(a.cpp COMPILE_OPTIONS -DABC)
#   set_source_files_properties(... COMPILE_OPTIONS -DABC)
#   add_executable(target1 a.cpp ...)
#   set_source_files_properties(a.cpp COMPILE_OPTIONS -DDEF)
#   set_source_files_properties(... COMPILE_OPTIONS -DDEF)
#   add_executable(target2 a.cpp ...)
#
# The problem with such code is that second set_source_files_properties call
# overrides a.cpp COMPILE_OPTIONS for target1, not just target2.
#
# Case A: not all source files inside target1 and target2 use the same set of flags:
#   add_library(temp1 OBJECT a.cpp)
#   set_target_property(temp1 COMPILE_OPTIONS -DABC)
#   add_library(... OBJECT ...)
#   set_target_property(... COMPILE_OPTIONS -DABC)
#   add_executable(target1 $<TARGET_OBJECTS:temp1> ...)
#   add_library(temp2 OBJECT a.cpp)
#   set_target_property(temp2 COMPILE_OPTIONS -DDEF)
#   add_library(... OBJECT ...)
#   set_target_property(... COMPILE_OPTIONS -DDEF)
#   add_executable(target2 $<TARGET_OBJECTS:temp2> ...)
#
# Case B: all source files in target1/2 use the same flags:
#   add_executable(target1 a.cpp ...)
#   set_target_property(target1 COMPILE_OPTIONS -DABC)
#   add_executable(target2 a.cpp ...)
#   set_target_property(target2 COMPILE_OPTIONS -DDEF)
#
# This optimizer modifies build object model to produce correct CMake output for case A
class CMakeFixMultipleSourceInstancesWithDifferentFlags(Generator):
    priority = -2
    compile_flags_placeholder = "@compile_flags@"
    include_dirs_placeholder = "@include_dirs@"

    def __init__(self, context):
        self.context = context

    def optimize(self, targets):
        source_index = {}
        pending_sources = set()
        module_targets = []
        for idx, target in enumerate(targets):
            if target["type"] == "module":
                module_targets.append((idx, target))
                for source in target["sources"]:
                    path = source["path"]
                    if path in source_index:
                        s1 = source
                        s2 = source_index[path]
                        if (
                            s1["compile_flags"] != s2["compile_flags"]
                            or s1["include_dirs"] != s2["include_dirs"]
                        ):
                            pending_sources.add(path)
                    else:
                        source_index[path] = source

        if not pending_sources:
            return targets

        logger.debug(
            "Creating object libraries for each source file instance: %r"
            % pending_sources
        )

        object_targets = []
        # source + flags => object_target
        # this index is needed to avoid making duplicate object targets
        object_target_index = {}
        counter = {}
        for idx, target in module_targets:
            if len(target["sources"]) == 0:
                continue
            sources = [s for s in target["sources"] if s["path"] not in pending_sources]
            remaining = [s for s in target["sources"] if s["path"] in pending_sources]
            target["sources"] = sources
            target_output_dir = os.path.dirname(target["output"])
            for source in remaining:
                source = get_source_with_inherited_flags(target, source)
                key = source_object_to_string(source)
                if key in object_target_index:
                    object_target_output = object_target_index[key]["output"]
                else:
                    path = source["path"]
                    number = counter.get(path, 0) + 1
                    counter[path] = number
                    object_target_name = path.replace(
                        ParserContext.build_dir_placeholder + "/", ""
                    )
                    object_target_name = object_target_name.replace(
                        ParserContext.source_dir_placeholder + "/", ""
                    )
                    object_target_name = (
                        object_target_name.replace("/", "_").replace(".", "_").lower()
                    )
                    object_target_name += "_" + str(number)
                    object_target_output = (
                        target_output_dir + "/" + object_target_name + ".o"
                    )
                    object_target = get_module_target(
                        "object_lib",
                        object_target_name,
                        object_target_output,
                        compile_flags=source["compile_flags"],
                        include_dirs=source["include_dirs"],
                        sources=[
                            get_source_file_reference(
                                path,
                                language=source["language"],
                                dependencies=source.get("dependencies"),
                            )
                        ],
                    )
                    # current target depends on object_target, which means
                    # object_target must be declared before it.
                    # idx: array index that should accomodate object_target
                    object_targets.append((idx, object_target))
                    object_target_index[key] = object_target
                target["objects"].append(object_target_output)
                target["dependencies"].append(object_target_output)

            if len(target["sources"]) == 0:
                # All sources were replaced with object files
                if self.compile_flags_placeholder in target["compile_flags"]:
                    target["compile_flags"] = [self.compile_flags_placeholder]
                else:
                    target["compile_flags"] = []

                if self.include_dirs_placeholder in target["include_dirs"]:
                    target["include_dirs"] = [self.include_dirs_placeholder]
                else:
                    target["include_dirs"] = []

                for prop in language_specific_properties:
                    if prop in target:
                        target[prop] = []

        counter = 0
        for idx, target in object_targets:
            targets.insert(idx + counter, target)
            counter += 1

        return targets


__all__ = ["CMakeFixMultipleSourceInstancesWithDifferentFlags"]
