cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/libs)

set_source_files_properties(${SOURCE_DIR}/foo.c PROPERTIES INCLUDE_DIRECTORIES "${SOURCE_DIR}")
add_library(foo SHARED ${SOURCE_DIR}/foo.c)
