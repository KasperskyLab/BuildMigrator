cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(a_c_1 OBJECT ${SOURCE_DIR}/a.c)

add_library(a_o OBJECT $<TARGET_OBJECTS:a_c_1>)
set_target_properties(a_o PROPERTIES LINKER_LANGUAGE C)

add_library(b_c_1 OBJECT ${SOURCE_DIR}/b.c)

add_library(a SHARED $<TARGET_OBJECTS:a_o> $<TARGET_OBJECTS:b_c_1>)
set_target_properties(a PROPERTIES LINKER_LANGUAGE C)

add_library(object_lib_1 OBJECT ${SOURCE_DIR}/a.c ${SOURCE_DIR}/b.c)
target_compile_options(object_lib_1 PRIVATE -DFOO)

add_library(a_foo SHARED $<TARGET_OBJECTS:object_lib_1>)
set_target_properties(a_foo PROPERTIES LINKER_LANGUAGE C)

add_library(a_mixed SHARED
    $<TARGET_OBJECTS:a_o>
    $<TARGET_OBJECTS:b_c_1>
    $<TARGET_OBJECTS:object_lib_1>
)
set_target_properties(a_mixed PROPERTIES LINKER_LANGUAGE C)

add_library(a3.o ALIAS a_o)
