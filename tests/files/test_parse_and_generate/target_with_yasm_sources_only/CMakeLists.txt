cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(CMAKE_ASM_YASM_OBJECT_FORMAT win32)
set(CMAKE_ASM_YASM_MACHINE x86)

add_executable(main ${SOURCE_DIR}/main.c)

# Workaround for CMake error: 'No SOURCES given to target' / 'no source files for target'
if(NOT EXISTS ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
    file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/empty.c "")
endif()
add_executable(yasm1 ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
target_yasm_sources(yasm1 PRIVATE ${SOURCE_DIR}/yasm1.asm)

add_executable(yasm2 ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
target_yasm_sources(yasm2 PRIVATE ${SOURCE_DIR}/yasm2.asm)
