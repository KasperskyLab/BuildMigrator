cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/utf-16-be.txt ${CMAKE_CURRENT_BINARY_DIR}/utf-16-be.txt COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/utf-8-sig.txt ${CMAKE_CURRENT_BINARY_DIR}/utf-8-sig.txt COPYONLY)

add_library(test SHARED ${SOURCE_DIR}/foo.c)
target_include_directories(test PRIVATE ${SOURCE_DIR})
