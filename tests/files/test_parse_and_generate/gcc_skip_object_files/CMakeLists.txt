cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_executable(test
    ${SOURCE_DIR}/a.cpp
    ${SOURCE_DIR}/b.cpp
    ${SOURCE_DIR}/main.cpp
)
target_compile_options(test PRIVATE -DMSG_A=a -DMSG_B=b)
target_include_directories(test PRIVATE ${SOURCE_DIR})
