cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/Output Directory")

add_library(a SHARED "${SOURCE_DIR}/Source File.cpp")
set_target_output_subdir(a RUNTIME_OUTPUT_DIRECTORY "Output Directory")
set_target_output_subdir(a ARCHIVE_OUTPUT_DIRECTORY "Output Directory")

add_library(does_not_exist SHARED "${SOURCE_DIR}/Source File.cpp")
set_target_output_subdir(does_not_exist RUNTIME_OUTPUT_DIRECTORY "Output Directory")
set_target_output_subdir(does_not_exist ARCHIVE_OUTPUT_DIRECTORY "Output Directory")
