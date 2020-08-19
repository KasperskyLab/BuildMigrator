cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(a.static STATIC ${SOURCE_DIR}/a.c)
set_target_properties(a.static PROPERTIES OUTPUT_NAME a)

add_library(b SHARED ${SOURCE_DIR}/b.c)
target_link_options(b PRIVATE -Wl,--exclude-libs,liba.a)
target_link_libraries(b PRIVATE m a.static)
