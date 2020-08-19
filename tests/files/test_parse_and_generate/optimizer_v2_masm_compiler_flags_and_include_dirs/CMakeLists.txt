cmake_minimum_required(VERSION 3.13)

project(PROJECT C)
enable_language(ASM_MASM)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
language_compile_options(ASM_MASM -DMASM=1)
language_include_directories(ASM_MASM ${CMAKE_CURRENT_BINARY_DIR}/include_a)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include_a)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include_b)

add_library(shared SHARED ${SOURCE_DIR}/masm1.asm ${SOURCE_DIR}/c1.c)
target_language_compile_options(shared ASM_MASM PRIVATE -DF1)
target_language_include_directories(shared ASM_MASM PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/include_b)

add_executable(app ${SOURCE_DIR}/masm2.asm)
target_compile_options(app PRIVATE -DF2)
target_include_directories(app PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
