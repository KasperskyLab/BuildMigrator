cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

set_source_files_properties(${SOURCE_DIR}/1.obj PROPERTIES EXTERNAL_OBJECT ON)
add_library(a.static STATIC ${SOURCE_DIR}/1.obj)
set_target_properties(a.static PROPERTIES LINKER_LANGUAGE CXX)
target_link_options(a.static PRIVATE /ignore:4221)
set_target_properties(a.static PROPERTIES OUTPUT_NAME liba)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/2.o ${CMAKE_CURRENT_BINARY_DIR}/2.o COPYONLY)

set_source_files_properties(${CMAKE_CURRENT_BINARY_DIR}/2.o PROPERTIES EXTERNAL_OBJECT ON)
add_library(b.static STATIC ${CMAKE_CURRENT_BINARY_DIR}/2.o)
set_target_properties(b.static PROPERTIES LINKER_LANGUAGE CXX)
target_link_options(b.static PRIVATE /ignore:4221)
set_target_properties(b.static PROPERTIES OUTPUT_NAME libb)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/dir/3.obj ${CMAKE_CURRENT_BINARY_DIR}/dir/3.obj COPYONLY)

set_source_files_properties(${CMAKE_CURRENT_BINARY_DIR}/dir/3.obj PROPERTIES EXTERNAL_OBJECT ON)
add_library(c SHARED ${CMAKE_CURRENT_BINARY_DIR}/dir/3.obj)
set_target_properties(c PROPERTIES LINKER_LANGUAGE CXX)
target_link_options(c PRIVATE /ignore:4221)
set_target_properties(c PROPERTIES OUTPUT_NAME libc)

set_source_files_properties(${CMAKE_CURRENT_BINARY_DIR}/2.o PROPERTIES EXTERNAL_OBJECT ON)
add_library(d SHARED ${SOURCE_DIR}/a.cpp ${CMAKE_CURRENT_BINARY_DIR}/2.o)
target_link_options(d PRIVATE /ignore:4221)
target_link_libraries(d PRIVATE c)
set_target_properties(d PROPERTIES OUTPUT_NAME libd)
