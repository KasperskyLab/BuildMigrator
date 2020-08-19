cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/include/src.h ${CMAKE_CURRENT_BINARY_DIR}/include/src.h COPYONLY)

set_source_files_properties(${SOURCE_DIR}/src.cpp PROPERTIES INCLUDE_DIRECTORIES ${CMAKE_CURRENT_BINARY_DIR}/include)
add_executable(app ${SOURCE_DIR}/src.cpp)
