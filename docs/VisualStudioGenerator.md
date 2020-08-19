# Problems with Visual Studio generator

When using generated CMakeLists.txt, `Ninja` and `Unix Makefiles` are recommended
over `Visual Studio` generator. VS has many instances of incorrect flag control
(described below), which sometimes makes it impossible to reproduce original
build flags for each source file.

All the problems described below are most likely not specific to the way CMake generates
Visual Studio projects, but an inherent behavior of VS.

- `add_compile_options`, `target_compile_options`: all specified flags should be passed to all
  languages. When using VS, only definitions (`-D`) are passed to all languages, the rest is passed
  only to C/C++ source files.
- `add_compile_options($<$<COMPILE_LANGUAGE:CXX>:flags>)`, `target_compile_options($<$<COMPILE_LANGUAGE:CXX>:flags>)`: specified flags should be passed only to C++ source files. When using VS, definitions are passed to all source files, remaining flags are passed to both  C and C++.
- `*include_directories($<$<COMPILE_LANGUAGE:LANG>:dirs>)`: if LANG is C then dirs are ignored. C source files always receive include_directories from CXX.
- `CMAKE_<LANG>_FLAGS`:
  - If LANG is ASM_MASM: definitions (`-D`) are ignored. Definitions for ASM_MASM are taken from CMAKE_CXX_FLAGS.
  - If LANG is ASM_NASM: definitions from CMAKE_CXX_FLAGS are added to specified flags
  - if LANG is RC: definitions from CMAKE_CXX_FLAGS are added to specified flags
  - C flags are ignored, C source files are compiled with CXX flags
- VS may add unexpected flags like -D_MBCS, -D_SBCS, -D_UNICODE etc, which may break compilation
  if the code isn't ready for them.

`Ninja` and `Unix Makefiles` generators don't have the problems described above.
