cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(foo SHARED ${SOURCE_DIR}/foo.c)

add_library(foo.static STATIC ${SOURCE_DIR}/foo.c)
set_target_properties(foo.static PROPERTIES OUTPUT_NAME foo)
