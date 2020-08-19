cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/arm64.h ${CMAKE_CURRENT_BINARY_DIR}/arm64.h COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/armv7s.h ${CMAKE_CURRENT_BINARY_DIR}/armv7s.h COPYONLY)

add_executable(test ${SOURCE_DIR}/test.c)
target_include_directories(test PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
