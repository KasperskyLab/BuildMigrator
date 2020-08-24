cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
add_compile_options(-DTEST=1)
include_directories(${CMAKE_CURRENT_BINARY_DIR}/include)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/include/a.h ${CMAKE_CURRENT_BINARY_DIR}/include/a.h COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/external/C_/somedir/1.def C:/somedir/1.def COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/external/X_/a/b/c/2.tmp X:/a/b/c/2.tmp COPYONLY)

add_library(test1 SHARED ${SOURCE_DIR}/1.c)
target_link_options(test1 PRIVATE /def:C:/somedir/1.def)

add_library(test2 SHARED ${SOURCE_DIR}/1.c)
target_link_options(test2 PRIVATE /def:X:/a/b/c/2.tmp)
