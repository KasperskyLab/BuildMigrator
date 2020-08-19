
set(OMIT_UNICODE_COMPILE_DEFINITIONS ON)

include(remove_compilation_flag)

remove_compilation_flag("[-/]arch:IA32")
remove_compilation_flag("[-/]EHsc")
# Bump minimal supported Windows version
override_minimal_supported_windows_version(0x0A000002)

# Fix Ninja+clang-cl error:
# > CMake/bin/cmcldeps.exe RC file.rc file.rc.res.d file.rc.res "Note: including file: " clang-cl.exe rc.exe /fo file.rc.res file.rc:
#   fatal error: UTF-16 (LE) byte order mark detected in file.rc, but encoding is not supported
set(CMAKE_NINJA_CMCLDEPS_RC OFF)