cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_executable(a1 ${SOURCE_DIR}/1.c)

add_executable(a2 ${SOURCE_DIR}/2.c)

add_executable(a3 ${SOURCE_DIR}/3.c)
