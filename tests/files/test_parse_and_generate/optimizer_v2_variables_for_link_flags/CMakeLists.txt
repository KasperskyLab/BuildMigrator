cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(link_flags_1
    -Wl,-z,relro,-z,now
    -Wl,aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    -pthread
    -static-libgcc
)
set(link_flags_2 -Wl,bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb -nolibc -nostdlib)

add_executable(test1 ${SOURCE_DIR}/a.c)
target_link_options(test1 PRIVATE ${link_flags_1} -pie)

add_executable(test2 ${SOURCE_DIR}/b.c)
target_link_options(test2 PRIVATE ${link_flags_2})

add_library(test3 SHARED ${SOURCE_DIR}/c.c)
target_link_options(test3 PRIVATE ${link_flags_1})

add_library(test4 SHARED ${SOURCE_DIR}/d.c)
target_link_options(test4 PRIVATE ${link_flags_2})
