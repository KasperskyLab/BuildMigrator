cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/symbols_foo.txt ${CMAKE_CURRENT_BINARY_DIR}/symbols_foo.txt COPYONLY)

add_library(foo_o OBJECT ${SOURCE_DIR}/foo.c)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/foo.o
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_COMMAND} -E copy_if_different "$<TARGET_OBJECTS:foo_o>" "${CMAKE_CURRENT_BINARY_DIR}/foo.o"
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_OBJCOPY} --remove-section=.somesection.* --globalize-symbols=${CMAKE_CURRENT_BINARY_DIR}/symbols_foo.txt --redefine-sym abc=def ${CMAKE_CURRENT_BINARY_DIR}/foo.o
    DEPENDS
        foo_o
    VERBATIM
)
add_custom_target(foo_o_post_build ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/foo.o)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/symbols_bar.txt ${CMAKE_CURRENT_BINARY_DIR}/symbols_bar.txt COPYONLY)

add_library(bar_o OBJECT ${SOURCE_DIR}/bar.c)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/bar.o
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_COMMAND} -E copy_if_different "$<TARGET_OBJECTS:bar_o>" "${CMAKE_CURRENT_BINARY_DIR}/bar.o"
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_OBJCOPY} --remove-section=.somesection.* --globalize-symbols=${CMAKE_CURRENT_BINARY_DIR}/symbols_bar.txt --redefine-sym abc=def ${CMAKE_CURRENT_BINARY_DIR}/bar.o
    DEPENDS
        bar_o
    VERBATIM
)
add_custom_target(bar_o_post_build ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/bar.o)

add_executable(main
    ${SOURCE_DIR}/main.c
    ${CMAKE_CURRENT_BINARY_DIR}/foo.o
    ${CMAKE_CURRENT_BINARY_DIR}/bar.o
)
