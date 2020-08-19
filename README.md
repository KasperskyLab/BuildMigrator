# BuildMigrator - migrate your builds to CMake

BuildMigrator automates migration from Autotools (make), Ninja or MSBuild
to CMake. It achieves that by parsing build logs and generating a CMakeLists.txt
for discovered build artifacts. Additionally, it helps remove unused files
by keeping track of files that were used during compilation.

BuildMigrator is intended for use in Monorepo-style projects with lots of
third party dependencies that require a homogenous build process and clean
source tree.

Support for target build systems other than CMake is planned (Bazel).

Supported log types:

- Autotools (make)
- Ninja
- MSBuild
- strace

Supported languages:

- C/C++ (GCC, Clang, MSVC)
- Assembler (Netwide, MASM, GNU, Yasm)
- Objective C/C++
- Resource files (.rc)

Supported target platforms:

- Windows
- Linux
- Darwin (macOS, iOS)
- Our tests show that other platforms like FreeBSD and Android are covered by Linux support.

BuildMigrator was battle-tested on many libraries, including:

- Boost
- ICU
- jemalloc
- libxml2
- libxslt
- OpenSSL

**Important:** `Ninja` or `Unix Makefiles` CMake generators are recommended for building
CMakeLists.txt created by BuildMigrator.
Usage of `Visual Studio` generator is strongly discouraged due to a lack of correct compiler
option control in VS. See explanation: [/docs/VisualStudioGenerator.md](VisualStudioGenerator.md).

## Installation

Requirements: Python 2 or 3.

Download the latest [release package](https://github.com/KasperskyLab/BuildMigrator/releases) and extract it somewhere.
All the provided command line utilities are located inside `bin` subdirectory.

## Quickstart

If you want to just get started, you can follow the [examples](/docs/Examples.md).

## User Manual

[User Manual](/docs/UserManual.md) contains a quick overview of BuildMigrator workings,
description of provided command line utilities with a list of supported command line arguments.
