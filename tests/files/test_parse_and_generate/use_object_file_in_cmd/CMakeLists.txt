cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(a_o OBJECT ${SOURCE_DIR}/a.c)

find_program(COPY_A_O copy_a_o)
if(NOT COPY_A_O)
    message(FATAL_ERROR "copy_a_o not found")
endif()

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/a1.o
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_COMMAND} -E copy_if_different "$<TARGET_OBJECTS:a_o>" "${CMAKE_CURRENT_BINARY_DIR}/a.o"
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${COPY_A_O} ${CMAKE_CURRENT_BINARY_DIR}/a.o ${CMAKE_CURRENT_BINARY_DIR}/a1.o
    DEPENDS
        a_o
    VERBATIM
)
add_custom_target(a1_o ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/a1.o)

add_library(b_o OBJECT ${SOURCE_DIR}/b.c)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/b1.o
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_COMMAND} -E copy_if_different "$<TARGET_OBJECTS:b_o>" "${CMAKE_CURRENT_BINARY_DIR}/b.o"
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${COPY_A_O} ${CMAKE_CURRENT_BINARY_DIR}/b.o ${CMAKE_CURRENT_BINARY_DIR}/b1.o
    DEPENDS
        b_o
    VERBATIM
)
add_custom_target(b1_o ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/b1.o)
