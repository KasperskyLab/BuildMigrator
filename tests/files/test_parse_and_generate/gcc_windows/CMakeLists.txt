cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_executable(a ${SOURCE_DIR}/1.c)
target_include_directories(a PRIVATE F:/3rd_party/include)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/a/b/c/include)

add_executable(b ${SOURCE_DIR}/2.cpp)
target_include_directories(b PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/a/b/c/include)
