cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(main_o OBJECT ${SOURCE_DIR}/main.c)

add_executable(a.out ${SOURCE_DIR}/main.c)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/libs)

add_library(libs_a_out SHARED ${SOURCE_DIR}/main.c)
set_target_output_subdir(libs_a_out LIBRARY_OUTPUT_DIRECTORY libs)
set_target_output_subdir(libs_a_out RUNTIME_OUTPUT_DIRECTORY libs)
