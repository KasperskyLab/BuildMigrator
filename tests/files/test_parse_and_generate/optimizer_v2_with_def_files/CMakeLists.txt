cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(test1 SHARED ${SOURCE_DIR}/1.c ${SOURCE_DIR}/2.c ${SOURCE_DIR}/3.c)
target_link_options(test1 PRIVATE /def:${SOURCE_DIR}/1.def)
target_compile_options(test1 PRIVATE -DTEST=1)

add_library(test2 SHARED ${SOURCE_DIR}/4.c)
target_compile_options(test2 PRIVATE -DTEST=2)
