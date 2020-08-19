cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)
enable_language(ASM)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(compile_flags_1
    -DAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    -DBBBBBBBBBBBBBBBBB
    -DCCCCCCCCCCCCCCCCC
)
set(compile_flags_2 -DXXXXXXXXXXXXXXXXXXXXXXXXXXXX -DYYYYYYYYYYYYYYYYYYYYYYYYYY)
language_compile_options(C ${compile_flags_2})
language_compile_options(CXX ${compile_flags_2})

set_source_files_properties(${SOURCE_DIR}/1.c PROPERTIES COMPILE_OPTIONS -DF1)
add_executable(a1 ${SOURCE_DIR}/1.c ${SOURCE_DIR}/2.c)
target_compile_options(a1 PRIVATE ${compile_flags_1})

add_executable(a2 ${SOURCE_DIR}/3.c ${SOURCE_DIR}/4.cpp ${SOURCE_DIR}/7.S)
target_language_compile_options(a2 ASM PRIVATE -DAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA)
target_language_compile_options(a2 CXX PRIVATE -DF4)

add_executable(a3 ${SOURCE_DIR}/5.cpp ${SOURCE_DIR}/6.c)
target_compile_options(a3 PRIVATE ${compile_flags_1} -DEEEE -DGGGG)
target_language_compile_options(a3 C PRIVATE -DF8)
target_language_compile_options(a3 CXX PRIVATE -DF7)
