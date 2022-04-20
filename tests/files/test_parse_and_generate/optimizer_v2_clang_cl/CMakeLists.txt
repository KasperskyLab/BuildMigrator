cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(compile_flags_1
    -D__WRL_ENABLE_FUNCTION_STATICS__
    -Wextra-semi
    -Wheader-hygiene
    -Wimplicit-fallthrough
    -Wno-backend-plugin
    -Wno-c++11-narrowing
    -Wno-ignored-pragma-optimize
    -Wno-missing-field-initializers
    -Wno-nonportable-include-path
    -Wno-profile-instr-out-of-date
    -Wno-profile-instr-unprofiled
    -Wno-trigraphs
    -Wno-undefined-var-template
    -Wno-unneeded-internal-declaration
    -Wno-unused-const-variable
    -Wno-unused-function
    -Wno-unused-parameter
    -Wstring-conversion
    -Wtautological-overlap-compare
    -Wthread-safety
    -Wunreachable-code
    "SHELL:-Xclang -debug-info-kind=limited"
    "SHELL:-Xclang -fdebug-compilation-dir"
    "SHELL:-Xclang ."
    -fcrash-diagnostics-dir=${CMAKE_CURRENT_BINARY_DIR}/crashreports
    -fmerge-all-constants
    -fprofile-instr-use=${SOURCE_DIR}/pgo_profiles/123.profdata
    -gcodeview-ghash
    -no-canonical-prefixes
    /W4
    /WX
    /wd4091
    /wd4100
    /wd4121
    /wd4127
    /wd4200
    /wd4201
    /wd4204
    /wd4221
    /wd4244
    /wd4245
    /wd4251
    /wd4267
    /wd4275
    /wd4305
    /wd4312
    /wd4324
    /wd4351
    /wd4355
    /wd4389
    /wd4456
    /wd4457
    /wd4458
    /wd4459
    /wd4503
    /wd4505
    /wd4510
    /wd4512
    /wd4577
    /wd4589
    /wd4610
    /wd4611
    /wd4661
    /wd4701
    /wd4702
    /wd4703
    /wd4706
    /wd4715
    /wd4838
    /wd4995
    /wd4996
)
set(compile_flags_2
    -fcrash-diagnostics-dir=${CMAKE_CURRENT_BINARY_DIR}/crashreports
    -fmerge-all-constants
)
add_compile_options(
    -fcolor-diagnostics
    -mllvm
    -instcombine-lower-dbg-declare=0
    -fcomplete-member-pointers
    /Gy
    /FS
    /bigobj
    /utf-8
    /Zc:twoPhase
    /Zc:sizedDealloc-
    /X
    -fmsc-version=1916
    -msse3
    /Ob2
    /Oy-
    /Zc:inline
    /Gw
    /Oi
    /guard:cf,nochecks
    /MT$<$<CONFIG:Debug>:d>
)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/crashreports)

add_library(a_cpp_1 OBJECT ${SOURCE_DIR}/a.cpp)
target_compile_options(a_cpp_1 PRIVATE
    /GR-
    ${compile_flags_1}
    "SHELL:-Xclang -fdebug-compilation-dir"
    "SHELL:-Xclang ."
    "SHELL:-Xclang -debug-info-kind=limited"
)

set_source_files_properties(${SOURCE_DIR}/b.cpp PROPERTIES COMPILE_OPTIONS
    "${compile_flags_1};SHELL:-Xclang -fdebug-compilation-dir;SHELL:-Xclang .;SHELL:-Xclang -debug-info-kind=limited"
)
set_source_files_properties(${SOURCE_DIR}/c.cpp PROPERTIES COMPILE_OPTIONS
    "${compile_flags_1};SHELL:-Xclang -fdebug-compilation-dir;SHELL:-Xclang .;SHELL:-Xclang -debug-info-kind=limited"
)
set_source_files_properties(${SOURCE_DIR}/d.cpp PROPERTIES COMPILE_OPTIONS
    "${compile_flags_2};SHELL:-Xclang -fdebug-compilation-dir;SHELL:-Xclang .;-no-canonical-prefixes;SHELL:-Xclang -debug-info-kind=limited;-fprofile-instr-use=${SOURCE_DIR}/pgo_profiles/123.profdata"
)
add_library(test SHARED
    ${SOURCE_DIR}/b.cpp
    ${SOURCE_DIR}/c.cpp
    ${SOURCE_DIR}/d.cpp
    ${SOURCE_DIR}/e.cpp
    $<TARGET_OBJECTS:a_cpp_1>
)
target_compile_options(test PRIVATE /GR-)
set_target_properties(test PROPERTIES ARCHIVE_OUTPUT_NAME test.dll)

add_library(a_cpp_2 OBJECT ${SOURCE_DIR}/a.cpp)
target_compile_options(a_cpp_2 PRIVATE ${compile_flags_2} -D__WRL_ENABLE_FUNCTION_STATICS__)

add_library(test2 SHARED $<TARGET_OBJECTS:a_cpp_2>)
set_target_properties(test2 PROPERTIES LINKER_LANGUAGE CXX)
set_target_properties(test2 PROPERTIES ARCHIVE_OUTPUT_NAME test2.dll)
