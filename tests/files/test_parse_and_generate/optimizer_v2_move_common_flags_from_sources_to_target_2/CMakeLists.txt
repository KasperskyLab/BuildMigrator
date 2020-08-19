cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)
enable_language(ASM)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include_a)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include_b)

add_executable(app ${SOURCE_DIR}/a.cpp ${SOURCE_DIR}/a.c ${SOURCE_DIR}/a.S)
target_link_options(app PRIVATE -pie)
target_compile_options(app PRIVATE -DA=1 -Wall)
target_include_directories(app PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/include_a)
target_language_compile_options(app ASM PRIVATE -Wa,--execstack)
target_language_compile_options(app CXX PRIVATE -DB=1 -std=c++17)
target_language_include_directories(app CXX PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/include_b)

set_source_files_properties(${SOURCE_DIR}/b2.c PROPERTIES COMPILE_OPTIONS "-DA=1;-fno-stack-protector")
set_source_files_properties(${SOURCE_DIR}/b2.c PROPERTIES INCLUDE_DIRECTORIES ${CMAKE_CURRENT_BINARY_DIR}/include_a)
set_source_files_properties(${SOURCE_DIR}/b1.c PROPERTIES COMPILE_OPTIONS -std=c11)
add_library(lib SHARED ${SOURCE_DIR}/b2.c ${SOURCE_DIR}/b1.c)
target_link_options(lib PRIVATE -Wl,-z,execstack)
target_compile_options(lib PRIVATE -DB=1 -Wno-error)
target_include_directories(lib PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/include_b)
