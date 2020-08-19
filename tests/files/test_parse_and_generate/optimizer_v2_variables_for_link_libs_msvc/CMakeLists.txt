cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(libs_1 aaaaaaaaaaaaaaaaaa bbbbbbbbbbbbbbbbbbbbbbbb)

add_library(static1.static STATIC ${SOURCE_DIR}/a.c)
set_target_properties(static1.static PROPERTIES OUTPUT_NAME static1)

add_library(shared1 SHARED ${SOURCE_DIR}/b.c)
target_link_libraries(shared1 PRIVATE static1.static ${libs_1})

add_library(shared2 SHARED ${SOURCE_DIR}/c.c)

add_executable(exe1 ${SOURCE_DIR}/d.c)
target_link_libraries(exe1 PRIVATE static1.static ${libs_1})

add_executable(exe2 ${SOURCE_DIR}/e.c)
