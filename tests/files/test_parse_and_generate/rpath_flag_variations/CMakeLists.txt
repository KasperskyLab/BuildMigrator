cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/1)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/link)

add_library(a SHARED ${SOURCE_DIR}/1.c)
target_link_options(a PRIVATE
    -Wl,-rpath
    -Wl,${CMAKE_CURRENT_BINARY_DIR}/1
    -Wl,-rpath-link
    -Wl,${CMAKE_CURRENT_BINARY_DIR}/link
)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/2)

add_library(b SHARED ${SOURCE_DIR}/2.c)
target_link_options(b PRIVATE
    -Wl,-rpath-link,${CMAKE_CURRENT_BINARY_DIR}/link
    -Wl,-rpath,${CMAKE_CURRENT_BINARY_DIR}/2
)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/3)

add_library(c SHARED ${SOURCE_DIR}/3.c)
target_link_options(c PRIVATE
    -Wl,--rpath
    -Wl,${CMAKE_CURRENT_BINARY_DIR}/3
    -Wl,--rpath-link
    -Wl,${CMAKE_CURRENT_BINARY_DIR}/link
)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/4)

add_library(d SHARED ${SOURCE_DIR}/4.c)
target_link_options(d PRIVATE
    -Wl,--rpath,${CMAKE_CURRENT_BINARY_DIR}/4
    -Wl,--rpath-link,${CMAKE_CURRENT_BINARY_DIR}/link
)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/5)

add_library(e SHARED ${SOURCE_DIR}/5.c)
target_link_options(e PRIVATE
    -Wl,--rpath=${CMAKE_CURRENT_BINARY_DIR}/5
    -Wl,--rpath-link=${CMAKE_CURRENT_BINARY_DIR}/link
)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/6)

add_library(f_so SHARED ${SOURCE_DIR}/6.c)
target_link_options(f_so PRIVATE
    -Wl,-rpath=${CMAKE_CURRENT_BINARY_DIR}/6
    -Wl,-rpath-link=${CMAKE_CURRENT_BINARY_DIR}/link
)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/7)

add_library(g SHARED ${SOURCE_DIR}/7.c)
target_link_options(g PRIVATE
    -rpath
    ${CMAKE_CURRENT_BINARY_DIR}/7
    -rpath-link
    ${CMAKE_CURRENT_BINARY_DIR}/link
)
