cmake_minimum_required(VERSION 3.13)

project(PROJECT C)
enable_language(ASM_MASM)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/include/f1.inc ${CMAKE_CURRENT_BINARY_DIR}/include/f1.inc COPYONLY)

set_source_files_properties(${SOURCE_DIR}/main.asm PROPERTIES INCLUDE_DIRECTORIES ${CMAKE_CURRENT_BINARY_DIR}/include)
add_executable(app ${SOURCE_DIR}/main.asm ${SOURCE_DIR}/main.c)
