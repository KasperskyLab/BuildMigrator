cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(a1 SHARED ${SOURCE_DIR}/a.c)
target_compile_options(a1 PRIVATE -DA=1)

add_library(a2 SHARED ${SOURCE_DIR}/a.c)
target_compile_options(a2 PRIVATE -DA=2)

add_library(a3 SHARED ${SOURCE_DIR}/a.c)
target_compile_options(a3 PRIVATE -DA=3)
