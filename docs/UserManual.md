# User Manual

BuildMigrator provides a set of tools that automate build migration
to CMake. We found it most useful when migrating third party dependencies
that use Autotools (make) and similar. Such build systems often require
unnecessarily long configuration step before building. They also have no easy
way to setup target-level dependencies and pass compilation flags
when used from CMake. All these problems are alleviated if such libraries
can be built natively with CMake.

## Using BuildMigrator to generate CMakeLists.txt

BuildMigrator provides two command line utilities: `build_migrator` and `cmake_merge`.

Note: on Windows, `build_migrator` must run in `vcvarsall.bat` environment.

`build_migrator` is responsible for CMakeLists.txt generation. Its operation is divided
into multiple commands (steps): `build`, `parse`, `optimize`, `generate`.
Each command has its own arguments, which can be listed with:

```bash
build_migrator --commands [{build,parse,optimize,generate} ...] --help
```

If `build_migrator` is called with `--commands` argument, only specified commands are executed.
Otherwise, all commands are executed.

Commands are described in more detail in the following sections.

### 1. Obtain build logs and build directory

```
build_migrator --commands build [args...]

args:
  --source_dir DIR      Source directory of the project that you want to migrate.
  --out_dir DIR         Output directory. Default: current directory.
  --build_command COMMAND [WORKING_DIR] [LOG] [COMMAND [WORKING_DIR] [LOG] ...]
                        COMMAND should be given as one argument, i.e. "make mytarget".
                        COMMAND supports subsitutions: {source_dir}, {out_dir}.
                        WORKING_DIR is optional, default value is taken from --out_dir.
                        LOG is the optional path to the log file produced by COMMAND.
                        LOG accepts special values:
                            CONSOLE: Pipe console output to file (path chosen automatically),
                            STRACE: Using strace, log syscalls made during build (strace output path
                            chosen automatically).
                        If no LOG is specified for any given COMMAND, default value (CONSOLE) is
                        automatically set for the last given COMMAND. Default value can be changed
                        using --log_provider argument.
  --log_provider {CONSOLE,STRACE}
                        Default LOG value for --build_command
```

This command obtains build log and associated build directory (builds the project, basically).
BuildMigrator uses these artifacts for the next commands.

This command is optional. Building be done manually without the help of BuildMigrator.

### 2. Parse build logs to produce Build Object Model

```
build_migrator --commands parse [args...]

args:
  --source_dir DIR      Source directory of the project that you want to migrate.
                        This argument's value persists between multiple commands if
                        --out_dir is the same.
  --out_dir DIR         Output directory. Default: current directory.
  --logs [TYPE:]PATH [[TYPE:]PATH ...]
                        Path to build log. For allowed log types, see --log_type argument.
                        Logs are processed in order.
  --log_type {make,msbuild,ninja,strace}
                        Supported log types.
  --build_dirs DIR [DIR ...]
                        Directory with build artifacts described in the provided build log.
                        Cannot be the same as source directory.
  --working_dir DIR     Initial working directory for given build logs.
  --path_alias PATH ALIAS
                        During parsing, if an argument points to PATH, replace it with ALIAS.
                        PATH can be relative to build directory. ALIAS can be made into a
                        configurable variable by specifying a value like this: @VARIBLE_NAME@.
                        After a variable is created, it can be used in other ALIASES like this:
                        @DIR@/path-to-file.txt.
  --platform {linux,windows,darwin}
                        Platform under which the build log was obtained. Mac and Linux builds
                        can be parsed on any platform. Windows build logs can be parsed only
                        on Windows. Default: current platform.
  --targets PATH/GLOB [PATH/GLOB ...]
                        Only specified files and their dependencies will be added to Build Object Model.
                        Values can be a path or a glob expression. Values are evaluated relative to build
                        directory. If a glob expression contains filename without directory, it matches
                        recursively.
  --capture_sources PATH/GLOB [PATH/GLOB ...]
                        Store only selected source files into Build Object Model.
                        Paths are evaluated relative to source directory.
                        By default, all source files are captured.
  --dont_capture_sources
                        Don't store source files in Build Object Model.
  --replace_line REGEX REPL
                        Replaces occurences of regex in build log.
                        Applicable for make, ninja or msbuild --log_type.
  --replace_strace REGEX REPL
                        Replaces occurences of regex in syscall arguments in build log.
                        Applicable only for --log_type strace.
  --tokenizer_ruleset {windows,posix}
                        Change command tokenization rules. Default is inferred
                        from --platform. It is recommended to use
                        posix_on_windows to correctly parse make/ninja logs
                        from Windows builds.
  --command_substitution
                        Enable command substitution in Posix-style (e.g. Makefile) logs.
                        Examples: 'gcc `pwd`/a.c' or 'gcc $(pwd)/a.c' will expand into
                        'gcc <current working dir>/a.c'.
                        WARNING: command is executed via Popen(shell=True), this may be a security hazard.
                        Use at your own risk.
  --ignore_compile_flags REGEX [REGEX ...]
                        Omit compilation flags matching specified regular expression.
                        Parser will behave as if flags weren't present in the build log.
  --ignore_link_flags REGEX [REGEX ...]
                        Omit link flags matching specified regular expression.
                        Parser will behave as if flags weren't present in the build log.
```

