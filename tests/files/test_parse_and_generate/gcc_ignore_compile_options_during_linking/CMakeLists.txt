cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

set_source_files_properties(${SOURCE_DIR}/main.c PROPERTIES COMPILE_OPTIONS "-fPIC;-fPIE")
add_executable(test ${SOURCE_DIR}/main.c)
target_link_options(test PRIVATE -pie)
