cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(EXTERNAL_DIR sqlite/src CACHE STRING "")

set_source_files_properties(${SOURCE_DIR}/a.c PROPERTIES INCLUDE_DIRECTORIES "${EXTERNAL_DIR}")
add_library(a.static STATIC ${SOURCE_DIR}/a.c)
set_target_properties(a.static PROPERTIES OUTPUT_NAME a)

set_source_files_properties(${SOURCE_DIR}/b.c PROPERTIES INCLUDE_DIRECTORIES "${EXTERNAL_DIR}")
add_library(b SHARED ${SOURCE_DIR}/b.c)
set_target_properties(b PROPERTIES VERSION 2.0.1)
set_target_properties(b PROPERTIES SOVERSION 2)
