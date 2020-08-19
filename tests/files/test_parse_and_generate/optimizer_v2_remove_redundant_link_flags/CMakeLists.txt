cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include)

add_library(a_o OBJECT ${SOURCE_DIR}/a.cpp)
target_link_libraries(a_o PRIVATE Threads::Threads)
target_compile_options(a_o PRIVATE -DA=B -fno-rtti)
target_include_directories(a_o PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/include)
