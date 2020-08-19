cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)
enable_language(ASM_MASM)
enable_language(ASM_NASM)
enable_language(RC)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(CMAKE_ASM_YASM_OBJECT_FORMAT win32)
set(CMAKE_ASM_YASM_MACHINE x86)
set(CMAKE_ASM_NASM_OBJECT_FORMAT win32)
set(compile_flags_1 -DAAAAAAAAAAA -DBBBBBBBBBBBB -DCCCCCCCCCCC)
language_compile_options(C /GR-)
language_compile_options(CXX /GR-)
language_compile_options(RC /w /l409)
language_compile_options(ASM_YASM -pnasm -rnasm)

set_source_files_properties(${SOURCE_DIR}/masm1.asm ${SOURCE_DIR}/masm2.asm PROPERTIES LANGUAGE ASM_MASM)
set_source_files_properties(${SOURCE_DIR}/nasm1.asm ${SOURCE_DIR}/nasm2.asm PROPERTIES LANGUAGE ASM_NASM)
set_source_files_properties(${SOURCE_DIR}/yasm1.asm PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${SOURCE_DIR}/nasm1.asm PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${SOURCE_DIR}/masm1.asm PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${SOURCE_DIR}/foo1.c PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${SOURCE_DIR}/bar1.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${SOURCE_DIR}/resource1.rc PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${SOURCE_DIR}/resource2.rc PROPERTIES COMPILE_OPTIONS /g511)
add_library(test SHARED
    ${SOURCE_DIR}/nasm1.asm
    ${SOURCE_DIR}/nasm2.asm
    ${SOURCE_DIR}/masm1.asm
    ${SOURCE_DIR}/masm2.asm
    ${SOURCE_DIR}/foo1.c
    ${SOURCE_DIR}/foo2.c
    ${SOURCE_DIR}/bar1.cpp
    ${SOURCE_DIR}/bar2.cpp
    ${SOURCE_DIR}/resource1.rc
    ${SOURCE_DIR}/resource2.rc
)
target_yasm_sources(test PRIVATE ${SOURCE_DIR}/yasm1.asm ${SOURCE_DIR}/yasm2.asm)
