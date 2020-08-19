cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/lib/libb.lib ${CMAKE_CURRENT_BINARY_DIR}/lib/libb.lib COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/libc.lib ${CMAKE_CURRENT_BINARY_DIR}/libc.lib COPYONLY)

add_library(d SHARED ${SOURCE_DIR}/src.cpp)
target_link_libraries(d PRIVATE
    ${SOURCE_DIR}/liba
    ${CMAKE_CURRENT_BINARY_DIR}/lib/libb
    ${CMAKE_CURRENT_BINARY_DIR}/libc
)
