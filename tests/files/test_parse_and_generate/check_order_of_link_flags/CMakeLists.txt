cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(cap-ng SHARED ${SOURCE_DIR}/cap-ng.c)
target_link_options(cap-ng PRIVATE -g -Wl,-z -Wl,relro)
set_target_properties(cap-ng PROPERTIES VERSION 0.0.0)
set_target_properties(cap-ng PROPERTIES SOVERSION 0)
