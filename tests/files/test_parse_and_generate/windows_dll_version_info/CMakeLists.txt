cmake_minimum_required(VERSION 3.13)

project(icu LANGUAGES CXX VERSION 60.1)
enable_language(RC)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(ICU_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
add_compile_options(
    -DHAVE_DLOPEN=0
    -DU_HAVE_ATOMIC=1
    -DU_HAVE_MMAP=0
    -DU_HAVE_DIRENT_H=0
    -DU_HAVE_POPEN=0
    -DU_HAVE_TZNAME=0
    -DU_HAVE_STRTOD_L=0
    -DU_RELEASE=1
    -D_CRT_SECURE_NO_DEPRECATE
)
include_directories(${ICU_SOURCE_DIR})
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/lib/icuuc.lib ${CMAKE_CURRENT_BINARY_DIR}/lib/icuuc.lib COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/stubdata/icudt.lib ${CMAKE_CURRENT_BINARY_DIR}/stubdata/icudt.lib COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/lib/icuin.lib ${CMAKE_CURRENT_BINARY_DIR}/lib/icuin.lib COPYONLY)

add_library(icuio58 SHARED ${ICU_SOURCE_DIR}/io.cpp ${ICU_SOURCE_DIR}/io.rc)
target_link_options(icuio58 PRIVATE -base:0x4ab00000)
target_link_libraries(icuio58 PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}/lib/icuuc
    ${CMAKE_CURRENT_BINARY_DIR}/stubdata/icudt
    ${CMAKE_CURRENT_BINARY_DIR}/lib/icuin
)
target_language_compile_options(icuio58 CXX PRIVATE
    -DU_ATTRIBUTE_DEPRECATED=
    -DWIN32
    -DCYGWINMSVC
    -DU_IO_IMPLEMENTATION
    /GL-
    /W4
    -GF
)
set_target_properties(icuio58 PROPERTIES ARCHIVE_OUTPUT_NAME icuio)
set_target_output_subdir(icuio58 RUNTIME_OUTPUT_DIRECTORY lib)
set_target_output_subdir(icuio58 ARCHIVE_OUTPUT_DIRECTORY lib)
set_target_properties(icuio58 PROPERTIES VERSION 58.2)