This command parses build log into an internal representation called Build Object Model.
Build Object Model contains all build targets found during parsing, as well as their source
files.
By default, Build Object Model is saved in the output directory (`--out_dir`).
Build Object Model is automatically loaded during the execution of subsequent commands.

### 3. Optimize Build Object Model, generate CMakeLists.txt

```
build_migrator --commands optimize generate --generator cmake [optimizer args...] [generator args...]

optimizer args:
  --keep_flags REGEX [REGEX ...]
                        Keep only matching compiler and linker flags in Build Object Model.
                        This argument doesn't affect link libraries (-lpthread etc).
                        By default, all flags are kept.
  --delete_flags REGEX [REGEX ...]
                        Delete matching compiler and linker flags.
                        This option comes into effect after --keep_flags.
                        Keep in mind, that this option is processed after build log object model
                        has already been constructed. This means that if some flag introduces an
                        unwanted dependency, this option will not delete that dependency.
                        If this behavior is not desired, --ignore_compile_flags and
                        --ignore_link_flags should be used.
  --replace_flag REGEX REPL
                        Replace matching compiler and linker flags.
                        This option comes into effect after --delete_flags.
  --file_target_change_encoding PATHMASK SOURCE_ENC DEST_ENC
                        Change encoding for files matching specified mask.
                        Supported encoding names are the same as for io module.
  --file_target_gsub PATHMASK REGEX REPL
                        Substitute content for files matching specified mask.
  --aggressive_optimization
                        Enable aggressive optimizations. This may greatly decrease resulting
                        CMakeLists.txt size at the expense of its readability.

generator args:
  --cmake_project_name NAME
                        Value of project(PROJECT-NAME) argument.
  --cmake_project_version VERSION
                        Value of project(VERSION) argument.
  --rename REGEX REPL   Modify automatic CMake target names.
  --default_var_value VAR_NAME VALUE
                        Change default value for generated CMake variable
  --flat_build_dir      Ignore output subdirectories for module targets.
                        For example: "@build_dir@/1/2/3/libfoo.a becomes
                        @build_dir@/libfoo.a.
```

During optimization, Build Object Model is transformed into a more concise
equivalent. This allows for a more readable CMakeLists.txt. For example:

```
gcc -c foo.c -o foo.o && gcc -shared foo.o -o libfoo.so

CMakeLists:
add_library(foo_o OBJECT foo.c)
add_library(foo SHARED $<TARGET_OBJECTS:foo_o>)
```

becomes:

