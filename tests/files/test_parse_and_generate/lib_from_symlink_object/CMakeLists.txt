cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

set_source_files_properties(${SOURCE_DIR}/object.c PROPERTIES COMPILE_OPTIONS -DHAVE_CONFIG_H)
add_library(lib.static STATIC ${SOURCE_DIR}/object.c)
set_target_properties(lib.static PROPERTIES OUTPUT_NAME lib)
