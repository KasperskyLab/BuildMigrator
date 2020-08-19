cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(a SHARED ${SOURCE_DIR}/a.cpp)
set_target_properties(a PROPERTIES OUTPUT_NAME liba)
set_target_properties(a PROPERTIES ARCHIVE_OUTPUT_NAME liba.dll)

add_library(b SHARED ${SOURCE_DIR}/a.cpp)
target_link_libraries(b PRIVATE a)
set_target_properties(b PROPERTIES OUTPUT_NAME libb)

add_library(c SHARED ${SOURCE_DIR}/a.cpp)
target_link_libraries(c PRIVATE b)
set_target_properties(c PROPERTIES OUTPUT_NAME libc)
