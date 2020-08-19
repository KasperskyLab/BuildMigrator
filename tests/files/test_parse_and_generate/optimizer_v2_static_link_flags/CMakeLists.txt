cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
static_library_options(/WX)

add_library(s1.static STATIC ${SOURCE_DIR}/1.c)
target_link_options(s1.static PRIVATE /LTCG)
set_target_properties(s1.static PROPERTIES OUTPUT_NAME s1)

add_library(s2.static STATIC ${SOURCE_DIR}/2.c)
set_target_properties(s2.static PROPERTIES OUTPUT_NAME s2)

add_executable(app ${SOURCE_DIR}/3.c)
