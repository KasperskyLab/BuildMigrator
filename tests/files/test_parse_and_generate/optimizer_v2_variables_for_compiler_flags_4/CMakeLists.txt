cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)
enable_language(ASM)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(compile_flags_1 -DAAAAAAAAAAAAAAAAA -DBBBBBBBBBBBBBBBBB -DDDDDDDDDDDDDDDDDD)

set_source_files_properties(${SOURCE_DIR}/1.c PROPERTIES COMPILE_OPTIONS "-DDDDDDDDDDDDDDDDDD;-DF1")
set_source_files_properties(${SOURCE_DIR}/2.c PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
add_executable(a1 ${SOURCE_DIR}/1.c ${SOURCE_DIR}/2.c ${SOURCE_DIR}/8.c)
target_compile_options(a1 PRIVATE -DCCCCCCCCCCCCCCCCC)

add_executable(a2 ${SOURCE_DIR}/3.c ${SOURCE_DIR}/4.cpp ${SOURCE_DIR}/7.S)
target_language_compile_options(a2 ASM PRIVATE ${compile_flags_1} -DCCCCCCCCCCCCCCCCC)
target_language_compile_options(a2 CXX PRIVATE -DCCCCCCCCCCCCCCCCC -DDDDDDDDDDDDDDDDDD -DF4)

set_source_files_properties(${SOURCE_DIR}/5.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1};-DF7;-DCCCCCCCCCCCCCCCCC")
set_source_files_properties(${SOURCE_DIR}/6.cpp PROPERTIES COMPILE_OPTIONS -DF8)
add_executable(a3 ${SOURCE_DIR}/5.cpp ${SOURCE_DIR}/6.cpp)
target_compile_options(a3 PRIVATE -DEEEE -DGGGG)