```
gcc -shared foo.c -o libfoo.so

CMakeLists:
add_library(foo SHARED foo.c)
```

During generation, CMakeLists.txt is created as well as `source` and `prebuilt` directories.

- `source` directory contains required build files that originally were in --source_dir
- `prebuilt` directory contains required files that originally were in --build_dirs and have no command that produce them as output.

Original source tree is no longer needed, generated CMakeLists.txt is self-contained.

### 4. Merge multiple CMakeLists.txt files

If project is built differently for each supported platform, CMakeLists.txt should be generated for each platform.
Resulting CMakeLists.txt files are then merged into one. This can be done using `merge_cmake` tool. Usage:

```
cmake_merge infile [infile ...] outfile
```

Before merging, each `infile` must be preprocessed by adding CMake condition for its platform as a comment on the first line. For example:

infile:

```cmake
# WIN32
add_library(bar STATIC 1.c 2.c)
target_compile_options(bar PRIVATE /DFOR_WIN32)
```

infile:

```cmake
# APPLE
add_library(bar STATIC 1.c 2.c)
target_compile_options(bar PRIVATE /DFOR_APPLE)
```

outfile:

```cmake
add_library(bar STATIC 1.c 2.c)
if (WIN32)
    target_compile_options(bar PRIVATE /DFOR_WIN32)
endif()
if (APPLE)
    target_compile_options(bar PRIVATE /DFOR_APPLE)
endif()
```

### 5. Generate BUILD.bazel

```
build_migrator --commands optimize generate --generator bazel [optimizer args...] [generator args...]

optimizer args:
  --keep_flags REGEX [REGEX ...]
                        Keep only matching compiler and linker flags in Build Object Model.
                        This argument doesn't affect link libraries (-lpthread etc).
                        By default, all flags are kept.
  --delete_flags REGEX [REGEX ...]
                        Delete matching compiler and linker flags.
                        This option comes into effect after --keep_flags.
                        Keep in mind, that this option is processed after build log object model
                        has already been constructed. This means that if some flag introduces an
                        unwanted dependency, this option will not delete that dependency.
                        If this behavior is not desired, --ignore_compile_flags and
                        --ignore_link_flags should be used.
  --replace_flag REGEX REPL
                        Replace matching compiler and linker flags.
                        This option comes into effect after --delete_flags.
  --file_target_change_encoding PATHMASK SOURCE_ENC DEST_ENC
                        Change encoding for files matching specified mask.
                        Supported encoding names are the same as for io module.
  --file_target_gsub PATHMASK REGEX REPL
                        Substitute content for files matching specified mask.

generator args:
  --prebuilt_subdir DIRNAME
                        Directory for files that were generated during
                        original build, but have no associated command line.
                        Files like these may appear if there's no parser for
                        command line that generates them, or command line is
                        not listed in build logs. Default: prebuilt.
  --source_subdir DIRNAME
                        Subdirectory for captured source files. Default:
                        source.
```

Above commands create BUILD.bazel script as well as `source` and `prebuilt` directories.

- `source` directory contains required build files that originally were in --source_dir
- `prebuilt` directory contains required files that originally were in --build_dirs and have no command that produce them as output.

Original source tree is no longer needed, generated BUILD.bazel script is self-contained.

## Presets

Due to extreme configurability with multitude of available options,
sometimes it may be hard to navigate through BuildMigrator's command
line interface. To alleviate that, BuildMigrator provides presets.

A preset is a JSON file that stores BuildMigrator settings.
BuildMigrator settings is a dictionary of arguments and values that are
otherwise passed through command line. Almost any command line
argument can be specified in settings dictionary.

Presets are applied with `--presets` argument. BuildMigrator has many built-in presets.
For example, if you need to generate a CMakeLists.txt for a Autotools (make) log which
was created on Linux, you may specify `linux` and `autotools` presets:

```
build_migrator --presets linux autotools ...
```

To get full list of available presets, call:

```
build_migrator --list_presets
```
