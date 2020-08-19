cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

set_source_files_properties(${SOURCE_DIR}/foo.c PROPERTIES COMPILE_OPTIONS -fPIC)
add_library(static.static STATIC ${SOURCE_DIR}/foo.c ${SOURCE_DIR}/static.c)
set_target_properties(static.static PROPERTIES OUTPUT_NAME static)

add_executable(main ${SOURCE_DIR}/main.c ${SOURCE_DIR}/foo.c)
