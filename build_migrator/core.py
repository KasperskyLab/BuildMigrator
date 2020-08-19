import json
import logging
import os
import pickle
import pprint
from build_migrator.modules import ModuleLoader


class BuildMigrator(object):
    """
    BuildMigrator class.

    BuildMigrator objects provide full set of methods needed to migrate from
    one build system to another:
    - Build specified project
    - Parse build logs and other artifacts to construct Build Object Model
    - Optimize Build Object Model for more succinct resulting build scripts
    - Generate build scripts for target build system

    In general, applications don't need more than one BuildMigrator instance.
    """

    _logger = logging.getLogger(__name__)
    _pretty_printer = pprint.PrettyPrinter(indent=2)

    def __init__(self, modules=None, settings=None):
        """
        Initializes BuildMigrator with given modules.

        Parameters
        ----------
        modules : result of ModuleLoader.load(), optional
            Given modules are used in build(), parse(), optimize() and generate() methods.
            If not given, default set of modules is created.
            For more information consult ModuleLoader documentation.
        settings : dict:
            Global settings for all stages (build, parse, generate, optimize).

            Supported settings mirror command line arguments for commands:

            `build_migrator --commands build parse optimize generate --help`

            Settings dictionary can be created manually or using SettingsLoader.
        """

        if modules is None:
            modules = ModuleLoader().load()
        self.modules = modules

        if settings is None:
            settings = {}
        if 'out_dir' not in settings:
            settings['out_dir'] = os.path.abspath(os.getcwd())
        self._settings = settings

    def build(self, **settings):
        """
        Build provided sources, producing build log and other artifacts that are
        used at later stages.

        Supported settings mirror command line arguments for `build` command:

        `build_migrator --commands build --help`

        Settings passed to this method override global settings.
        Settings dictionary can be created manually or using SettingsLoader.
        """
        kwargs = self._settings.copy()
        kwargs.update(settings or {})
        if kwargs:
            self._logger.debug(
                "Building using settings: %s", self._pretty_printer.pformat(settings)
            )
        else:
            self._logger.debug("Building")

        entry_point, builders = self.modules.create_builders(self, **settings)
        return entry_point.build(builders)

    def parse(self, build_object_model=None, **settings):
        """
        Parse build log, producing unoptimized Build Object Model.

        Supported settings mirror command line arguments for `parse` command:

        `build_migrator --commands parse --help`

        Settings passed to this method override global settings.
        Settings dictionary can be created manually or using SettingsLoader.

        Parameters
        ----------
        build_object_model : list
            Initial Build Object Model. This argument can be used to create
            aggregated Object Model for multiple projects.

        Returns
        -------
        Build Object Model
        """
        kwargs = self._settings.copy()
        kwargs.update(settings or {})
        if kwargs:
            self._logger.debug(
                "Parsing using settings: %s", self._pretty_printer.pformat(kwargs)
            )
        else:
            self._logger.debug("Parsing")

        entry_point, parsers = self.modules.create_parsers(self, **kwargs)
        return entry_point.parse(build_object_model, parsers)

    def optimize(self, build_object_model, **settings):
        """
        Optimize provided Build Object Model.

        Supported settings mirror command line arguments for `optimize` command:

        `build_migrator --commands optimize --help`

        Settings passed to this method override global settings.
        Settings dictionary can be created manually or using SettingsLoader.

        Parameters
        ----------
        build_object_model : list
            Build Object Model returned by parse() method

        Returns
        -------
        Build Object Model
        """
        kwargs = self._settings.copy()
        kwargs.update(settings or {})
        if kwargs:
            self._logger.debug(
                "Optimizing using settings: %s", self._pretty_printer.pformat(settings)
            )
        else:
            self._logger.debug("Optimizing")

        entry_point, optimizers = self.modules.create_optimizers(self, **kwargs)
        return entry_point.optimize(build_object_model, optimizers)

    def generate(self, build_object_model, **settings):
        """
        Generate CMakeLists.txt for provided Build Object Model.

        Supported settings mirror command line arguments for `generate` command:

        `build_migrator --commands generate --help`

        Settings passed to this method override global settings.
        Settings dictionary can be created manually or using SettingsLoader.

        Parameters
        ----------
        build_object_model : list
            Build Object Model returned by optimize() method
        """
        kwargs = self._settings.copy()
        kwargs.update(settings or {})
        if kwargs:
            self._logger.debug(
                "Generating using settings: %s", self._pretty_printer.pformat(settings)
            )
        else:
            self._logger.debug("Generating")

        entry_point, generators = self.modules.create_generators(self, **kwargs)
        entry_point.generate(build_object_model, generators)

    def save_build_object_model(self, path, build_object_model):
        """
        Save Build Object Model to file

        Parameters
        ----------
        path : path-like object
            Path to output file
        build_object_model : list
            Build Object Model
        """
        self._logger.info("Saving Build Object Model to %s", path)
        with open(path, "wb") as f:
            pickle.dump(build_object_model, f, protocol=2)

    def save_settings(self, path, user_settings=None):
        """
        Save settings to file

        Parameters
        ----------
        path : path-like object
            Path to output file
        user_settings : dict
            User settings
        """
        if user_settings is None:
            user_settings = {}
        with open(path, "w") as f:
            nonpersistent_attrs = (
                "show_settings",
                "list_modules",
                "verbose",
                "list_presets",
                "parsers",
                "builders",
                "optimizers",
                "generators",
                "build_commands",
                "commands"
            )
            settings = self._settings.copy()
            settings.update(user_settings)
            for attr in nonpersistent_attrs:
                if attr in settings:
                    del settings[attr]
            json.dump(settings, f)

    def load_build_object_model(self, path):
        """
        Load Build Object Model from file

        Parameters
        ----------
        path : path-like object
            Path to input file

        Returns
        -------
        Build Object Model
        """
        self._logger.info("Loading Build Object Model from %s", path)
        with open(path, "rb") as f:
            return pickle.load(f)

    def load_settings(self, path, user_settings=None):
        """
        Load settings from file

        Parameters
        ----------
        path : path-like object
            Path to input file
        user_settings : dict
            User settings

        Returns
        -------
        Build Object Model
        """
        if user_settings is None:
            user_settings = {}
        with open(path, "r") as f:
            settings = json.load(f)
            settings.update(user_settings)
            return settings

    def get_global_settings(self, attr):
        """
        Get a value from global settings

        Parameters
        ----------
        attr : str
            attribute name

        Returns
        -------
        any
            attribute value
        """
        return self._settings.get(attr)

    def set_global_settings(self, attr, value):
        """
        Modify global settings

        Parameters
        ----------
        attr : str
            attribute name
        value : any
            attribute value
        """
        self._logger.info('Changing global settings: %s => %r', attr, value)
        self._settings[attr] = value
