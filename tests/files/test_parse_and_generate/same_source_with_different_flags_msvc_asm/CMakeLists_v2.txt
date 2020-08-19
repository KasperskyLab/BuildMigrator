cmake_minimum_required(VERSION 3.8)

project(PROJECT )
enable_language(ASM_MASM)
enable_language(ASM_NASM)

include(cmake_framework)
include(compiler_config)
include(system)
include(target_yasm_sources)
fix_asm_flags()
find_thread_library()

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(CMAKE_ASM_NASM_OBJECT_FORMAT win32)
set(CMAKE_ASM_YASM_OBJECT_FORMAT win32)
set(CMAKE_ASM_YASM_MACHINE x86)

add_library(yasm_test_asm_1 OBJECT )
set_target_properties(yasm_test_asm_1 PROPERTIES LINKER_LANGUAGE ASM_MASM)
target_compile_options(yasm_test_asm_1 PRIVATE -pnasm -rnasm -DYASM_MODE=1)
target_yasm_sources(yasm_test_asm_1 PRIVATE ${SOURCE_DIR}/yasm_test.asm)

set_source_files_properties(${SOURCE_DIR}/nasm_test.asm PROPERTIES LANGUAGE ASM_NASM)
add_library(nasm_test_asm_1 OBJECT ${SOURCE_DIR}/nasm_test.asm)
set_target_properties(nasm_test_asm_1 PROPERTIES LINKER_LANGUAGE ASM_MASM)
target_compile_options(nasm_test_asm_1 PRIVATE -DNASM_MODE=1)

set_source_files_properties(${SOURCE_DIR}/masm_test.asm PROPERTIES LANGUAGE ASM_MASM)
add_library(masm_test_asm_1 OBJECT ${SOURCE_DIR}/masm_test.asm)
set_target_properties(masm_test_asm_1 PROPERTIES LINKER_LANGUAGE ASM_MASM)
target_compile_options(masm_test_asm_1 PRIVATE -DMASM_MODE=1)

add_library(test1
    $<TARGET_OBJECTS:yasm_test_asm_1>
    $<TARGET_OBJECTS:nasm_test_asm_1>
    $<TARGET_OBJECTS:masm_test_asm_1>
)
set_target_properties(test1 PROPERTIES LINKER_LANGUAGE ASM_MASM)

add_library(yasm_test_asm_2 OBJECT )
set_target_properties(yasm_test_asm_2 PROPERTIES LINKER_LANGUAGE ASM_MASM)
target_compile_options(yasm_test_asm_2 PRIVATE -pnasm -rnasm -DYASM_MODE=2)
target_yasm_sources(yasm_test_asm_2 PRIVATE ${SOURCE_DIR}/yasm_test.asm)

set_source_files_properties(${SOURCE_DIR}/nasm_test.asm PROPERTIES LANGUAGE ASM_NASM)
add_library(nasm_test_asm_2 OBJECT ${SOURCE_DIR}/nasm_test.asm)
set_target_properties(nasm_test_asm_2 PROPERTIES LINKER_LANGUAGE ASM_MASM)
target_compile_options(nasm_test_asm_2 PRIVATE -DNASM_MODE=2)

add_library(yasm_test_asm_3 OBJECT )
set_target_properties(yasm_test_asm_3 PROPERTIES LINKER_LANGUAGE ASM_MASM)
target_compile_options(yasm_test_asm_3 PRIVATE -pnasm -rnasm -DYASM_MODE=2)
target_include_directories(yasm_test_asm_3 PRIVATE ${SOURCE_DIR})
target_yasm_sources(yasm_test_asm_3 PRIVATE ${SOURCE_DIR}/yasm_test.asm)

set_source_files_properties(${SOURCE_DIR}/masm_test.asm PROPERTIES LANGUAGE ASM_MASM)
add_library(masm_test_asm_2 OBJECT ${SOURCE_DIR}/masm_test.asm)
set_target_properties(masm_test_asm_2 PROPERTIES LINKER_LANGUAGE ASM_MASM)
target_compile_options(masm_test_asm_2 PRIVATE -DMASM_MODE=2)

add_library(test2
    $<TARGET_OBJECTS:yasm_test_asm_2>
    $<TARGET_OBJECTS:nasm_test_asm_2>
    $<TARGET_OBJECTS:yasm_test_asm_3>
    $<TARGET_OBJECTS:masm_test_asm_1>
    $<TARGET_OBJECTS:masm_test_asm_2>
)
set_target_properties(test2 PROPERTIES LINKER_LANGUAGE ASM_MASM)
