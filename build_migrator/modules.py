import copy
import functools
import inspect
import logging
import os
import pkgutil
import sys
import traceback
import build_migrator.builders  # noqa: F401
import build_migrator.generators  # noqa: F401
import build_migrator.optimizers  # noqa: F401
import build_migrator.parsers  # noqa: F401
from build_migrator.common.algorithm import get_subdict


_EXTENSION_EXTS = (".py", ".pyc")
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_logger = logging.getLogger(__name__)


class ModuleGroups(object):
    BUILDERS = "builders"
    PARSERS = "parsers"
    OPTIMIZERS = "optimizers"
    GENERATORS = "generators"


class ModuleLoader(object):
    """
    ModuleLoader class.

    ModuleLoader loads BuildMigrator modules. BuildMigrator module is a Python
    module (.py or .pyc), which exports types implementing following interfaces:
    - build_migrator.Builder
    - build_migrator.Parser
    - build_migrator.Optimizer
    - build_migrator.Generator
    - build_migrator.EntryPoint

    ModuleLoader allows selectively loading built-in modules, or custom modules
    created by the user.

    For full list of built-in modules, call:

    `build_migrator --list_modules`
    """

    DEFAULT_GENERATORS = ["cmake"]

    def __init__(self, search_dirs=None):
        """
        Initialize ModuleLoader

        Parameters
        ----------
        search_dirs : list of str, optional
            Additional module search directories, by default None
            This argument mirrors `--module_dirs` command line argument
        """
        self.search_dirs = search_dirs or []

    def load(self, builders=None, parsers=None, optimizers=None, generators=None):
        """
        Load BuildMigrator modules.

        This method mirrors following command line aguments:

        `--builders`, `--parsers`, `--optimizers`, `--generators`

        Parameters
        ----------
        builders : list of str, optional
            List of paths or names of modules (filename without extension)
            that implement build_migrator.Builder interface.
            Here and for other module groups: one of the selected modules must
            implement build_migrator.EntryPoint interface.
            By default: all found Builder modules
        parsers : list of str, optional
            List of paths or names of modules that implement 
            build_migrator.Parser interface.
            By default: all found Parser modules
        optimizers : list of str, optional
            List of paths or names of modules that implement
            build_migrator.Optimizer interface.
            By default: all found Optimizer modules
        generators : list of str, optional
            List of paths or names of modules that implement
            build_migrator.Generator interface.
            By default: ['cmake']

        Returns
        -------
        Returns an object of internal type that can be passed to
        BuildMigrator constructor.
        """
        if generators is None:
            generators = self.DEFAULT_GENERATORS

        return self._load_no_defaults(builders, parsers, optimizers, generators)

    def _load_no_defaults(
        self, builders=None, parsers=None, optimizers=None, generators=None
    ):
        return _Initializer(
            _load_module_exports(
                "build_migrator.builders.",
                [os.path.join(_SCRIPT_DIR, ModuleGroups.BUILDERS)] + self.search_dirs,
                Builder,
                builders,
            ),
            _load_module_exports(
                "build_migrator.parsers.",
                [os.path.join(_SCRIPT_DIR, ModuleGroups.PARSERS)] + self.search_dirs,
                Parser,
                parsers,
            ),
            _load_module_exports(
                "build_migrator.optimizers.",
                [os.path.join(_SCRIPT_DIR, ModuleGroups.OPTIMIZERS)] + self.search_dirs,
                Optimizer,
                optimizers,
            ),
            _load_module_exports(
                "build_migrator.generators.",
                [os.path.join(_SCRIPT_DIR, ModuleGroups.GENERATORS)] + self.search_dirs,
                Generator,
                generators,
            ),
        )


class Parser(object):
    """
    Parser interface. Parsers produce Build Object Model from build log.

    Implementation notes
    --------------------

    Extension interfaces and Build Object Model are still under
    active development and may change in the future.

    Currently there's no stable specification for Build Object Model.
    At this point, Build Object Model is a list of dict, where
    each dict is created using functions from build_migrator.helpers.
    Code of built-in modules is recommended as reference implementation.

    Attributes
    ----------
    - priority : int
        optional, default value: maxint
        Parsers are ordered by this attribute

    Methods
    -------
    - add_arguments(parser : argparse.ArgumentParser)
        optional, class/static method
        Adds command line arguments that can be used to configure
        this extension.
    - __init__(self, context : EntryPoint, ...)
        optional
        Command line arguments from add_arguments() are passed
        to this method as keyword arguments.
    - parse(self, target : dict)
        required
        "Target" describes a command from build log in terms of Build Object Model.
        Targets can be created using functions from build_migrator.helpers.
        Returns:
            If Parser is not applicable: same target
            Otherwise: new target, or list of targets
    """

    pass


