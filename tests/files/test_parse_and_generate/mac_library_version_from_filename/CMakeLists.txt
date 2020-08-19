cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(foo.1.2.3 SHARED ${SOURCE_DIR}/foo.c)
target_compile_options(foo.1.2.3 PRIVATE -fPIC)
set_target_properties(foo.1.2.3 PROPERTIES OUTPUT_NAME foo)
set_target_properties(foo.1.2.3 PROPERTIES VERSION 1.2.3)

add_executable(main ${SOURCE_DIR}/main.c)
target_link_libraries(main PRIVATE foo.1.2.3)
