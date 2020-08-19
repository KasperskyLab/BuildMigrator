cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(a SHARED ${SOURCE_DIR}/a.c)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/libprebuilt.so ${CMAKE_CURRENT_BINARY_DIR}/libprebuilt.so COPYONLY)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/out)

add_library(b SHARED ${SOURCE_DIR}/b.cpp)
set_target_output_subdir(b LIBRARY_OUTPUT_DIRECTORY out)
set_target_output_subdir(b RUNTIME_OUTPUT_DIRECTORY out)
