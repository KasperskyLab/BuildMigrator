cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(foo SHARED ${SOURCE_DIR}/foo.c)
target_link_options(foo PRIVATE -unknown-link-flag)
target_compile_options(foo PRIVATE -DFOO=1 -unknown-compile-flag)
