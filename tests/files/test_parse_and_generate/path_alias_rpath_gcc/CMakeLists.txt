cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(RPATH_PATH_ROOT /some/path CACHE STRING "")

add_library(a SHARED ${SOURCE_DIR}/main.cpp)
target_link_options(a PRIVATE "-Wl,-rpath -Wl,${RPATH_PATH_ROOT}/lib")
