cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(foo_o OBJECT ${SOURCE_DIR}/foo.c)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/symbols_foo.txt ${CMAKE_CURRENT_BINARY_DIR}/symbols_foo.txt COPYONLY)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/foo_modified.o
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_COMMAND} -E copy_if_different "$<TARGET_OBJECTS:foo_o>" "${CMAKE_CURRENT_BINARY_DIR}/foo.o"
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_OBJCOPY} --remove-section=.somesection.* --globalize-symbols=${CMAKE_CURRENT_BINARY_DIR}/symbols_foo.txt --redefine-sym abc=def ${CMAKE_CURRENT_BINARY_DIR}/foo.o ${CMAKE_CURRENT_BINARY_DIR}/foo_modified.o
    DEPENDS
        ${CMAKE_CURRENT_BINARY_DIR}/symbols_foo.txt
        foo_o
    VERBATIM
)
add_custom_target(foo_modified_o ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/foo_modified.o)

add_library(bar_o OBJECT ${SOURCE_DIR}/bar.c)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/symbols_bar.txt ${CMAKE_CURRENT_BINARY_DIR}/symbols_bar.txt COPYONLY)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/bar_modified.o
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_COMMAND} -E copy_if_different "$<TARGET_OBJECTS:bar_o>" "${CMAKE_CURRENT_BINARY_DIR}/bar.o"
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_OBJCOPY} --remove-section=.somesection.* --globalize-symbols=${CMAKE_CURRENT_BINARY_DIR}/symbols_bar.txt --redefine-sym abc=def ${CMAKE_CURRENT_BINARY_DIR}/bar.o ${CMAKE_CURRENT_BINARY_DIR}/bar_modified.o
    DEPENDS
        ${CMAKE_CURRENT_BINARY_DIR}/symbols_bar.txt
        bar_o
    VERBATIM
)
add_custom_target(bar_modified_o ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/bar_modified.o)

set_source_files_properties(
    ${CMAKE_CURRENT_BINARY_DIR}/foo_modified.o
    ${CMAKE_CURRENT_BINARY_DIR}/bar_modified.o
    PROPERTIES EXTERNAL_OBJECT ON
)
add_executable(main
    ${SOURCE_DIR}/main.c
    ${CMAKE_CURRENT_BINARY_DIR}/foo_modified.o
    ${CMAKE_CURRENT_BINARY_DIR}/bar_modified.o
)
add_dependencies(main bar_modified_o foo_modified_o)
