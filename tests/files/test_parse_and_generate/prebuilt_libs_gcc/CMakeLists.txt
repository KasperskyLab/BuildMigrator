cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/libb.so ${CMAKE_CURRENT_BINARY_DIR}/libb.so COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/lib/libc.a ${CMAKE_CURRENT_BINARY_DIR}/lib/libc.a COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/libd.a ${CMAKE_CURRENT_BINARY_DIR}/libd.a COPYONLY)

add_library(e SHARED ${SOURCE_DIR}/src.cpp)
target_link_libraries(e PRIVATE
    ${SOURCE_DIR}/liba.a
    ${CMAKE_CURRENT_BINARY_DIR}/libb.so
    ${CMAKE_CURRENT_BINARY_DIR}/lib/libc.a
    ${CMAKE_CURRENT_BINARY_DIR}/libd.a
)
