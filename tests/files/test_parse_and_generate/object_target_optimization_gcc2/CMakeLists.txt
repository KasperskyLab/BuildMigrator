cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/shared)

add_library(object_lib_1 OBJECT ${SOURCE_DIR}/a.c ${SOURCE_DIR}/b.c)

add_library(sh1 SHARED $<TARGET_OBJECTS:object_lib_1>)
set_target_properties(sh1 PROPERTIES LINKER_LANGUAGE C)

add_library(sh2 SHARED $<TARGET_OBJECTS:object_lib_1>)
set_target_properties(sh2 PROPERTIES LINKER_LANGUAGE C)
target_link_options(sh2 PRIVATE -Wl,-z,relro)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/static)

add_library(object_lib_2 OBJECT ${SOURCE_DIR}/a.c ${SOURCE_DIR}/b.c)
target_compile_options(object_lib_2 PRIVATE -DSTATIC)

add_library(st.static STATIC $<TARGET_OBJECTS:object_lib_2>)
set_target_properties(st.static PROPERTIES LINKER_LANGUAGE C)
set_target_properties(st.static PROPERTIES OUTPUT_NAME st)
