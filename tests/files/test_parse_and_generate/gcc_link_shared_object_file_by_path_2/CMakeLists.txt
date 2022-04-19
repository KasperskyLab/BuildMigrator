cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/c)

add_library(foo SHARED ${SOURCE_DIR}/foo.c)
target_compile_options(foo PRIVATE -fPIC)
set_target_output_subdir(foo LIBRARY_OUTPUT_DIRECTORY c)
set_target_output_subdir(foo RUNTIME_OUTPUT_DIRECTORY c)
set_target_properties(foo PROPERTIES VERSION 1.2.3)

add_executable(main ${SOURCE_DIR}/main.c)
target_link_libraries(main PRIVATE foo)
set_target_output_subdir(main RUNTIME_OUTPUT_DIRECTORY c)
