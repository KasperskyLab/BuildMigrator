cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(foo.static STATIC ${SOURCE_DIR}/foo.c)
set_target_properties(foo.static PROPERTIES OUTPUT_NAME foo)
set_target_output_subdir(foo.static ARCHIVE_OUTPUT_DIRECTORY out)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/out)

add_library(foo SHARED ${SOURCE_DIR}/foo.c)
set_target_output_subdir(foo LIBRARY_OUTPUT_DIRECTORY out)
set_target_output_subdir(foo RUNTIME_OUTPUT_DIRECTORY out)
