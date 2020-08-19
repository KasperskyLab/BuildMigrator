cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/shared)

set_source_files_properties(${SOURCE_DIR}/foo.c PROPERTIES COMPILE_OPTIONS /EHsc)
add_library(foo SHARED ${SOURCE_DIR}/foo.c)
set_target_properties(foo PROPERTIES OUTPUT_NAME libfoo)
set_target_output_subdir(foo RUNTIME_OUTPUT_DIRECTORY shared)
set_target_output_subdir(foo ARCHIVE_OUTPUT_DIRECTORY shared)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/static)

add_library(foo.static STATIC ${SOURCE_DIR}/foo.c)
set_target_properties(foo.static PROPERTIES OUTPUT_NAME libfoo)
set_target_output_subdir(foo.static ARCHIVE_OUTPUT_DIRECTORY static)

add_executable(main_static ${SOURCE_DIR}/foo.c)
target_link_options(main_static PRIVATE /subsystem:console)
target_link_libraries(main_static PRIVATE foo.static)
set_target_output_subdir(main_static RUNTIME_OUTPUT_DIRECTORY static)

set_source_files_properties(${SOURCE_DIR}/main.c PROPERTIES COMPILE_OPTIONS /EHsc)
add_executable(main ${SOURCE_DIR}/main.c)
target_link_options(main PRIVATE /subsystem:console)
target_link_libraries(main PRIVATE foo)
