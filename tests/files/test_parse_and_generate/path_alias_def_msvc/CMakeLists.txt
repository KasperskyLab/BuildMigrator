cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(DEF_FILE_ROOT some_path_to_external_dir CACHE STRING "")

add_library(main SHARED ${CMAKE_CURRENT_BINARY_DIR}/source/main.cpp)
target_link_options(main PRIVATE /def:${DEF_FILE_ROOT}/main.def)
