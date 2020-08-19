cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/libarchive/archive_static.dir/Release)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/libarchive/Release)

set_source_files_properties(${SOURCE_DIR}/libarchive/foo.c PROPERTIES COMPILE_OPTIONS
    "/W3;/WX-;/Ob2;/Oi;/Oy-;-DWIN32;-D_WINDOWS;-DLIBARCHIVE_STATIC;-DHAVE_CONFIG_H;-D_CRT_SECURE_NO_DEPRECATE;-DCMAKE_INTDIR=\"Release\";-D_MBCS;/MD$<$<CONFIG:Debug>:d>;/GS;/fp:precise;/Zc:wchar_t;/Zc:forScope;/Zc:inline;/Gd;/analyze-;/errorReport:queue"
)
set_source_files_properties(${SOURCE_DIR}/libarchive/foo.c PROPERTIES INCLUDE_DIRECTORIES "${SOURCE_DIR}/libarchive;${CMAKE_CURRENT_BINARY_DIR}")
set_source_files_properties(${SOURCE_DIR}/libarchive/bar.c PROPERTIES COMPILE_OPTIONS
    "/W3;/WX-;/Ob2;/Oi;/Oy-;-DWIN32;-D_WINDOWS;-DLIBARCHIVE_STATIC;-DHAVE_CONFIG_H;-D_CRT_SECURE_NO_DEPRECATE;-DCMAKE_INTDIR=\"Release\";-D_MBCS;/MD$<$<CONFIG:Debug>:d>;/GS;/fp:precise;/Zc:wchar_t;/Zc:forScope;/Zc:inline;/Gd;/analyze-;/errorReport:queue"
)
set_source_files_properties(${SOURCE_DIR}/libarchive/bar.c PROPERTIES INCLUDE_DIRECTORIES "${SOURCE_DIR}/libarchive;${CMAKE_CURRENT_BINARY_DIR}")
add_library(archive_static.static STATIC
    ${SOURCE_DIR}/libarchive/foo.c
    ${SOURCE_DIR}/libarchive/bar.c
)
set_target_properties(archive_static.static PROPERTIES OUTPUT_NAME archive_static)
set_target_output_subdir(archive_static.static ARCHIVE_OUTPUT_DIRECTORY libarchive/Release)
