cmake_minimum_required(VERSION 3.13)

project(PROJECT C)
enable_language(ASM_NASM)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(CMAKE_ASM_NASM_OBJECT_FORMAT win32)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/setup.asm ${CMAKE_CURRENT_BINARY_DIR}/setup.asm COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/include/f1.inc ${CMAKE_CURRENT_BINARY_DIR}/include/f1.inc COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/include/f2.inc ${CMAKE_CURRENT_BINARY_DIR}/include/f2.inc COPYONLY)

set_source_files_properties(${SOURCE_DIR}/main.asm PROPERTIES COMPILE_OPTIONS "-DA=B;-P${CMAKE_CURRENT_BINARY_DIR}/setup.asm")
set_source_files_properties(${SOURCE_DIR}/main.asm PROPERTIES INCLUDE_DIRECTORIES ${CMAKE_CURRENT_BINARY_DIR}/include)
add_executable(app ${SOURCE_DIR}/main.asm ${SOURCE_DIR}/main.c)
