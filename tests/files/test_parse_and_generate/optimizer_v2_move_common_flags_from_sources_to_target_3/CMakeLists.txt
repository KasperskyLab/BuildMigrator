cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(compile_flags_1 -DF1 -DF2 -DF3 -DF4 /MT$<$<CONFIG:Debug>:d> /Zc:wchar_t-)
language_compile_options(C ${compile_flags_1})
language_include_directories(C
    ${CMAKE_CURRENT_BINARY_DIR}/i1
    ${CMAKE_CURRENT_BINARY_DIR}/i2
)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/i1)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/i2)

add_library(sh1 SHARED
    ${SOURCE_DIR}/1.c
    ${SOURCE_DIR}/2.cpp
    ${SOURCE_DIR}/3.cpp
    ${SOURCE_DIR}/4.cpp
)
target_language_compile_options(sh1 CXX PRIVATE ${compile_flags_1})
target_language_include_directories(sh1 CXX PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}/i1
    ${CMAKE_CURRENT_BINARY_DIR}/i2
)

add_library(sh2 SHARED ${SOURCE_DIR}/5.cpp)

add_library(st.static STATIC ${SOURCE_DIR}/1.c ${SOURCE_DIR}/2.cpp)
target_compile_options(st.static PRIVATE -DSTATIC_IMPL)
target_language_compile_options(st.static CXX PRIVATE ${compile_flags_1})
target_language_include_directories(st.static CXX PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}/i1
    ${CMAKE_CURRENT_BINARY_DIR}/i2
)
set_target_properties(st.static PROPERTIES OUTPUT_NAME st)
