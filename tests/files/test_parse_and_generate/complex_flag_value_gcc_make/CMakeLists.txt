cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

set_source_files_properties(${SOURCE_DIR}/test1.cpp PROPERTIES COMPILE_OPTIONS "-DVALUES1={ \"1.a\", \"2.b\", \"3.c\" }")
set_source_files_properties(${SOURCE_DIR}/test2.cpp PROPERTIES COMPILE_OPTIONS "-DVALUES2={ 1.a, 2.b, 3.c }")
set_source_files_properties(${SOURCE_DIR}/test3.cpp PROPERTIES COMPILE_OPTIONS "-DVALUES3={ \"1.a\", \"2.b\", \"3.c\" }")
add_library(test SHARED
    ${SOURCE_DIR}/test1.cpp
    ${SOURCE_DIR}/test2.cpp
    ${SOURCE_DIR}/test3.cpp
)
