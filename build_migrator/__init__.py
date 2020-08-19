import os
import sys

__module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, __module_dir)

from build_migrator.core import BuildMigrator  # noqa: E402
from build_migrator.modules import (  # noqa: E402
    ModuleLoader,
    Builder,
    Parser,
    Optimizer,
    Generator,
    EntryPoint,
)
from build_migrator.settings import SettingsLoader  # noqa: E402


__doc__ = """
BuildMigrator - migrate your builds to CMake
=====================================================================

BuildMigrator provides streamlined migration process from Autotools (make),
Ninja or MSBuild to CMake. It achieves that by parsing build logs and then
generating an optimized CMakeLists.txt for discovered build artifacts.

Support for target build systems other than CMake is planned (Bazel).

BuildMigrator is intended for use in Monorepo-style projects with lots of
third party dependencies that require a homogenous build process.

Supported log types:
    Autotools (make), Ninja, MSBuild, Strace

Supported languages:
    C/C++, Assembler (Netwide, MASM, GNU), Objective C/C++, resource files (.rc)

Supported compilers:
    GCC, Clang, MSVC, MASM, Netwide Assembler (NASM), Yasm

Supported target platforms:
    Windows, Linux, Darwin (macOS, iOS)
    Our tests show that other platforms like FreeBSD and Android are covered
    by Linux support.

BuildMigrator is modular and extendable. Even if source build system,
language or compiler is not supported out of the box, BuildMigrator can
probably be configured or extended to support them.
"""


__all__ = [
    "BuildMigrator",
    "ModuleLoader",
    "SettingsLoader",
    "Builder",
    "Parser",
    "Optimizer",
    "Generator",
    "EntryPoint",
]
