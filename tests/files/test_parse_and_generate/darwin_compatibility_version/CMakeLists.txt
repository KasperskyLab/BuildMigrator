cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/lib)

add_library(a SHARED ${SOURCE_DIR}/foo.c)
set_target_output_subdir(a LIBRARY_OUTPUT_DIRECTORY lib)
set_target_output_subdir(a RUNTIME_OUTPUT_DIRECTORY lib)
set_target_properties(a PROPERTIES VERSION 1.2.3)
set_target_properties(a PROPERTIES SOVERSION 1)

add_library(b SHARED ${SOURCE_DIR}/foo.c)
set_target_output_subdir(b LIBRARY_OUTPUT_DIRECTORY lib)
set_target_output_subdir(b RUNTIME_OUTPUT_DIRECTORY lib)
set_target_properties(b PROPERTIES VERSION 4.5)
set_target_properties(b PROPERTIES SOVERSION 4)

add_library(c SHARED ${SOURCE_DIR}/foo.c)
set_target_output_subdir(c LIBRARY_OUTPUT_DIRECTORY lib)
set_target_output_subdir(c RUNTIME_OUTPUT_DIRECTORY lib)
set_target_properties(c PROPERTIES VERSION 6)
set_target_properties(c PROPERTIES SOVERSION 6)

add_library(d SHARED ${SOURCE_DIR}/foo.c)
set_target_output_subdir(d LIBRARY_OUTPUT_DIRECTORY lib)
set_target_output_subdir(d RUNTIME_OUTPUT_DIRECTORY lib)
set_target_properties(d PROPERTIES VERSION 7)
