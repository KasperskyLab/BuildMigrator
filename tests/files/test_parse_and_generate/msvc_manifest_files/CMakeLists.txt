cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/common_controls.manifest ${CMAKE_CURRENT_BINARY_DIR}/common_controls.manifest COPYONLY)

add_executable(test
    ${SOURCE_DIR}/as_invoker.manifest
    ${CMAKE_CURRENT_BINARY_DIR}/common_controls.manifest
    ${SOURCE_DIR}/main.cpp
)
target_link_options(test PRIVATE /manifest:embed /manifestuac:no /SUBSYSTEM:CONSOLE,5.01)
