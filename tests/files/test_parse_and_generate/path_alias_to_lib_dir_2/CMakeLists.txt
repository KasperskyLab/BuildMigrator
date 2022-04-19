cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(LIB_DIR predictable_default_value CACHE STRING "")
link_libraries(
    ${LIB_DIR}/liba.a
    ${LIB_DIR}/libb.a
    ${LIB_DIR}/libc.a
    ${LIB_DIR}/libd.a
)

add_executable(test1 ${SOURCE_DIR}/test1.c)

add_executable(test2 ${SOURCE_DIR}/test1.c)

add_executable(test3 ${SOURCE_DIR}/test3.c)
