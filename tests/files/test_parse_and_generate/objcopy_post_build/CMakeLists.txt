cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/symbols.txt ${CMAKE_CURRENT_BINARY_DIR}/symbols.txt COPYONLY)

add_library(foo SHARED ${SOURCE_DIR}/foo.c)

add_custom_command(TARGET foo POST_BUILD
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_OBJCOPY} --redefine-syms=${CMAKE_CURRENT_BINARY_DIR}/symbols.txt $<TARGET_FILE:foo>
    VERBATIM
)

add_executable(main ${SOURCE_DIR}/main.c)
target_link_libraries(main PRIVATE foo)
