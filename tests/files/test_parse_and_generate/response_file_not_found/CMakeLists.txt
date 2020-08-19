cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

# Workaround for CMake error: 'No SOURCES given to target' / 'no source files for target'
if(NOT EXISTS ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
    file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/empty.c "")
endif()
add_executable(response_file_not_found ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
target_link_options(response_file_not_found PRIVATE @file_not_found.rsp /subsystem:console)

set_source_files_properties(${SOURCE_DIR}/foo.c PROPERTIES COMPILE_OPTIONS /EHsc)
set_source_files_properties(${SOURCE_DIR}/main.c PROPERTIES COMPILE_OPTIONS /EHsc)
add_executable(main ${SOURCE_DIR}/foo.c ${SOURCE_DIR}/main.c)
target_link_options(main PRIVATE /subsystem:console)
