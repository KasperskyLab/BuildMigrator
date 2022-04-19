cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/c)

add_library(a SHARED ${SOURCE_DIR}/foo.c)
set_target_output_subdir(a LIBRARY_OUTPUT_DIRECTORY c)
set_target_output_subdir(a RUNTIME_OUTPUT_DIRECTORY c)
set_target_properties(a PROPERTIES VERSION 1.2.3)
set_target_properties(a PROPERTIES SOVERSION 1)

add_library(b SHARED ${SOURCE_DIR}/foo.c)
set_target_output_subdir(b LIBRARY_OUTPUT_DIRECTORY c)
set_target_output_subdir(b RUNTIME_OUTPUT_DIRECTORY c)
set_target_properties(b PROPERTIES VERSION 1.2.3)
set_target_properties(b PROPERTIES SOVERSION 1)

add_library(c SHARED ${SOURCE_DIR}/foo.c)
set_target_output_subdir(c LIBRARY_OUTPUT_DIRECTORY c)
set_target_output_subdir(c RUNTIME_OUTPUT_DIRECTORY c)
set_target_properties(c PROPERTIES VERSION 1.2.3)
set_target_properties(c PROPERTIES SOVERSION 1)

add_library(d SHARED ${SOURCE_DIR}/foo.c)
set_target_output_subdir(d LIBRARY_OUTPUT_DIRECTORY c)
set_target_output_subdir(d RUNTIME_OUTPUT_DIRECTORY c)
set_target_properties(d PROPERTIES VERSION 1.2)
set_target_properties(d PROPERTIES SOVERSION 1)

add_library(e SHARED ${SOURCE_DIR}/foo.c)
set_target_output_subdir(e LIBRARY_OUTPUT_DIRECTORY c)
set_target_output_subdir(e RUNTIME_OUTPUT_DIRECTORY c)
set_target_properties(e PROPERTIES VERSION 1)
set_target_properties(e PROPERTIES SOVERSION 1)

add_library(f SHARED ${SOURCE_DIR}/foo.c)
set_target_output_subdir(f LIBRARY_OUTPUT_DIRECTORY c)
set_target_output_subdir(f RUNTIME_OUTPUT_DIRECTORY c)
set_target_properties(f PROPERTIES VERSION 1)
