cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
language_compile_options(C -DC=1)
language_include_directories(C ${CMAKE_CURRENT_BINARY_DIR}/include_a)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include_a)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include_b)

add_library(shared SHARED ${SOURCE_DIR}/c1.c ${SOURCE_DIR}/cpp1.cpp)
target_language_compile_options(shared C PRIVATE -DF1)
target_language_include_directories(shared C PRIVATE ${CMAKE_CURRENT_BINARY_DIR})

add_executable(app ${SOURCE_DIR}/c2.c)
target_compile_options(app PRIVATE -DF2)
target_include_directories(app PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/include_b)