class Optimizer(object):
    """
    Optimizer interface. Optimizers process Build Object Model into more
    compact form, which produces shorter and more readable build scripts.

    Attributes
    ----------
    - priority : int
        optional, default value: maxint
        Optimizers are ordered by this attribute

    Methods
    -------
    - add_arguments(parser : argparse.ArgumentParser)
        optional, class/static method
        Adds command line arguments that can be used to configure
        this extension.
    - __init__(self, context : EntryPoint, ...)
        optional
        Command line arguments from add_arguments() are passed
        to this method as keyword arguments.
    - optimize(self, build_object_model : list of dict)
        required
        Optimizes build_object_model
        Returns: list of dict
    """

    pass


class Generator(object):
    """
    Generator interface.
    Generators produce build scripts from Build Object Model.

    Attributes
    ----------
    - priority : int
        optional, default value: maxint
        Generators are ordered by this attribute

    Methods
    -------
    - add_arguments(parser : argparse.ArgumentParser)
        optional, class/static method
        Adds command line arguments that can be used to configure
        this extension.
    - __init__(self, context : EntryPoint, ...)
        optional
        Command line arguments from add_arguments() are passed
        to this method as keyword arguments.
    - generate(self, target : dict)
        required
        'target' is an item from Build Object Model. Targets are created during
        parsing and optimization using methods from build_migrator.helpers.
        Returns:
            True, if Generator is applicable to given target. Target won't be passed to other generators.
            False, otherwise.
    """

    pass


class Builder(object):
    """
    Builder interface.

    Methods
    -------
    - add_arguments(parser : argparse.ArgumentParser)
        optional, class/static method
        Adds command line arguments that can be used to configure
        this extension.

    Must also implement EntryPoint interface.
    """

    pass


class EntryPoint(object):
    """
    EntryPoint interface.

    If type implements EntryPoint, it must implement additional interface
    type: Parser, Optimizer or Generator.

    EntryPoint is a top-level Builder, Parser, Optimizer or Generator that
    manages other extensions of the same type.

    EntryPoint+Parser methods
    -------------------------
    - __init__(self, build_migrator : BuildMigrator, ...)
        required
        Command line arguments from add_arguments() are passed
        to this method as keyword arguments.
    - parse(build_object_model, parsers : list of Parser)
        required
        build_object_model can be None
        Returns: build_object_model

    EntryPoint+Optimizer methods
    -------------------------
    - __init__(self, build_migrator : BuildMigrator ...)
        required
        Command line arguments from add_arguments() are passed
        to this method as keyword arguments.
    - optimize(build_object_model, optimizers : list of Optimizer)
        required
        Returns: build_object_model

    EntryPoint+Generator methods
    -------------------------
    - __init__(self, build_migrator : BuildMigrator ...)
        required
        Command line arguments from add_arguments() are passed
        to this method as keyword arguments.
    - generate(build_object_model, generators : list of Generator)
        required
        No return type

    EntryPoint+Builder methods
    -------------------------
    - __init__(self, build_migrator : BuildMigrator ...)
        required
        Command line arguments from add_arguments() are passed
        to this method as keyword arguments.
    - build()
        required
        Should create settings.json file in --out_dir with settings for subsequent commands
        settings.json may include such attributes as 'logs', 'source_dir', 'build_dirs'.
        No return type
    """

    pass


