cmake_minimum_required(VERSION 3.13)

project(PROJECT LANGUAGES)
enable_language(ASM_NASM)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(CMAKE_ASM_NASM_OBJECT_FORMAT win32)
add_compile_options(-DNASM=1)
include_directories(${CMAKE_CURRENT_BINARY_DIR}/include_a)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include_a)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include_b)

add_library(shared SHARED ${SOURCE_DIR}/nasm1.asm)
target_compile_options(shared PRIVATE -DF1)

add_executable(app ${SOURCE_DIR}/nasm2.asm)
target_compile_options(app PRIVATE -DF2)
target_include_directories(app PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/include_b)
