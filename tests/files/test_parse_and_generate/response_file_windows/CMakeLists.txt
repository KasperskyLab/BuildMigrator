cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

set_source_files_properties(${SOURCE_DIR}/main.cpp PROPERTIES COMPILE_OPTIONS /EHsc)
set_source_files_properties(${SOURCE_DIR}/extra.cpp PROPERTIES COMPILE_OPTIONS /EHsc)
add_executable(main ${SOURCE_DIR}/main.cpp ${SOURCE_DIR}/extra.cpp)
target_link_options(main PRIVATE /subsystem:console)
