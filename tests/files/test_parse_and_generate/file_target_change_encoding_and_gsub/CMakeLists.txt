cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/ui_unscaled_resources.rc ${CMAKE_CURRENT_BINARY_DIR}/ui_unscaled_resources.rc COPYONLY)

add_library(test SHARED ${SOURCE_DIR}/foo.c)
