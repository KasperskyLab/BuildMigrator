cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

set_source_files_properties(${SOURCE_DIR}/1.o PROPERTIES EXTERNAL_OBJECT ON)
add_library(a.static STATIC ${SOURCE_DIR}/1.o)
set_target_properties(a.static PROPERTIES LINKER_LANGUAGE CXX)
set_target_properties(a.static PROPERTIES OUTPUT_NAME a)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/2.o ${CMAKE_CURRENT_BINARY_DIR}/2.o COPYONLY)

set_source_files_properties(${CMAKE_CURRENT_BINARY_DIR}/2.o PROPERTIES EXTERNAL_OBJECT ON)
add_library(b SHARED ${CMAKE_CURRENT_BINARY_DIR}/2.o)
set_target_properties(b PROPERTIES LINKER_LANGUAGE CXX)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/dir/3.o ${CMAKE_CURRENT_BINARY_DIR}/dir/3.o COPYONLY)

set_source_files_properties(${CMAKE_CURRENT_BINARY_DIR}/dir/3.o PROPERTIES EXTERNAL_OBJECT ON)
add_library(c SHARED ${SOURCE_DIR}/a.cpp ${CMAKE_CURRENT_BINARY_DIR}/dir/3.o)
target_link_libraries(c PRIVATE b)
