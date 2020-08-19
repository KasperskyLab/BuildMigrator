cmake_minimum_required(VERSION 3.13)

project(PROJECT LANGUAGES)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

find_program(COPY_SOURCE copy_source)
if(NOT COPY_SOURCE)
    message(FATAL_ERROR "copy_source not found")
endif()

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/b.c
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${COPY_SOURCE} ${SOURCE_DIR}/a.c ${CMAKE_CURRENT_BINARY_DIR}/b.c
    DEPENDS
        ${SOURCE_DIR}/a.c
    VERBATIM
)
add_custom_target(b.c ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/b.c)
