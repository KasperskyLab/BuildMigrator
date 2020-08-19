cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
configure_file("${CMAKE_CURRENT_LIST_DIR}/prebuilt/include dir/header.h" "${CMAKE_CURRENT_BINARY_DIR}/include dir/header.h" COPYONLY)
configure_file("${CMAKE_CURRENT_LIST_DIR}/prebuilt/lib dir/a.lib" "${CMAKE_CURRENT_BINARY_DIR}/lib dir/a.lib" COPYONLY)

set_source_files_properties(${SOURCE_DIR}/source file.cpp PROPERTIES INCLUDE_DIRECTORIES "${CMAKE_CURRENT_BINARY_DIR}/include dir")
add_library(b SHARED "${SOURCE_DIR}/source file.cpp")
target_link_libraries(b PRIVATE "${CMAKE_CURRENT_BINARY_DIR}/lib dir/a")
set_target_output_subdir(b RUNTIME_OUTPUT_DIRECTORY "lib dir")
set_target_output_subdir(b ARCHIVE_OUTPUT_DIRECTORY "lib dir")

add_library(c SHARED "${SOURCE_DIR}/source file.cpp")
target_link_libraries(c PRIVATE b)
