cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)
enable_language(ASM_MASM)
enable_language(ASM_NASM)
enable_language(RC)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(CMAKE_ASM_YASM_OBJECT_FORMAT win32)
set(CMAKE_ASM_NASM_OBJECT_FORMAT win32)
set(include_dirs_1
    ${CMAKE_CURRENT_BINARY_DIR}/aaaaaaaaaaaaaaaaaaaaaa
    ${CMAKE_CURRENT_BINARY_DIR}/bbbbbbbbbbbbbbbbbbb
)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/aaaaaaaaaaaaaaaaaaaaaa)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/bbbbbbbbbbbbbbbbbbb)

set_source_files_properties(${SOURCE_DIR}/5.asm ${SOURCE_DIR}/6.asm PROPERTIES LANGUAGE ASM_MASM)
set_source_files_properties(${SOURCE_DIR}/7.asm ${SOURCE_DIR}/8.asm PROPERTIES LANGUAGE ASM_NASM)
set_source_files_properties(${SOURCE_DIR}/1.cpp PROPERTIES INCLUDE_DIRECTORIES "${include_dirs_1}")
set_source_files_properties(${SOURCE_DIR}/3.c PROPERTIES INCLUDE_DIRECTORIES "${include_dirs_1}")
set_source_files_properties(${SOURCE_DIR}/5.asm PROPERTIES INCLUDE_DIRECTORIES "${include_dirs_1}")
set_source_files_properties(${SOURCE_DIR}/7.asm PROPERTIES INCLUDE_DIRECTORIES "${include_dirs_1}")
set_source_files_properties(${SOURCE_DIR}/9.rc PROPERTIES INCLUDE_DIRECTORIES "${include_dirs_1}")
set_source_files_properties(${SOURCE_DIR}/11.asm PROPERTIES INCLUDE_DIRECTORIES "${include_dirs_1}")
add_executable(test
    ${SOURCE_DIR}/1.cpp
    ${SOURCE_DIR}/2.cpp
    ${SOURCE_DIR}/3.c
    ${SOURCE_DIR}/4.c
    ${SOURCE_DIR}/5.asm
    ${SOURCE_DIR}/6.asm
    ${SOURCE_DIR}/7.asm
    ${SOURCE_DIR}/8.asm
    ${SOURCE_DIR}/9.rc
    ${SOURCE_DIR}/10.rc
)
target_yasm_sources(test PRIVATE ${SOURCE_DIR}/11.asm ${SOURCE_DIR}/12.asm)
