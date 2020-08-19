cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(test_cpp_1 OBJECT ${SOURCE_DIR}/test.cpp)
target_compile_options(test_cpp_1 PRIVATE -DMODE=1 /GR-)

add_library(test_cpp_2 OBJECT ${SOURCE_DIR}/test.cpp)
target_compile_options(test_cpp_2 PRIVATE -DMODE=2)

add_library(test_c_1 OBJECT ${SOURCE_DIR}/test.c)
target_compile_options(test_c_1 PRIVATE -DCMODE=1)

add_library(test1 SHARED
    $<TARGET_OBJECTS:test_cpp_1>
    $<TARGET_OBJECTS:test_cpp_2>
    $<TARGET_OBJECTS:test_c_1>
)
set_target_properties(test1 PROPERTIES LINKER_LANGUAGE C)

add_library(test_cpp_3 OBJECT ${SOURCE_DIR}/test.cpp)
target_compile_options(test_cpp_3 PRIVATE -DMODE=2)
target_include_directories(test_cpp_3 PRIVATE ${SOURCE_DIR})

add_library(test_c_2 OBJECT ${SOURCE_DIR}/test.c)
target_compile_options(test_c_2 PRIVATE -DCMODE=2)

add_library(test2 SHARED
    $<TARGET_OBJECTS:test_cpp_3>
    $<TARGET_OBJECTS:test_c_1>
    $<TARGET_OBJECTS:test_c_2>
)
set_target_properties(test2 PROPERTIES LINKER_LANGUAGE C)