class _Initializer(object):
    def __init__(self, builders, parsers, optimizers, generators):
        self._module_dict = {
            ModuleGroups.BUILDERS: builders,
            ModuleGroups.PARSERS: parsers,
            ModuleGroups.OPTIMIZERS: optimizers,
            ModuleGroups.GENERATORS: generators,
        }

    def create_builders(self, build_migrator, **kwargs):
        """
        Supported **kwargs mirror command line arguments
        for `build` command:

        `build_migrator --commands build --help`

        Parameters
        ----------
        build_migrator : BuildMigrator
            Parent BuildMigrator instance

        Returns
        -------
        list of build_migrator.Builder
        """

        return self._create(ModuleGroups.BUILDERS, build_migrator=build_migrator, **kwargs)

    def create_parsers(self, build_migrator, **kwargs):
        """
        Supported **kwargs mirror command line arguments
        for `parse` command:

        `build_migrator --commands parse --help`

        Parameters
        ----------
        build_migrator : BuildMigrator
            Parent BuildMigrator instance

        Returns
        -------
        list of build_migrator.Parser
        """
        return self._create(ModuleGroups.PARSERS, build_migrator=build_migrator, **kwargs)

    def create_optimizers(self, build_migrator, **kwargs):
        """
        Supported **kwargs mirror command line arguments
        for `optimize` command:

        `build_migrator --commands optimize --help`

        Parameters
        ----------
        build_migrator : BuildMigrator
            Parent BuildMigrator instance

        Returns
        -------
        list of build_migrator.Optimizer
        """
        return self._create(ModuleGroups.OPTIMIZERS, build_migrator=build_migrator, **kwargs)

    def create_generators(self, build_migrator, **kwargs):
        """
        Supported **kwargs mirror command line arguments
        for `generate` command:

        `build_migrator --commands generate --help`

        Parameters
        ----------
        build_migrator : BuildMigrator
            Parent BuildMigrator instance

        Returns
        -------
        list of build_migrator.Generator
        """
        return self._create(ModuleGroups.GENERATORS, build_migrator=build_migrator, **kwargs)

    def _create(self, group, **kwargs):
        entry_point, other_types = _split_at_entry_point(
            [descr.type for descr in self._module_dict[group]]
        )
        known_argnames = set(
            functools.reduce(
                lambda set1, set2: set1 + set2,
                [
                    descr.required_init_argnames + descr.optional_init_argnames
                    for descr in self._module_dict[group]
                ],
            )
        )

        supported_kwargs = get_subdict(kwargs, *known_argnames)
        unknown_kwargs = set(kwargs.keys()) - known_argnames
        if unknown_kwargs:
            # TODO: turn into an error?
            _logger.warn("Unknown kwargs: {}".format(", ".join(unknown_kwargs)))
        return _batch_initialize(entry_point, other_types, **supported_kwargs)


def _split_at_entry_point(types):
    types = copy.copy(types)
    entry_point = None
    for t in types:
        if issubclass(t, EntryPoint):
            if entry_point is not None:
                msg = "Multiple EntryPoints found: {}, {}".format(entry_point, t)
                raise ValueError(msg)
            entry_point = t

    if entry_point is not None:
        types.remove(entry_point)
        return entry_point, types

    raise ValueError("EntryPoint not found")


def _batch_initialize(entry_point_type, other_types, **kwargs):
    objects = []
    unknown_kwargs = set(kwargs.keys())
    entry_point = None
    for t in [entry_point_type] + other_types:
        required_args, optional_args = _get_argspec_for_init(t)
        argnames = set(required_args + optional_args)
        unknown_kwargs -= argnames
        kwargs_ = get_subdict(kwargs, *argnames)
        if kwargs_:
            _logger.debug("Initializing %r with %r", t, kwargs_)
        else:
            _logger.debug("Initializing %r", t)
        if entry_point is not None and "context" in argnames:
            kwargs_["context"] = entry_point
        obj = t(**kwargs_)
        if entry_point is None:
            entry_point = obj
        else:
            objects.append(obj)
    if unknown_kwargs:
        raise ValueError("Unknown arguments: %s", ", ".join(unknown_kwargs))
    return entry_point, objects


