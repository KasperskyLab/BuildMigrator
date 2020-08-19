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

set_source_files_properties(${SOURCE_DIR}/3.asm PROPERTIES LANGUAGE ASM_MASM)
set_source_files_properties(${SOURCE_DIR}/4.asm PROPERTIES LANGUAGE ASM_NASM)
add_executable(out
    ${SOURCE_DIR}/1.c
    ${SOURCE_DIR}/2.cpp
    ${SOURCE_DIR}/3.asm
    ${SOURCE_DIR}/4.asm
    ${SOURCE_DIR}/5.rc
)
target_yasm_sources(out PRIVATE ${SOURCE_DIR}/6.asm)
