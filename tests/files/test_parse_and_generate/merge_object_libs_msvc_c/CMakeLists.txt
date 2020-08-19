cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(test1_c_1 OBJECT ${SOURCE_DIR}/test1.c)
target_compile_options(test1_c_1 PRIVATE -DCMODE=1)

add_library(test2_c_1 OBJECT ${SOURCE_DIR}/test2.c)
target_compile_options(test2_c_1 PRIVATE -DCMODE=1)

add_library(object_lib_1 OBJECT ${SOURCE_DIR}/test1.cpp ${SOURCE_DIR}/test2.cpp)
target_compile_options(object_lib_1 PRIVATE -DMODE=1 /GR-)

add_library(object_lib_2 OBJECT ${SOURCE_DIR}/test1.cpp ${SOURCE_DIR}/test2.cpp)
target_compile_options(object_lib_2 PRIVATE -DMODE=2)

add_library(test1 SHARED
    $<TARGET_OBJECTS:test1_c_1>
    $<TARGET_OBJECTS:test2_c_1>
    $<TARGET_OBJECTS:object_lib_1>
    $<TARGET_OBJECTS:object_lib_2>
)
set_target_properties(test1 PROPERTIES LINKER_LANGUAGE C)

add_library(test1_c_2 OBJECT ${SOURCE_DIR}/test1.c)
target_compile_options(test1_c_2 PRIVATE -DCMODE=2)

add_library(test2_c_2 OBJECT ${SOURCE_DIR}/test2.c)
target_compile_options(test2_c_2 PRIVATE -DCMODE=2)

add_library(object_lib_3 OBJECT ${SOURCE_DIR}/test1.cpp ${SOURCE_DIR}/test2.cpp)
target_compile_options(object_lib_3 PRIVATE -DMODE=2)
target_include_directories(object_lib_3 PRIVATE ${SOURCE_DIR})

add_library(test2 SHARED
    $<TARGET_OBJECTS:test1_c_1>
    $<TARGET_OBJECTS:test2_c_1>
    $<TARGET_OBJECTS:test1_c_2>
    $<TARGET_OBJECTS:test2_c_2>
    $<TARGET_OBJECTS:object_lib_3>
)
set_target_properties(test2 PROPERTIES LINKER_LANGUAGE C)

add_library(test3 SHARED
    $<TARGET_OBJECTS:test1_c_1>
    $<TARGET_OBJECTS:test1_c_2>
    $<TARGET_OBJECTS:object_lib_1>
)
set_target_properties(test3 PROPERTIES LINKER_LANGUAGE C)
