cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(CMAKE_ASM_YASM_OBJECT_FORMAT win32)
add_compile_options(-DYASM=1)
include_directories(${CMAKE_CURRENT_BINARY_DIR}/include_a)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include_a)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include_b)

# Workaround for CMake error: 'No SOURCES given to target' / 'no source files for target'
if(NOT EXISTS ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
    file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/empty.c "")
endif()
add_library(shared SHARED ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
target_compile_options(shared PRIVATE -DF1)
target_yasm_sources(shared PRIVATE ${SOURCE_DIR}/yasm1.asm)

add_executable(app1 ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
target_compile_options(app1 PRIVATE -DF2)
target_include_directories(app1 PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/include_b)
target_yasm_sources(app1 PRIVATE ${SOURCE_DIR}/yasm2.asm)

add_executable(app2 ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
target_link_options(app2 PRIVATE c2.obj)
target_compile_options(app2 PRIVATE -DCOMMON)
target_include_directories(app2 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
target_yasm_sources(app2 PRIVATE ${SOURCE_DIR}/yasm3.asm ${SOURCE_DIR}/yasm4.asm)
