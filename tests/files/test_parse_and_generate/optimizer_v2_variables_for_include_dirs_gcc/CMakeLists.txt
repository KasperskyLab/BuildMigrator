cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)
enable_language(ASM)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(include_dirs_1
    ${CMAKE_CURRENT_BINARY_DIR}/aaaaaaaaaaaaaaaaaaaaaa
    ${CMAKE_CURRENT_BINARY_DIR}/bbbbbbbbbbbbbbbbbbb
)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/aaaaaaaaaaaaaaaaaaaaaa)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/bbbbbbbbbbbbbbbbbbb)

set_source_files_properties(${SOURCE_DIR}/1.c PROPERTIES INCLUDE_DIRECTORIES "${include_dirs_1}")
set_source_files_properties(${SOURCE_DIR}/3.cpp PROPERTIES INCLUDE_DIRECTORIES "${include_dirs_1}")
set_source_files_properties(${SOURCE_DIR}/5.S PROPERTIES INCLUDE_DIRECTORIES "${include_dirs_1}")
add_executable(test
    ${SOURCE_DIR}/1.c
    ${SOURCE_DIR}/2.c
    ${SOURCE_DIR}/3.cpp
    ${SOURCE_DIR}/4.cpp
    ${SOURCE_DIR}/5.S
    ${SOURCE_DIR}/6.S
)