def _process_command_line_args(args, help_mode=False):
    # In --help mode, if at least one module group is specified explicitly,
    # ignore default values for other groups.
    # This is required to make --help for modules work, for example:
    # ` --generators cmake --help` should display help only for cmake generator.
    non_default_modules = (
        args.builders or args.parsers or args.optimizers or args.generators
    )

    if args.commands:
        # Only modules for specified --commands should be loaded,
        # this allows requesting --help only for selected commands:
        # --commands parse generate --help
        if "build" not in args.commands:
            args.builders = []
        if "parse" not in args.commands:
            args.parsers = []
        if "optimize" not in args.commands:
            args.optimizers = []
        if "generate" not in args.commands:
            args.generators = []

    loader = ModuleLoader(args.module_dirs)
    if args.list_modules:
        for group, descriptors in loader._load_no_defaults()._module_dict.items():
            modules = set([d.module_name for d in descriptors])
            entry_point_modules = set(
                [d.module_name for d in descriptors if d.is_entry_point]
            )
            print("{}:".format(group))
            for name in sorted(entry_point_modules):
                print("  {} (entry point)".format(name))
            for name in sorted(modules):
                if name not in entry_point_modules:
                    print("  {}".format(name))
            print()
        sys.exit(0)
    else:
        keys = [
            ModuleGroups.BUILDERS,
            ModuleGroups.PARSERS,
            ModuleGroups.OPTIMIZERS,
            ModuleGroups.GENERATORS,
        ]
        kwargs = get_subdict(vars(args), *keys)
        if non_default_modules and help_mode:
            if any(kwargs.values()):
                for key in keys:
                    if kwargs.get(key) is None:
                        kwargs[key] = []

        modules = loader.load(**kwargs)

    return modules


def _add_arguments(argument_parser):
    parser = argument_parser.add_argument_group("modules")
    parser.add_argument(
        "--list_modules",
        action="store_true",
        help="List all available modules (--module_dirs value is honored).",
    )
    parser.add_argument(
        "--module_dirs",
        metavar="PATH",
        nargs="+",
        help="Additinal module search directories.",
    )
    parser.add_argument(
        "--builders",
        metavar="NAME or PATH",
        nargs="+",
        help="Use only specified builder modules. By default, all builders are loaded. "
        "BuildMigrator classifies Python module as 'builder' if it exports at least one "
        "type implementing `build_migrator.Builder` interface. One module in this "
        "list must also implement `build_migrator.EntryPoint` interface.",
    )
    parser.add_argument(
        "--parsers",
        metavar="NAME or PATH",
        nargs="+",
        help="Use only specified parser modules. By default, all parsers are loaded. "
        "BuildMigrator classifies Python module as 'parser' if it exports at least one "
        "type implementing `build_migrator.Parser` interface. One module in this "
        "list must also implement `build_migrator.EntryPoint` interface.",
    )
    parser.add_argument(
        "--optimizers",
        metavar="NAME or PATH",
        nargs="+",
        help="Use only specified optimizer modules. By default, all optimizers are loaded. "
        "BuildMigrator classifies Python module as 'optimizer' if it exports at least one "
        "type implementing `build_migrator.Optimizer` interface. One module in this "
        "list must also implement `build_migrator.EntryPoint` interface.",
    )
    parser.add_argument(
        "--generators",
        metavar="NAME or PATH",
        nargs="+",
        help="Use only specified generator modules. Default: {}. "
        "BuildMigrator classifies Python module as 'generaor' if it exports at least one "
        "type implementing `build_migrator.Generator` interface. One module in this "
        "list must also implement `build_migrator.EntryPoint` interface.".format(
            ", ".join(ModuleLoader.DEFAULT_GENERATORS)
        ),
    )


def _add_module_arguments(argument_parser, modules):
    if modules is not None:
        module_dict = modules._module_dict
    else:
        module_dict = {}
    group_to_description = {
        ModuleGroups.BUILDERS: "builder arguments (available when 'build' is in --commands, or --commands is not specified)",
        ModuleGroups.PARSERS: "parser arguments (available when 'parse' is in --commands, or --commands is not specified)",
        ModuleGroups.OPTIMIZERS: "optimizer arguments (available when 'optimize' is in --commands, or --commands is not specified)",
        ModuleGroups.GENERATORS: "generator arguments (available when 'generate' is in --commands, or --commands is not specified)",
    }
    for group, descriptors in module_dict.items():
        group_arguments = argument_parser.add_argument_group(
            group_to_description[group]
        )
        for t in [d.type for d in descriptors]:
            add_arguments_attr = getattr(t, "add_arguments", None)
            if callable(add_arguments_attr):
                add_arguments_attr(group_arguments)


