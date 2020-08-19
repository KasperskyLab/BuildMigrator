cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(foo_c_1 OBJECT ${SOURCE_DIR}/foo.c)

add_library(foo SHARED $<TARGET_OBJECTS:foo_c_1>)
set_target_properties(foo PROPERTIES LINKER_LANGUAGE C)

add_library(foo_c_2 OBJECT ${SOURCE_DIR}/foo.c)
target_compile_options(foo_c_2 PRIVATE -DSTATIC)

add_library(foo.static STATIC $<TARGET_OBJECTS:foo_c_2>)
set_target_properties(foo.static PROPERTIES LINKER_LANGUAGE C)
set_target_properties(foo.static PROPERTIES OUTPUT_NAME foo)
