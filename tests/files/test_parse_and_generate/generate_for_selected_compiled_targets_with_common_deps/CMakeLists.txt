cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(c.static STATIC ${SOURCE_DIR}/c.c)
set_target_properties(c.static PROPERTIES OUTPUT_NAME c)

add_executable(app_a ${SOURCE_DIR}/a.c)
target_link_libraries(app_a PRIVATE c.static)

add_executable(app_b ${SOURCE_DIR}/b.c)
target_link_libraries(app_b PRIVATE c.static)
