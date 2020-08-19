cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
language_compile_options(CXX -DCXX=1)
language_include_directories(CXX ${CMAKE_CURRENT_BINARY_DIR}/include_a)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include_a)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include_b)

add_library(shared SHARED ${SOURCE_DIR}/cpp1.cpp ${SOURCE_DIR}/c1.c)
target_language_compile_options(shared CXX PRIVATE -DF1)
target_language_include_directories(shared CXX PRIVATE ${CMAKE_CURRENT_BINARY_DIR})

add_executable(app1 ${SOURCE_DIR}/cpp2.cpp)
target_compile_options(app1 PRIVATE -DF2)
target_include_directories(app1 PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/include_b)

set_source_files_properties(${SOURCE_DIR}/cpp3.cpp PROPERTIES COMPILE_OPTIONS -DF3)
set_source_files_properties(${SOURCE_DIR}/cpp4.cpp PROPERTIES COMPILE_OPTIONS -DF4)
add_executable(app2
    ${SOURCE_DIR}/c2.c
    ${SOURCE_DIR}/cpp3.cpp
    ${SOURCE_DIR}/cpp4.cpp
)
target_language_compile_options(app2 CXX PRIVATE -DCOMMON)
target_language_include_directories(app2 CXX PRIVATE ${SOURCE_DIR})
