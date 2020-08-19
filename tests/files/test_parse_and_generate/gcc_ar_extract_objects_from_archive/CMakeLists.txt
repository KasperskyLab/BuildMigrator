cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(lib.static STATIC ${SOURCE_DIR}/object.c)
set_target_properties(lib.static PROPERTIES OUTPUT_NAME lib)

add_library(result.static STATIC ${SOURCE_DIR}/object.c)
set_target_properties(result.static PROPERTIES OUTPUT_NAME result)
