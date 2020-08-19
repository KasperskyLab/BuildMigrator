cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include)

set_source_files_properties(${SOURCE_DIR}/main.c PROPERTIES COMPILE_OPTIONS "-Wa,--noexecstack;-DA=1;-DB=2;-fPIC;-g")
set_source_files_properties(${SOURCE_DIR}/main.c PROPERTIES INCLUDE_DIRECTORIES "${CMAKE_CURRENT_BINARY_DIR}/include;${SOURCE_DIR}/include")
set_source_files_properties(${SOURCE_DIR}/util.c PROPERTIES COMPILE_OPTIONS "-DA=1;-fPIC;-g;-DB=2;-Wa,--noexecstack")
set_source_files_properties(${SOURCE_DIR}/util.c PROPERTIES INCLUDE_DIRECTORIES "${CMAKE_CURRENT_BINARY_DIR}/include;${SOURCE_DIR}/include")
add_executable(test ${SOURCE_DIR}/main.c ${SOURCE_DIR}/util.c)
target_link_options(test PRIVATE -g -Wl,-search_paths_first)
