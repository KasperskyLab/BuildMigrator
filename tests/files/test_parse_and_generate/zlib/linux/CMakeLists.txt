cmake_minimum_required(VERSION 3.13)

project(zlib LANGUAGES C VERSION 1.2.11)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(ZLIB_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}/source" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include)
configure_file(${CMAKE_CURRENT_LIST_DIR}/linux/zconf.h ${CMAKE_CURRENT_BINARY_DIR}/zconf.h COPYONLY)

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
target_compile_options(zlib_object_lib_2 PRIVATE -D_LARGEFILE64_SOURCE=1)
target_include_directories(zlib_object_lib_2 PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}/include
    ${CMAKE_CURRENT_BINARY_DIR}
    ${ZLIB_SOURCE_DIR}
)

add_library(z.static STATIC $<TARGET_OBJECTS:zlib_object_lib_2>)
set_target_properties(z.static PROPERTIES LINKER_LANGUAGE C)
set_target_properties(z.static PROPERTIES OUTPUT_NAME z)

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
target_compile_options(zlib_object_lib_1 PRIVATE -DZLIB_DLL -D_LARGEFILE64_SOURCE=1)
target_include_directories(zlib_object_lib_1 PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}/include
    ${CMAKE_CURRENT_BINARY_DIR}
    ${ZLIB_SOURCE_DIR}
)

add_library(z SHARED $<TARGET_OBJECTS:zlib_object_lib_1>)
set_target_properties(z PROPERTIES LINKER_LANGUAGE C)
target_link_options(z PRIVATE -Wl,--version-script,${ZLIB_SOURCE_DIR}/zlib.map)
set_target_properties(z PROPERTIES VERSION 1.2.11)
set_target_properties(z PROPERTIES SOVERSION 1)
