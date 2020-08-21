# Examples

All example scripts and CMakeLists are located [in Examples subfolder](Examples).

## OpenSSL

This example shows how to generate a CMakeLists.txt for OpenSSL libraries,
openssl executable (`apps/openssl`) and some unit tests.
It was tested on OpenSSL version 1.1.1g.

### OpenSSL: Linux

Command line [for_linux.sh](Examples/openssl/for_linux.sh)

```
build_migrator --build_command "{source_dir}/config" \
    --build_command make \
    --source_dir "<OpenSSL source dir>" \
    --presets autotools linux \
    --aggressive_optimization \
    --targets libcrypto.a libcrypto.so libssl.a libssl.so \
              apps/openssl test/asn1_decode_test test/x509_time_test \
    --verbose
```

Resulting CMakeLists.txt: [CMakeLists_linux.txt](Examples/openssl/CMakeLists_linux.txt)

Notes:

- BuildMigrator automatically parses console output of the last `--build_command` (this behavior can be overridden).
- `--targets` specifies paths to top-level targets for generator.
  Any targets that top-level targets don't depend on are skipped during CMakeList.txt generation.
- Generated CMakeLists.txt fully reproduces source build, down to compilation flags of each source file. Sometimes it comes at the cost of readability, as in this case.
- If a target has too many sources, they are listed in a separate file. See `SSL_STATIC_SRC.cmake` and `ssl.static` library.
- Source files that were used during build are added to `source` subdirectory. This means you don't need the original source tree anymore.
- Some source files may also appear in `prebuilt` subdirectory. This happens when source files are generated during build and parser wasn't able to find a command that generates them in the logs.
- CMakeLists.txt may uses some extension functions from `extensions.cmake`.

### OpenSSL: Windows

Command line [for_windows.bat](Examples/openssl/for_windows.bat)

```
build_migrator --build_command "perl {source_dir}/Configure VC-WIN64A" ^
    --build_command "nmake /U" ^
    --source_dir "<OpenSSL source dir>" ^
    --presets autotools windows ^
    --aggressive_optimization ^
    --targets libcrypto_static.lib libcrypto-1_1-x64.dll ^
             libssl_static.lib libssl-1_1-x64.dll ^
             apps/openssl.exe test/asn1_decode_test.exe test/x509_time_test.exe ^
    --verbose
```

Resulting CMakeLists.txt: [CMakeLists_windows.txt](Examples/openssl/CMakeLists_windows.txt)

### OpenSSL: Darwin

Command line [for_darwin.sh](Examples/openssl/for_darwin.sh)

```
build_migrator --build_command "{source_dir}/config" \
    --build_command make \
    --source_dir "<OpenSSL source dir>" \
    --presets autotools darwin \
    --aggressive_optimization \
    --targets libcrypto.a libcrypto.dylib libssl.a libssl.dylib \
              apps/openssl test/asn1_decode_test test/x509_time_test \
    --verbose
```

## ICU

This example shows how to generate CMakeLists.txt for ICU4C libraries. It was
tested on ICU version 67.1.

### ICU: Linux

Command line [for_linux.sh](Examples/icu/for_linux.sh)

```
build_migrator --build_command "{source_dir}/configure --enable-static --enable-shared=no --enable-tests=no --enable-samples=no  --enable-dyload=no" \
    --build_command "make VERBOSE=1" \
    --project icu \
    --source_dir "<ICU source dir>/icu/source" \
    --presets autotools linux icu \
    --targets "lib/*.a" "stubdata/*.a" \
    --aggressive_optimization \
    --delete_flags "^-DU_BUILD=" "^-DU_HOST=" "^-DU_CC=" "^-DU_CXX=" \
    --verbose
```

Resulting CMakeLists.txt: [CMakeLists_linux.txt](Examples/icu/CMakeLists_linux.txt)

Notes:

- Generated CMakeLists.txt requires `pkgdata` and `icupkg` tools to be present in PATH.
  This is due to a limitation in CMake: it allows only cross-compilation, but these tools
  must be compiled for host architecture.

## Boost with ICU support

This example shows the following:

- How to generate CMakeLists.txt for Boost C++ libraries. It was tested with Boost version 1.73.
- How to setup dependencies between generated CMakeLists (Boost and ICU).
- How to split generation process into multiple BuildMigrator calls.

### Boost with ICU support: Linux

Build Boost: [1_build_for_linux.sh](Examples/boost_with_icu/1_build_for_linux.sh)

```
build_migrator --commands build \
    --source_dir "<Boost source dir>" \
    --build_command "{source_dir}/bootstrap.sh" "{source_dir}" \
    --build_command "{source_dir}/b2 --without-python --without-math address-model=64 architecture=x86 --build-dir=b --stagedir=stage variant=release link=static library-path=<ICU install dir>/lib -sICU_PATH=<ICU install dir> -sboost.locale.icu=on stage -q -j8 -d+2" "{source_dir}" \
    --presets autotools darwin \
    --verbose
```

Note: `library-path` and `-sICU_PATH` should point to original (Autotools-based) ICU `make install` directory.

Parse Boost logs: [2_parse_for_linux.sh](Examples/boost_with_icu/2_parse_for_linux.sh)

```
build_migrator --commands parse \
    --build_dirs <Boost source dir>/b/boost/bin.v2/libs \
    --targets "*.a" \
    --working_dir "<Boost source dir>" \
    --replace_line "compile-c-c\+\+ " "" \
    --path_alias "<ICU install dir>/include" "@ICU_INCLUDE_DIRS@" \
    --verbose
```

Notes:

- Boost.Build must be called from within Boost source directory, hence `--working_dir` argument.
- `--build_dirs` changes build directory to ignore anything below `<Boost source dir>/b/boost/bin.v2/libs`.
- `--path_alias` creates a configurable CMake variable (CACHE) that points to ICU include directory.
- Boost.Build prints some system messages starting with `compile-c-c++`, which Clang/GCC parser considers to be a compiler command line, which it's not. `--replace_line` argument fixes this.

Generate CMakeLists.txt: [3_generate_for_linux.sh](Examples/boost_with_icu/3_generate_for_linux.sh)

```
build_migrator --commands optimize generate --aggressive_optimization \
               --default_var_value ICU_INCLUDE_DIRS "" \
               --project boost \
               --flat_build_dir \
               --verbose
```

Notes:

- Default value of ICU_INCLUDE_DIRS variable will contain original string from build log.
  This is most likely not desired, so we change its value with `--default_var_value` argument.
- `--flat_build_dir` allows to ignore Boost's highly nested build tree when generating CMakeLists.txt.
  For example, `@build_dir@/1/2/3/4/libboost_system.a` becomes `@build_dir@/libboost_system.a` in CMake build output.

Resulting CMakeLists.txt: [CMakeLists_linux.txt](Examples/boost_with_icu/CMakeLists_linux.txt)

Generated CMakeLists for Boost and ICU can be built together using such entry point:

```cmake
cmake_minimum_required(VERSION 3.15)

project(boost_with_icu)

add_subdirectory(icu) # generated CMakeLists.txt for ICU
set(ICU_INCLUDE_DIRS
    ${CMAKE_CURRENT_LIST_DIR}/icu/source/common
    ${CMAKE_CURRENT_LIST_DIR}/icu/source/i18n
    ${CMAKE_CURRENT_LIST_DIR}/icu/source/io
    CACHE STRING ""
)
add_subdirectory(boost) # generated CMakeLists.txt for Boost
```
