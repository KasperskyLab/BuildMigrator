import argparse
import copy
import os


class ModuleTypes:
    executable = "executable"
    object_lib = "object_lib"
    shared_lib = "shared_lib"
    static_lib = "static_lib"
    interface = "interface"


def get_module_target(
    module_type,
    name,
    output,
    msvc_import_lib=None,
    compile_flags=None,
    dependencies=None,
    libs=None,
    module_name=None,
    include_dirs=None,
    link_flags=None,
    objects=None,
    sources=None,
    version=None,
    compatibility_version=None,
    post_build_commands=None,
):
    if compile_flags is None:
        compile_flags = []
    if dependencies is None:
        dependencies = []
    if libs is None:
        libs = []
    if include_dirs is None:
        include_dirs = []
    if link_flags is None:
        link_flags = []
    if objects is None:
        objects = []
    if sources is None:
        sources = []

    if msvc_import_lib and not isinstance(msvc_import_lib, list):
        msvc_import_lib = [msvc_import_lib]

    target = {
        "type": "module",
        "module_type": module_type,
        "output": output,
        "msvc_import_lib": msvc_import_lib,
        "compile_flags": compile_flags,  # + c_flags, cxx_flags, etc
        "module_name": module_name,
        "include_dirs": include_dirs,  # + c_includes, cxx_includes, etc
        "link_flags": link_flags,
        "libs": libs,
        "name": name,
        "objects": objects,
        "sources": sources,
        "version": version,
        "compatibility_version": compatibility_version,
        "dependencies": dependencies,
    }
    if post_build_commands is not None:
        target["post_build_commands"] = post_build_commands
    return target


def get_module_copy(name, source, output, module_name=None, dependencies=None):
    if dependencies is None:
        dependencies = []

    return {
        "name": name,
        "module_name": module_name,
        "type": "module_copy",
        "output": output,
        "source": source,
        "dependencies": dependencies,
    }


def get_class_target(name, properties=None, conditions=None):
    if properties is None:
        properties = {}
    return {
        "name": name,
        "type": "class",
        "properties": properties,
        "conditions": conditions,
        "dependencies": [],
    }


def get_file_target(content, output, dependencies=None):
    """
    Get a target that creates a file

    Parameters
    ----------
    content : str
        file content
    output : str
        copy destination during build
    dependencies : list of str, optional
        outputs of target's dependencies, by default None

    Returns
    -------
    dict
        file target
    """

    target = {"type": "file", "content": content, "output": output}

    if dependencies:
        target["dependencies"] = dependencies

    return target


def get_directory_target(output, dependencies=None):
    target = {
        "type": "directory",
        "output": output,
        "dependencies": dependencies,
    }

    return target


def get_copy_target(name, source, output, dependencies=None, origin=None):
    if dependencies is None:
        dependencies = []
    return {
        "type": "copy",
        "name": name,
        "source": source,
        "output": output,
        "dependencies": dependencies,
    }


def get_variable_target(name, placeholder, value, dependencies=None):
    if dependencies is None:
        dependencies = []
    return {
        "type": "variable",
        "name": name,
        "placeholder": placeholder,
        "value": value,
        "output": placeholder,
        "dependencies": dependencies,
    }


def get_command_target(name, program, args, output, dependencies=None):
    if dependencies is None:
        dependencies = []
    if isinstance(output, list):
        extra_outputs = output[1:]
        output = output[0]
    else:
        extra_outputs = None
    return {
        "name": name,
        "type": "cmd",
        "program": program,
        "args": args,
        "dependencies": dependencies,
        "output": output,
        "msvc_import_lib": extra_outputs,
    }


def get_interface_target(name, include_dirs=None, libs=None, dependencies=None):
    return {
        "name": name,
        "type": "module",
        "module_type": ModuleTypes.interface,
        "include_dirs": include_dirs or [],
        "libs": libs or [],
        "dependencies": dependencies or [],
        "output": name,
        "sources": [],
        "compile_flags": [],
        "link_flags": [],
        "objects": []
    }


