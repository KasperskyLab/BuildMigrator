cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(EXTERNAL_LIB_A external.a.static CACHE STRING "")
set(EXTERNAL_LIB_B external.b.static CACHE STRING "")
set(EXTERNAL_LIB_C external.c.static CACHE STRING "")
set(EXTERNAL_LIB_D external.d.static CACHE STRING "")
set(EXTERNAL_INCLUDE_A ${CMAKE_CURRENT_BINARY_DIR}/include/a CACHE STRING "")
set(EXTERNAL_INCLUDE_B ${CMAKE_CURRENT_BINARY_DIR}/include/b CACHE STRING "")
set(EXTERNAL_INCLUDE_C ${CMAKE_CURRENT_BINARY_DIR}/include/c CACHE STRING "")
set(EXTERNAL_INCLUDE_D ${CMAKE_CURRENT_BINARY_DIR}/include/d CACHE STRING "")
include_directories(
    ${EXTERNAL_INCLUDE_A}
    ${EXTERNAL_INCLUDE_B}
    ${EXTERNAL_INCLUDE_C}
    ${EXTERNAL_INCLUDE_D}
)
link_libraries(
    ${EXTERNAL_LIB_A}
    ${EXTERNAL_LIB_B}
    ${EXTERNAL_LIB_C}
    ${EXTERNAL_LIB_D}
)

add_executable(test1 ${SOURCE_DIR}/test1.cpp)

add_executable(test2 ${SOURCE_DIR}/test2.cpp)

add_executable(test3 ${SOURCE_DIR}/test3.cpp)
