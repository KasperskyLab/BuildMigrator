import argparse
import json
import os
import sys


_PRESET_EXTENSIONS = (".json",)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class SettingsLoader(object):
    """
    SettingsLoader class.

    SettingsLoader loads BuildMigrator settings from presets.

    BuildMigrator settings is a dictionary of arguments and values that are
    otherwise passed through command line. Almost any command line
    argument can be specified in settings dictionary. For full list of
    supported arguments, invoke `build_migrator --help`.

    Preset is a JSON file that stores BuildMigrator settings.
    """

    def __init__(self, search_dirs=None):
        """
        Initialize SettingsLoader

        Parameters
        ----------
        search_dirs : list of str, optional
            Additional search directories for presets.
            This argument mirrors `--preset_dirs` command line argument.
        """
        self.search_dirs = search_dirs or []

    def load(self, presets=None):
        """
        Load given presets, merge them into one dictionary using self.merge()
        and return the result.

        To see available presets, call:

        `build_migrator --list_presets`

        To inspect settings provided by a preset, call:

        `build_migrator --presets <preset> --show_settings`

        Parameters
        ----------
        presets : list of str, optional
            Preset can be either referenced by name (filename without
            extension) or path.

        Returns
        -------
        dict
            Resulting settings

        Raises
        ------
        FileNotFoundError
            Raised in case preset isn't found
        """
        merged_settings = {}
        preset_dict = {
            name: settings_path
            for name, settings_path in _enumerate_presets(self.search_dirs)
        }
        for name_or_path in presets or []:
            settings_path = None
            ext = os.path.splitext(name_or_path)[1].lower()
            if os.path.exists(name_or_path) and ext in _PRESET_EXTENSIONS:
                settings_path = name_or_path
            elif name_or_path in preset_dict:
                settings_path = preset_dict[name_or_path]
            else:
                raise IOError(
                    "Preset file not found: {}".format(name_or_path)
                )

            with open(settings_path) as f:
                settings = json.load(f)

            merged_settings = self.merge(merged_settings, settings)

        return merged_settings

    @staticmethod
    def merge(*settings):
        """
        Merge settings dictionaries. This method is used to merge preset settings.

        List values are concatenated. Non-list values are overwritten by rightmost dictionary.

        Returns
        -------
        dict
            settings dictionaries

        Raises
        ------
        ValueError
            Raised on invalid settings
        """
        result = {}
        for s in settings:
            for key, value in s.items():
                if key not in result:
                    result[key] = value
                else:
                    if isinstance(value, list) != isinstance(result[key], list):
                        msg = "Attribute type conflict in settings: {}".format(key)
                        raise ValueError(msg)
                    if isinstance(value, list):
                        result[key].extend(value)
                    else:
                        result[key] = value
        return result


def _process_command_line_args(args):
    if args.list_presets:
        for name, path in _enumerate_presets(args.preset_dirs):
            print("{}\n  {}".format(name, path))
        sys.exit(0)

    loader = SettingsLoader(args.preset_dirs)
    settings = loader.load(args.presets)
    if args.show_settings:
        print(json.dumps(settings, indent=4, sort_keys=True))
        sys.exit(0)

    return argparse.Namespace(**settings)


def _add_arguments(argument_parser):
    settings_parser = argument_parser.add_argument_group("presets")
    settings_parser.add_argument(
        "--list_presets",
        action="store_true",
        help="List available presets (--preset_dirs is honored).",
    )
    settings_parser.add_argument(
        "--preset_dirs",
        metavar="PATH",
        nargs="+",
        help="Additional search directories for presets.",
    )
    settings_parser.add_argument(
        "--presets",
        metavar="NAME or PATH",
        nargs="+",
        help="Load settings from selected presets. Preset is a JSON file that "
        "contains command line arguments with their values (=settings). "
        "Allowed JSON attributes are the same as command line "
        "arguments listed in --help message.",
    )
    settings_parser.add_argument(
        "--show_settings",
        action="store_true",
        help="Show effective settings for selected presets.",
    )


def _enumerate_presets(search_dirs=None):
    if search_dirs is None:
        search_dirs = []

    for search_dir in [_get_built_in_presets_dir()] + search_dirs:
        for filename in sorted(os.listdir(search_dir)):
            name, ext = os.path.splitext(filename)
            if ext.lower() in _PRESET_EXTENSIONS:
                yield (name, os.path.join(search_dir, filename))


def _get_built_in_presets_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "presets")


__all__ = ["SettingsLoader"]
