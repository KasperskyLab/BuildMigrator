cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

set(copy_prebuilt_artifacts_DIR prebuilt)
set(copy_prebuilt_artifacts_DEST ${CMAKE_CURRENT_BINARY_DIR})
file(GLOB_RECURSE _files RELATIVE ${CMAKE_CURRENT_LIST_DIR}/${copy_prebuilt_artifacts_DIR} ${copy_prebuilt_artifacts_DIR}/*)
foreach(_f ${_files})
    configure_file(${copy_prebuilt_artifacts_DIR}/${_f} ${copy_prebuilt_artifacts_DEST}/${_f} COPYONLY)
endforeach()

add_library(test SHARED ${CMAKE_CURRENT_BINARY_DIR}/foo.c)
