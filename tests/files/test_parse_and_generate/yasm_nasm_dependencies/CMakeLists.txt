cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(CMAKE_ASM_YASM_OBJECT_FORMAT win32)
set(CMAKE_ASM_YASM_MACHINE x86)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/setup.asm ${CMAKE_CURRENT_BINARY_DIR}/setup.asm COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/include/functions.inc ${CMAKE_CURRENT_BINARY_DIR}/include/functions.inc COPYONLY)

set_source_files_properties(${SOURCE_DIR}/main.asm PROPERTIES COMPILE_OPTIONS
    "-pnasm;-rnasm;-DPREFIX;-DX86=1;-P${CMAKE_CURRENT_BINARY_DIR}/setup.asm"
)
set_source_files_properties(${SOURCE_DIR}/main.asm PROPERTIES INCLUDE_DIRECTORIES ${CMAKE_CURRENT_BINARY_DIR}/include)
add_executable(app ${SOURCE_DIR}/main.c)
target_yasm_sources(app PRIVATE ${SOURCE_DIR}/main.asm)
