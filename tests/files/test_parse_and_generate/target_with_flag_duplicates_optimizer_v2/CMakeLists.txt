cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
add_compile_options(-DA=B)
language_include_directories(C ${CMAKE_CURRENT_BINARY_DIR}/i1)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/i1)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/i2)

set_source_files_properties(${SOURCE_DIR}/foo.c PROPERTIES COMPILE_OPTIONS -DFOO)
set_source_files_properties(${SOURCE_DIR}/baz.c PROPERTIES COMPILE_OPTIONS -DBAZ)
set_source_files_properties(${SOURCE_DIR}/baz.c PROPERTIES INCLUDE_DIRECTORIES ${CMAKE_CURRENT_BINARY_DIR}/i2)
add_library(test SHARED
    ${SOURCE_DIR}/foo.c
    ${SOURCE_DIR}/bar.cpp
    ${SOURCE_DIR}/baz.c
)
target_language_compile_options(test CXX PRIVATE -DBAR)
target_language_include_directories(test CXX PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/i2)