def get_source_file_reference(
    path, language=None, compile_flags=None, include_dirs=None, dependencies=None
):
    if compile_flags is None:
        compile_flags = []
    if include_dirs is None:
        include_dirs = []

    return {
        "path": path,
        "language": language,
        "compile_flags": compile_flags,
        "include_dirs": include_dirs,
        "dependencies": dependencies,
    }


def minify_target(target):
    if "content" in target:
        target["content"] = "..."
    for t in target.get("dependencies") or []:
        if isinstance(t, dict):
            minify_target(t)
    return target


def get_minified_target(target):
    target = copy.deepcopy(target)
    minify_target(target)
    return target


def get_minified_targets(targets):
    return list(map(get_minified_target, targets))


class ArgumentParserNoExit(argparse.ArgumentParser):
    """ArgumentParser subclass that does not call exit() on error()
    """

    def error(self, message):
        self.print_usage(argparse._sys.stderr)
        raise ValueError(argparse._("%s: error: %s\n") % (self.prog, message))


class ArgumentParserNoError(argparse.ArgumentParser):
    """ArgumentParser subclass that does not do anything on error()
    """

    def error(self, message):
        pass


language_to_flags_property = {
    "C": "c_flags",
    "C++": "cxx_flags",
    "GASM": "gasm_flags",
    "MASM": "masm_flags",
    "NASM": "nasm_flags",
    "RC": "rc_flags",
    "YASM": "yasm_flags",
}

language_to_includes_property = {
    "C": "c_include_dirs",
    "C++": "cxx_include_dirs",
    "GASM": "gasm_include_dirs",
    "MASM": "masm_include_dirs",
    "NASM": "nasm_include_dirs",
    "RC": "rc_include_dirs",
    "YASM": "yasm_include_dirs",
}


def get_source_with_inherited_flags(target, source):
    source = copy.copy(source)
    language = source.get("language")
    if language is not None:
        lang_flags_property = language_to_flags_property[language]
        lang_includes_property = language_to_includes_property[language]
        source["compile_flags"] = (
            target["compile_flags"]
            + (target.get(lang_flags_property) or [])
            + source["compile_flags"]
        )
        source["include_dirs"] = (
            target["include_dirs"]
            + (target.get(lang_includes_property) or [])
            + source["include_dirs"]
        )
    return source


def inherit_property_value(old, new):
    if new is None:
        return old
    if isinstance(old, list) and isinstance(new, list):
        return old + new
    return new


def is_target_in_class(target, class_target):
    if target.get("type") in [None, "class"]:
        return False
    conditions = class_target.get("conditions") or {}
    for property, expected_value in conditions.items():
        value = target.get(property)
        if value != expected_value:
            return False
    return True


def resolve_variables(values, target_index):
    if values is None:
        return None
    if not isinstance(values, list):
        return resolve_variables([values], target_index)[0]

    result = []
    for value in values:
        if isinstance(value, list):
            value = [resolve_variables(value, target_index)]
        else:
            variable_target = target_index.get(value)
            if variable_target is not None and variable_target["type"] == "variable":
                value = resolve_properties(variable_target, target_index, "value")
            else:
                value = [value]
        result.extend(value)

    return result


# Resolve property value for target, keeping in mind variables and classes
def resolve_properties(target, target_index, *properties):
    value = None
    for k, t in target_index.items():
        if t["type"] == "class" and is_target_in_class(target, t):
            new_value = resolve_properties(t["properties"], target_index, *properties)
            value = inherit_property_value(value, new_value)

    for p in properties:
        new_value = resolve_variables(target.get(p), target_index)
        value = inherit_property_value(value, new_value)
    return value


# Resolve compile flags for source, keeping in mind variables and classes
def resolve_compile_flags(target, source, target_index):
    lang_prop = language_to_flags_property[source["language"]]
    properties = ["compile_flags", lang_prop]

    values = resolve_properties(target, target_index, *properties)
    values = resolve_properties(source, target_index, *properties)
    return values


