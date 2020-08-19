cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(setargv.static STATIC ${SOURCE_DIR}/a.cpp)
target_link_options(setargv.static PRIVATE setargv.obj)
set_target_properties(setargv.static PROPERTIES OUTPUT_NAME setargv)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/libs/setargv.obj ${CMAKE_CURRENT_BINARY_DIR}/libs/setargv.obj COPYONLY)

set_source_files_properties(${CMAKE_CURRENT_BINARY_DIR}/libs/setargv.obj PROPERTIES EXTERNAL_OBJECT ON)
add_library(local_setargv.static STATIC
    ${SOURCE_DIR}/a.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/libs/setargv.obj
)
set_target_properties(local_setargv.static PROPERTIES OUTPUT_NAME local_setargv)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/libs/wsetargv.obj ${CMAKE_CURRENT_BINARY_DIR}/libs/wsetargv.obj COPYONLY)

set_source_files_properties(${CMAKE_CURRENT_BINARY_DIR}/libs/wsetargv.obj PROPERTIES EXTERNAL_OBJECT ON)
add_library(local_wsetargv SHARED
    ${SOURCE_DIR}/b.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/libs/wsetargv.obj
)

add_library(wsetargv SHARED ${SOURCE_DIR}/b.cpp)
target_link_options(wsetargv PRIVATE wsetargv.obj)
