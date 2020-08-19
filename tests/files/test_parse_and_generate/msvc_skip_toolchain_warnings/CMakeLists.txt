cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)
enable_language(RC)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include)

set_source_files_properties(${SOURCE_DIR}/version.rc PROPERTIES INCLUDE_DIRECTORIES ${CMAKE_CURRENT_BINARY_DIR}/include)
add_library(test SHARED ${SOURCE_DIR}/version.rc ${SOURCE_DIR}/test.cpp)
set_target_properties(test PROPERTIES ARCHIVE_OUTPUT_NAME test.dll)
