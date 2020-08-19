cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)
enable_language(ASM)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(compile_flags_1 -DSOMEFLAG1=aaa -DSOMEFLAG2=bbb -DSOMEFLAG3=ccc)
language_compile_options(C ${compile_flags_1})
language_compile_options(CXX ${compile_flags_1} --std=c++14)

add_executable(t1 ${SOURCE_DIR}/1.c)

add_executable(t2 ${SOURCE_DIR}/3.c)

add_executable(t3 ${SOURCE_DIR}/3.c)

add_executable(t4 ${SOURCE_DIR}/4.cpp)

add_executable(t5 ${SOURCE_DIR}/5.cpp)

add_executable(t6 ${SOURCE_DIR}/6.cpp)

add_executable(t7 ${SOURCE_DIR}/7.S)