# Resolve include dirs for source, keeping in mind variables and classes
def resolve_include_dirs(target, source, target_index):
    lang_prop = language_to_includes_property[source["language"]]
    properties = ["include_dirs", lang_prop]

    values = resolve_properties(target, target_index, *properties)
    values = resolve_properties(source, target_index, *properties)
    return values


# Remove all occurences of specified value in targets' property
def remove_value_from_property(target_index, property, value, target=None):
    if target is None:
        for _, t in target_index.items():
            remove_value_from_property(target_index, property, value, t)
        return

    if target["type"] == "class":
        target = target["properties"]
    cur_value = target.get(property)
    if cur_value is None:
        return
    if isinstance(cur_value, list):
        cur_value = list(filter(lambda v: v != value, cur_value))
        variables = cur_value
    elif cur_value == value:
        cur_value = None
    else:
        variables = [cur_value]
    for var_id in variables:
        if not isinstance(var_id, str):
            continue
        var_target = target_index.get(var_id)
        if var_target:
            remove_value_from_property(target_index, "value", value, var_target)
    target[property] = cur_value


def filter_flags(delete_rxs, flags):
    if not delete_rxs:
        return flags

    filtered_flags = []
    for f in flags:
        if not isinstance(f, str):
            # multiargument flag
            value = " ".join(f)
        else:
            value = f

        remove = False
        for r in delete_rxs:
            if r.search(value):
                remove = True
                break

        if not remove:
            filtered_flags.append(f)

    return filtered_flags


# TODO: improve
def flatten_list(lst):
    result = []
    for elem in lst:
        if isinstance(elem, list):
            result.extend(flatten_list(elem))
        else:
            result.append(elem)
    return result


def format_flag_msvc_lowercase(lst):
    return "".join(format_flag_msvc(lst)).lower()


def _replace_prefix_char(lst, prefix_char):
    if lst and lst[0]:
        lst = copy.deepcopy(lst)
        lst[0] = prefix_char + lst[0][1:]
    return lst


def format_flag_msvc(lst):
    return "".join(_replace_prefix_char(lst, "/"))


def format_flag_gnu(lst):
    return "".join(_replace_prefix_char(lst, "-"))


def get_target_and_dependencies(target, index, skip_set=set()):
    if target["output"] not in skip_set:
        skip_set.add(target["output"])
        for dep in target.get("dependencies") or []:
            if dep in index:
                for dep_target in get_target_and_dependencies(
                    index[dep], index, skip_set
                ):
                    yield dep_target
        yield target


def filter_top_level_targets(
    targets, top_level_output=None, index=None, skip_set=set()
):
    if top_level_output is None:
        top_level_output = [t["output"] for t in targets if t.get("top_level")]

    if not top_level_output:
        return targets

    result = []
    if index is None:
        index = {}
        for t in targets:
            output = t.get("output")
            if output is not None:
                index[output] = t
            extra_outputs = t.get("msvc_import_lib") or []
            for o in extra_outputs:
                index[o] = t

    skip_set = set()
    deps = []
    for o in top_level_output:
        deps.extend(
            [
                t["output"]
                for t in get_target_and_dependencies(index[o], index, skip_set)
            ]
        )

    global_target_deps = []
    for t in targets:
        if "output" in t:
            continue
        for d in t.get("dependencies") or []:
            global_target_deps.extend(
                [
                    t["output"]
                    for t in get_target_and_dependencies(index[d], index, skip_set)
                ]
            )

    top_level_output = set(top_level_output)
    top_level_output.update(deps)
    top_level_output.update(global_target_deps)

    for t in targets:
        output = t.get("output")
        if output is None:
            result.append(t)
        elif output in top_level_output:
            result.append(t)

    return result


def get_final_module_copy_source(t, index):
    # find original target, bypassing all intermediate copies
    while t["type"] == "module_copy":
        t = index[t["source"]]
    return t


def get_target_output_dir(target):
    if "output" not in target:
        return None
    output = target["output"]
    return os.path.dirname(output)
