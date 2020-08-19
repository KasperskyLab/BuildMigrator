cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/lib)

add_library(a SHARED ${SOURCE_DIR}/a.cpp)
set_target_output_subdir(a RUNTIME_OUTPUT_DIRECTORY lib)
set_target_output_subdir(a ARCHIVE_OUTPUT_DIRECTORY lib)

add_library(c SHARED ${SOURCE_DIR}/c.cpp)
target_link_libraries(c PRIVATE a b)
