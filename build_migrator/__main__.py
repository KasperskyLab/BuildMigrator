import argparse
import logging
import os
import sys

import __init__  # noqa: F401
import build_migrator.modules
import build_migrator.settings
from build_migrator import BuildMigrator
from build_migrator.helpers import ArgumentParserNoError


def _add_arguments(parser, add_help=True):
    if add_help:
        parser.add_argument(
            "-h",
            "--help",
            action="help",
            help="Show this help message and exit. Help message can be limited to "
            "requested modules or commands: "
            "`--commands parse --help`, "
            "`--generators cmake --help`, "
            "`--parsers autotools --help`",
        )
    parser.add_argument(
        "--commands",
        choices=["build", "parse", "optimize", "generate"],
        nargs="+",
        help="List of enabled commands.\n"
        "'build': builds provided source and publishes build log,\n"
        "'parse': parses build log into Build Object Model,\n"
        "'optimize': optimizes Build Object Model (produces smaller build scripts),\n"
        "'generate': generates build script based on Build Object Model.\n"
        "Default: do everything.",
    )
    parser.add_argument(
        "--out_dir",
        metavar="DIR",
        help="Output directory. Default: current directory.",
    )
    exclusive_group = parser.add_mutually_exclusive_group()
    exclusive_group.add_argument(
        "--save", metavar="PATH", help="Save Build Object Model to file."
    )
    exclusive_group.add_argument(
        "--load", metavar="PATH", help="Load Build Object Model from file.",
    )
    parser.add_argument("--verbose", "-v", action="store_true")


def _parse_args_first_pass(argv):
    arg_parser = ArgumentParserNoError(add_help=False)
    _add_arguments(arg_parser, add_help=False)
    build_migrator.modules._add_arguments(arg_parser)
    build_migrator.settings._add_arguments(arg_parser)
    args = None
    try:
        args, _ = arg_parser.parse_known_args()
    except Exception:
        # main argument parser will receive and display this error later
        args = arg_parser.parse_args([])

    help_mode = "--help" in argv or "-h" in argv
    if help_mode and "--presets" in argv:
        raise ValueError("--help and --presets are incompatible")
    modules = build_migrator.modules._process_command_line_args(
        args, help_mode=help_mode
    )
    arg_parser = _create_argument_parser(args, modules, help_mode=help_mode)
    # Create Namespace with default values before parsing other arguments
    initial_namespace = build_migrator.settings._process_command_line_args(args)

    return arg_parser, modules, initial_namespace


def _create_argument_parser(args, modules, help_mode=False):
    parser = argparse.ArgumentParser(prog="build_migrator", add_help=False)
    _add_arguments(parser)
    build_migrator.modules._add_module_arguments(parser, modules)
    help_only_for_requested_modules = help_mode and (
        args.commands
        or args.builders
        or args.parsers
        or args.optimizers
        or args.generators
    )
    if not help_only_for_requested_modules:
        build_migrator.modules._add_arguments(parser)
        build_migrator.settings._add_arguments(parser)

    return parser


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        argv = ["--help"]
    arg_parser, modules, namespace = _parse_args_first_pass(argv)
    args = arg_parser.parse_args(argv, namespace)
    # TODO: logger format
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    migrator = BuildMigrator(modules)

    settings = vars(args)
    settings = {key: value for key, value in settings.items() if value is not None}
    if "out_dir" not in settings:
        settings["out_dir"] = os.path.abspath(os.getcwd())

    default_bom_path = os.path.join(settings["out_dir"], "bom.pickle")
    persistent_settings_path = os.path.join(settings["out_dir"], "settings.json")

    if os.path.exists(persistent_settings_path):
        settings = migrator.load_settings(persistent_settings_path, settings)

    if args.load is None:
        if os.path.exists(default_bom_path):
            args.load = default_bom_path

    build_object_model = None
    if args.load:
        build_object_model = migrator.load_build_object_model(args.load)

    if args.commands is None or "build" in args.commands:
        migrator.build(**settings)

    if args.commands is None or "parse" in args.commands:
        build_object_model = migrator.parse(build_object_model, **settings)

    if args.commands is None or "optimize" in args.commands:
        build_object_model = migrator.optimize(build_object_model, **settings)

    if args.commands is None or "generate" in args.commands:
        migrator.generate(build_object_model, **settings)

    if build_object_model is not None:
        if args.save is None:
            args.save = default_bom_path
        migrator.save_build_object_model(args.save, build_object_model)

    migrator.save_settings(persistent_settings_path, settings)


if __name__ == "__main__":
    main()
