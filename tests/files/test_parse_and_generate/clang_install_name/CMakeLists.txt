cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(foo SHARED ${SOURCE_DIR}/foo.c)
target_link_options(foo PRIVATE
    -Wl,-headerpad_max_install_names
    -Wl,-search_paths_first
    -install_name
    /usr/local/lib/libfoo.dylib
)
