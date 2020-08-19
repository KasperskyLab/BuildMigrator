cmake_minimum_required(VERSION 3.13)

project(zlib LANGUAGES C VERSION 1.2.11)
enable_language(RC)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(ZLIB_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}/source" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include)
configure_file(${CMAKE_CURRENT_LIST_DIR}/windows/zconf.h ${CMAKE_CURRENT_BINARY_DIR}/zconf.h COPYONLY)

add_library(zlib_object_lib_1 OBJECT
    ${ZLIB_SOURCE_DIR}/adler32.c
    ${ZLIB_SOURCE_DIR}/compress.c
    ${ZLIB_SOURCE_DIR}/crc32.c
    ${ZLIB_SOURCE_DIR}/deflate.c
    ${ZLIB_SOURCE_DIR}/gzclose.c
    ${ZLIB_SOURCE_DIR}/gzlib.c
    ${ZLIB_SOURCE_DIR}/gzread.c
    ${ZLIB_SOURCE_DIR}/gzwrite.c
    ${ZLIB_SOURCE_DIR}/inflate.c
    ${ZLIB_SOURCE_DIR}/infback.c
    ${ZLIB_SOURCE_DIR}/inftrees.c
    ${ZLIB_SOURCE_DIR}/inffast.c
    ${ZLIB_SOURCE_DIR}/trees.c
    ${ZLIB_SOURCE_DIR}/uncompr.c
    ${ZLIB_SOURCE_DIR}/zutil.c
)
target_compile_options(zlib_object_lib_1 PRIVATE -DNO_FSEEKO -DZLIB_DLL)
target_include_directories(zlib_object_lib_1 PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}/include
    ${ZLIB_SOURCE_DIR}
    ${CMAKE_CURRENT_BINARY_DIR}
)

set_source_files_properties(${ZLIB_SOURCE_DIR}/win32/zlib1.rc PROPERTIES COMPILE_OPTIONS "-DNO_FSEEKO;-DZLIB_DLL")
set_source_files_properties(${ZLIB_SOURCE_DIR}/win32/zlib1.rc PROPERTIES INCLUDE_DIRECTORIES
    "${CMAKE_CURRENT_BINARY_DIR}/include;${ZLIB_SOURCE_DIR};${CMAKE_CURRENT_BINARY_DIR}"
)
add_library(zlib1 SHARED
    ${ZLIB_SOURCE_DIR}/win32/zlib1.rc
    $<TARGET_OBJECTS:zlib_object_lib_1>
)
set_target_properties(zlib1 PROPERTIES VERSION 1.2.11)

add_library(zlib_object_lib_2 OBJECT
    ${ZLIB_SOURCE_DIR}/adler32.c
    ${ZLIB_SOURCE_DIR}/compress.c
    ${ZLIB_SOURCE_DIR}/crc32.c
    ${ZLIB_SOURCE_DIR}/deflate.c
    ${ZLIB_SOURCE_DIR}/gzclose.c
    ${ZLIB_SOURCE_DIR}/gzlib.c
    ${ZLIB_SOURCE_DIR}/gzread.c
    ${ZLIB_SOURCE_DIR}/gzwrite.c
    ${ZLIB_SOURCE_DIR}/inflate.c
    ${ZLIB_SOURCE_DIR}/infback.c
    ${ZLIB_SOURCE_DIR}/inftrees.c
    ${ZLIB_SOURCE_DIR}/inffast.c
    ${ZLIB_SOURCE_DIR}/trees.c
    ${ZLIB_SOURCE_DIR}/uncompr.c
    ${ZLIB_SOURCE_DIR}/zutil.c
)
target_compile_options(zlib_object_lib_2 PRIVATE -DNO_FSEEKO)
target_include_directories(zlib_object_lib_2 PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}/include
    ${ZLIB_SOURCE_DIR}
    ${CMAKE_CURRENT_BINARY_DIR}
)

add_library(zlib.static STATIC $<TARGET_OBJECTS:zlib_object_lib_2>)
set_target_properties(zlib.static PROPERTIES LINKER_LANGUAGE C)
set_target_properties(zlib.static PROPERTIES OUTPUT_NAME zlib)
set_target_properties(zlib.static PROPERTIES VERSION 1.2.11)

add_library(zlib1mt SHARED
    ${ZLIB_SOURCE_DIR}/win32/zlib1.rc
    $<TARGET_OBJECTS:zlib_object_lib_1>
)
set_target_properties(zlib1mt PROPERTIES VERSION 1.2.11)

add_library(zlibmt.static STATIC $<TARGET_OBJECTS:zlib_object_lib_2>)
set_target_properties(zlibmt.static PROPERTIES LINKER_LANGUAGE C)
set_target_properties(zlibmt.static PROPERTIES OUTPUT_NAME zlibmt)
set_target_properties(zlibmt.static PROPERTIES VERSION 1.2.11)
