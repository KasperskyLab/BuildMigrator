cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(foo SHARED ${SOURCE_DIR}/foo.c)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/symbols.txt ${CMAKE_CURRENT_BINARY_DIR}/symbols.txt COPYONLY)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/libfoo_modified.so
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_OBJCOPY} --redefine-syms=${CMAKE_CURRENT_BINARY_DIR}/symbols.txt $<TARGET_FILE:foo> ${CMAKE_CURRENT_BINARY_DIR}/libfoo_modified.so
    DEPENDS
        ${CMAKE_CURRENT_BINARY_DIR}/symbols.txt
        foo
    VERBATIM
)
add_custom_target(libfoo_modified_so ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/libfoo_modified.so)

add_executable(main ${SOURCE_DIR}/main.c)
target_link_libraries(main PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/libfoo_modified.so)
add_dependencies(main libfoo_modified_so)
