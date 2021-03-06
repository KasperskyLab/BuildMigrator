cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)
enable_language(ASM)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(compile_flags_1 -DCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC)
set(compile_flags_2 -DAAAAAAAAAA -DBBBBBBBBBBB)
language_compile_options(C -DXXXXXXXXXXXXXXXXX -DYYYYYYYYYYYYYYYYYY)
language_compile_options(CXX -DXXXXXXXXXXXXXXXXX -DYYYYYYYYYYYYYYYYYY)

add_executable(a1 ${SOURCE_DIR}/1.c)
target_compile_options(a1 PRIVATE ${compile_flags_1} ${compile_flags_2} -DF1)

set_source_files_properties(${SOURCE_DIR}/2.c PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
add_executable(a2
    ${SOURCE_DIR}/2.c
    ${SOURCE_DIR}/3.c
    ${SOURCE_DIR}/4.cpp
    ${SOURCE_DIR}/9.S
)
target_language_compile_options(a2 ASM PRIVATE ${compile_flags_2})
target_language_compile_options(a2 C PRIVATE ${compile_flags_2})
target_language_compile_options(a2 CXX PRIVATE -DF4)

add_executable(a3 ${SOURCE_DIR}/5.cpp)
target_compile_options(a3 PRIVATE ${compile_flags_1} ${compile_flags_2} -DF5)

add_executable(a4 ${SOURCE_DIR}/6.cpp)
target_compile_options(a4 PRIVATE ${compile_flags_2} -DF6)

add_executable(a5 ${SOURCE_DIR}/7.cpp ${SOURCE_DIR}/8.c)
target_compile_options(a5 PRIVATE -DEEEE -DGGGG)
target_language_compile_options(a5 C PRIVATE -DF8)
target_language_compile_options(a5 CXX PRIVATE ${compile_flags_2} -DF7)
