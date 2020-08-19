cmake_minimum_required(VERSION 3.13)

project(PROJECT LANGUAGES)
enable_language(ASM_MASM)
enable_language(ASM_NASM)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(CMAKE_ASM_NASM_OBJECT_FORMAT " win64")

set_source_files_properties(${SOURCE_DIR}/embedded.S PROPERTIES LANGUAGE ASM_MASM)
set_source_files_properties(${SOURCE_DIR}/aes-x86_64.asm PROPERTIES LANGUAGE ASM_NASM)
set_source_files_properties(${SOURCE_DIR}/aes-x86_64.asm PROPERTIES COMPILE_OPTIONS -DNEAR)
set_source_files_properties(${SOURCE_DIR}/embedded.S PROPERTIES COMPILE_OPTIONS "/W3;/errorReport:prompt")
add_library(test.static STATIC ${SOURCE_DIR}/aes-x86_64.asm ${SOURCE_DIR}/embedded.S)
set_target_properties(test.static PROPERTIES LINKER_LANGUAGE ASM_MASM)
set_target_properties(test.static PROPERTIES OUTPUT_NAME test)
