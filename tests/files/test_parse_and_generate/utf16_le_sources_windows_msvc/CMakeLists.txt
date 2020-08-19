cmake_minimum_required(VERSION 3.13)

project(PROJECT C)
enable_language(RC)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/test.cur ${CMAKE_CURRENT_BINARY_DIR}/test.cur COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/include/foo.h ${CMAKE_CURRENT_BINARY_DIR}/include/foo.h COPYONLY)

set_source_files_properties(${SOURCE_DIR}/main.c PROPERTIES INCLUDE_DIRECTORIES ${CMAKE_CURRENT_BINARY_DIR}/include)
add_executable(app ${SOURCE_DIR}/resources.rc ${SOURCE_DIR}/main.c)
