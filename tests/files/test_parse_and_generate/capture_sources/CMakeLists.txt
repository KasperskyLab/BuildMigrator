cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_executable(a ${SOURCE_DIR}/a.c)
target_include_directories(a PRIVATE ${SOURCE_DIR}/include ${SOURCE_DIR})
