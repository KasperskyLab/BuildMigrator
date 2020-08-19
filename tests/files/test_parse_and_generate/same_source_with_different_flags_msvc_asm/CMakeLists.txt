cmake_minimum_required(VERSION 3.13)

project(PROJECT LANGUAGES)
enable_language(ASM_MASM)
enable_language(ASM_NASM)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(yasm_test_asm_1 OBJECT )
set_target_properties(yasm_test_asm_1 PROPERTIES LINKER_LANGUAGE ASM_MASM)
target_compile_options(yasm_test_asm_1 PRIVATE -pnasm -rnasm -fwin32 -mx86 -DYASM_MODE=1)
target_yasm_sources(yasm_test_asm_1 PRIVATE ${SOURCE_DIR}/yasm_test.asm)

set_source_files_properties(${SOURCE_DIR}/nasm_test.asm PROPERTIES LANGUAGE ASM_NASM)
add_library(nasm_test_asm_1 OBJECT ${SOURCE_DIR}/nasm_test.asm)
set_target_properties(nasm_test_asm_1 PROPERTIES LINKER_LANGUAGE ASM_MASM)
target_compile_options(nasm_test_asm_1 PRIVATE -fwin32 -DNASM_MODE=1)

set_source_files_properties(${SOURCE_DIR}/masm_test.asm PROPERTIES LANGUAGE ASM_MASM)
add_library(masm_test_asm_1 OBJECT ${SOURCE_DIR}/masm_test.asm)
set_target_properties(masm_test_asm_1 PROPERTIES LINKER_LANGUAGE ASM_MASM)
target_compile_options(masm_test_asm_1 PRIVATE -DMASM_MODE=1)

add_library(test1 SHARED
    $<TARGET_OBJECTS:yasm_test_asm_1>
    $<TARGET_OBJECTS:nasm_test_asm_1>
    $<TARGET_OBJECTS:masm_test_asm_1>
)
set_target_properties(test1 PROPERTIES LINKER_LANGUAGE ASM_MASM)

add_library(yasm_test_asm_2 OBJECT )
set_target_properties(yasm_test_asm_2 PROPERTIES LINKER_LANGUAGE ASM_MASM)
target_compile_options(yasm_test_asm_2 PRIVATE -pnasm -rnasm -fwin32 -mx86 -DYASM_MODE=2)
target_yasm_sources(yasm_test_asm_2 PRIVATE ${SOURCE_DIR}/yasm_test.asm)

set_source_files_properties(${SOURCE_DIR}/nasm_test.asm PROPERTIES LANGUAGE ASM_NASM)
add_library(nasm_test_asm_2 OBJECT ${SOURCE_DIR}/nasm_test.asm)
set_target_properties(nasm_test_asm_2 PROPERTIES LINKER_LANGUAGE ASM_MASM)
target_compile_options(nasm_test_asm_2 PRIVATE -fwin32 -DNASM_MODE=2)

add_library(yasm_test_asm_3 OBJECT )
set_target_properties(yasm_test_asm_3 PROPERTIES LINKER_LANGUAGE ASM_MASM)
target_compile_options(yasm_test_asm_3 PRIVATE -pnasm -rnasm -fwin32 -mx86 -DYASM_MODE=2)
target_include_directories(yasm_test_asm_3 PRIVATE ${SOURCE_DIR})
target_yasm_sources(yasm_test_asm_3 PRIVATE ${SOURCE_DIR}/yasm_test.asm)

set_source_files_properties(${SOURCE_DIR}/masm_test.asm PROPERTIES LANGUAGE ASM_MASM)
add_library(masm_test_asm_2 OBJECT ${SOURCE_DIR}/masm_test.asm)
set_target_properties(masm_test_asm_2 PROPERTIES LINKER_LANGUAGE ASM_MASM)
target_compile_options(masm_test_asm_2 PRIVATE -DMASM_MODE=2)

add_library(test2 SHARED
    $<TARGET_OBJECTS:yasm_test_asm_2>
    $<TARGET_OBJECTS:nasm_test_asm_2>
    $<TARGET_OBJECTS:yasm_test_asm_3>
    $<TARGET_OBJECTS:masm_test_asm_1>
    $<TARGET_OBJECTS:masm_test_asm_2>
)
set_target_properties(test2 PROPERTIES LINKER_LANGUAGE ASM_MASM)