def _get_argspec_for_init(module_export):
    if hasattr(module_export.__init__, "__code__"):
        argnames, varargs, kwargs, defaults = inspect.getargspec(module_export.__init__)
        if varargs:
            msg = "{}: varargs are not allowed in __init__ methods of module exports".format(
                module_export
            )
            raise ValueError(msg)
        if kwargs:
            msg = "{}: kwargs are not allowed in __init__ methods of module exports".format(
                module_export
            )
            raise ValueError(msg)
        if defaults is None:
            defaults = []
        return (
            argnames[1 : len(argnames) - len(defaults)],
            argnames[len(argnames) - len(defaults) :],
        )
    else:
        return [], []


class _ExportDescriptor(object):
    def __init__(
        self,
        type,
        module_name,
        required_init_argnames,
        optional_init_argnames,
        is_entry_point=False,
    ):
        self.type = type
        self.module_name = module_name
        self.required_init_argnames = required_init_argnames
        self.optional_init_argnames = optional_init_argnames
        self.is_entry_point = is_entry_point


def _load_module_exports(
    base_package_name, search_dirs, export_type, names_or_paths=None
):
    loader_dict = {
        name: loader
        for name, loader in _enumerate_module_loaders(base_package_name, search_dirs)
    }
    reraise_exception = True
    if names_or_paths is None:
        names_or_paths = loader_dict.keys()
        # user didn't specify any required modules,
        # so it doesn't matter if some of them won't load
        reraise_exception = False
    loaded_modules = set()
    loaded_types = set()
    export_descriptors = []
    for value in names_or_paths:
        if value not in loader_dict:
            path = value
            search_dir = os.path.dirname(path)
            name, ext = os.path.splitext(os.path.basename(path))
            if ext and ext.lower() not in _EXTENSION_EXTS:
                raise ValueError(
                    "File must have .py or .pyc extension: {}".format(path)
                )
            found = list(
                _enumerate_module_loaders(
                    base_package_name, [search_dir or "."], [name]
                )
            )
            if not found:
                raise ValueError("Module not found or invalid: {}".format(path))
            loader_dict[name] = found[0][1]
        else:
            name = value
        if name in loaded_modules:
            continue
        try:
            module = loader_dict[name]()
            loaded_modules.add(name)
            found_exports = [getattr(module, name) for name in module.__all__]
            found_exports = filter(lambda t: issubclass(t, export_type), found_exports)
            for t in found_exports:
                required_args, optional_args = _get_argspec_for_init(t)
                full_type_name = _get_full_type_name(t)
                if full_type_name in loaded_types:
                    continue
                loaded_types.add(full_type_name)
                export_descriptors.append(
                    _ExportDescriptor(
                        t, name, required_args, optional_args, issubclass(t, EntryPoint)
                    )
                )
        except Exception:
            _logger.error(traceback.format_exc())
            if reraise_exception:
                raise
    return _sort_descriptors(export_descriptors)


def _enumerate_module_loaders(base_package_name, directories, module_filter=None):
    for loader, fullname, ispkg in pkgutil.iter_modules(directories, base_package_name):
        if ispkg:
            continue
        module_name = fullname.split(".")[-1]
        if module_name.startswith("_"):
            continue
        if module_filter is not None and module_name not in module_filter:
            continue
        try:

            def _load(loader=loader, fullname=fullname):
                _logger.debug("Loading module {}".format(fullname))
                module = loader.find_module(fullname).load_module(fullname)
                _logger.debug("Module exports: {}".format(", ".join(module.__all__)))
                return module

            yield module_name, _load
        except Exception:
            _logger.error(traceback.format_exc())


def _get_priority(module_export):
    return getattr(module_export, "priority", sys.maxsize)


def _get_full_type_name(type):
    return type.__module__ + "." + type.__name__


def _sort_descriptors(export_descriptors):
    # `sorted` uses stable sorting algorithm
    # sort by name
    export_descriptors = sorted(
        export_descriptors, key=lambda d: (d.module_name, _get_full_type_name(d.type))
    )
    # sort by priority
    export_descriptors = sorted(export_descriptors, key=lambda d: _get_priority(d.type))
    # sort entry point / not entry point
    return sorted(export_descriptors, key=lambda d: not d.is_entry_point)


__all__ = ["ModuleLoader"]
