cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(ZLIB_INCLUDE_DIR ${SOURCE_DIR}/zlib/include CACHE STRING "")
set(include_dirs_1 ${ZLIB_INCLUDE_DIR} ${SOURCE_DIR})

add_executable(t1 ${SOURCE_DIR}/1.c)
target_include_directories(t1 PRIVATE ${include_dirs_1})

add_executable(t2 ${SOURCE_DIR}/2.c)
target_include_directories(t2 PRIVATE ${include_dirs_1})

add_executable(t3 ${SOURCE_DIR}/3.c)
target_include_directories(t3 PRIVATE ${include_dirs_1})

add_executable(t4 ${SOURCE_DIR}/4.c)
target_include_directories(t4 PRIVATE ${include_dirs_1})

add_executable(t5 ${SOURCE_DIR}/5.c)
