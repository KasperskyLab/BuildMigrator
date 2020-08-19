cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}/source" CACHE PATH "")
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/a.c ${CMAKE_CURRENT_BINARY_DIR}/a.c COPYONLY)

add_executable(a1 ${CMAKE_CURRENT_BINARY_DIR}/a.c)

add_executable(a2 ${SOURCE_DIR}/a.c)
