cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
add_compile_options(
    -D_MBCS
    /Zc:wchar_t
    /Zc:forScope
    /Zc:inline
    /Zc:threadSafeInit-
)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/Release/default)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/lib/default)

add_library(lib_default_jsonmd.static STATIC
    ${SOURCE_DIR}/_internal/Source/internalJSONNode.cpp
    ${SOURCE_DIR}/_internal/Source/JSONAllocator.cpp
)
target_compile_options(lib_default_jsonmd.static PRIVATE /MD$<$<CONFIG:Debug>:d>)
set_target_properties(lib_default_jsonmd.static PROPERTIES OUTPUT_NAME libjsonmd)
set_target_output_subdir(lib_default_jsonmd.static ARCHIVE_OUTPUT_DIRECTORY lib/default)

add_library(lib_default_jsonmt.static STATIC
    ${SOURCE_DIR}/_internal/Source/internalJSONNode.cpp
    ${SOURCE_DIR}/_internal/Source/JSONAllocator.cpp
)
target_compile_options(lib_default_jsonmt.static PRIVATE /MT$<$<CONFIG:Debug>:d>)
set_target_properties(lib_default_jsonmt.static PROPERTIES OUTPUT_NAME libjsonmt)
set_target_output_subdir(lib_default_jsonmt.static ARCHIVE_OUTPUT_DIRECTORY lib/default)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/Release/unicode)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/lib/unicode)

add_library(lib_unicode_jsonmt.static STATIC
    ${SOURCE_DIR}/_internal/Source/internalJSONNode.cpp
    ${SOURCE_DIR}/_internal/Source/JSONAllocator.cpp
)
target_compile_options(lib_unicode_jsonmt.static PRIVATE -DJSON_UNICODE /MT$<$<CONFIG:Debug>:d>)
set_target_properties(lib_unicode_jsonmt.static PROPERTIES OUTPUT_NAME libjsonmt)
set_target_output_subdir(lib_unicode_jsonmt.static ARCHIVE_OUTPUT_DIRECTORY lib/unicode)

add_library(lib_unicode_jsonmd.static STATIC
    ${SOURCE_DIR}/_internal/Source/internalJSONNode.cpp
    ${SOURCE_DIR}/_internal/Source/JSONAllocator.cpp
)
target_compile_options(lib_unicode_jsonmd.static PRIVATE -DJSON_UNICODE /MD$<$<CONFIG:Debug>:d>)
set_target_properties(lib_unicode_jsonmd.static PROPERTIES OUTPUT_NAME libjsonmd)
set_target_output_subdir(lib_unicode_jsonmd.static ARCHIVE_OUTPUT_DIRECTORY lib/unicode)
