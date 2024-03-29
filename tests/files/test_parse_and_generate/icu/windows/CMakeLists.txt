cmake_minimum_required(VERSION 3.13)

project(icu LANGUAGES C CXX VERSION 58.2)
enable_language(RC)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(ICU_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}/source" CACHE PATH "")
set(compile_flags_1
    -DUNISTR_FROM_CHAR_EXPLICIT=explicit
    -DUNISTR_FROM_STRING_EXPLICIT=explicit
    -DU_TOOLUTIL_IMPLEMENTATION
)
add_compile_options(
    -DHAVE_DLOPEN=0
    -DU_HAVE_ATOMIC=1
    -DU_HAVE_MMAP=0
    -DU_HAVE_DIRENT_H=0
    -DU_HAVE_POPEN=0
    -DU_HAVE_TZNAME=0
    -DU_HAVE_STRTOD_L=0
)
include_directories(${ICU_SOURCE_DIR}/common)
language_compile_options(C -DU_ATTRIBUTE_DEPRECATED= -DCYGWINMSVC /GL- -GF)
language_compile_options(CXX -DU_ATTRIBUTE_DEPRECATED= -DCYGWINMSVC /GL- -GF -Zc:wchar_t)
set(ICU_BUILD_OPTIONS_FILE ${CMAKE_CURRENT_BINARY_DIR}/data/icupkg.inc CACHE STRING "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/data/out/build/icudt58l)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/lib)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp)

find_program(ICU_ICUPKG icupkg)
if(NOT ICU_ICUPKG)
    message(FATAL_ERROR "icupkg not found")
endif()

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${ICU_ICUPKG} -d ${CMAKE_CURRENT_BINARY_DIR}/data/out/build/icudt58l --list -x * ${ICU_SOURCE_DIR}/data/in/icudt58l.dat -o ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst
    DEPENDS
        ${ICU_SOURCE_DIR}/data/in/icudt58l.dat
    VERBATIM
)
add_custom_target(data_out_tmp_icudata_lst ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/common)

add_library(data_out_tmp_icudata_o OBJECT ${ICU_SOURCE_DIR}/data/misc/icudata.rc)
target_include_directories(data_out_tmp_icudata_o PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/common)

find_program(ICU_PKGDATA pkgdata)
if(NOT ICU_PKGDATA)
    message(FATAL_ERROR "pkgdata not found")
endif()

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/lib/icudt58.dll
    ${CMAKE_CURRENT_BINARY_DIR}/lib/icudt.lib
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_COMMAND} -E copy_if_different "$<TARGET_OBJECTS:data_out_tmp_icudata_o>" "${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.res"
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${ICU_PKGDATA} -O ${ICU_BUILD_OPTIONS_FILE} -q -c -s ${CMAKE_CURRENT_BINARY_DIR}/data/out/build/icudt58l -d ${CMAKE_CURRENT_BINARY_DIR}/lib -e icudt58 -T ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp -p icudt58l -m dll -r 58 -L icudt ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst
    DEPENDS
        ${ICU_BUILD_OPTIONS_FILE}
        ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst
        data_out_tmp_icudata_o
    VERBATIM
)
add_custom_target(lib_icudata.58.2 ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/lib/icudt58.dll
    ${CMAKE_CURRENT_BINARY_DIR}/lib/icudt.lib)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/stubdata)

add_library(stubdata_icudata.58.2 SHARED ${ICU_SOURCE_DIR}/stubdata/stubdata.c)
target_link_options(stubdata_icudata.58.2 PRIVATE -NOENTRY)
set_target_properties(stubdata_icudata.58.2 PROPERTIES OUTPUT_NAME icudt58)
set_target_properties(stubdata_icudata.58.2 PROPERTIES ARCHIVE_OUTPUT_NAME icudt)
set_target_output_subdir(stubdata_icudata.58.2 RUNTIME_OUTPUT_DIRECTORY stubdata)
set_target_output_subdir(stubdata_icudata.58.2 ARCHIVE_OUTPUT_DIRECTORY stubdata)

add_library(icuuc.58.2 SHARED
    ${ICU_SOURCE_DIR}/common/ucnv.c
    ${ICU_SOURCE_DIR}/common/resbund.cpp
    ${ICU_SOURCE_DIR}/common/unistr_case_locale.cpp
    ${ICU_SOURCE_DIR}/common/uniset.cpp
    ${ICU_SOURCE_DIR}/common/common.rc
)
target_link_libraries(icuuc.58.2 PRIVATE stubdata_icudata.58.2)
target_language_compile_options(icuuc.58.2 C PRIVATE -DU_COMMON_IMPLEMENTATION)
target_language_compile_options(icuuc.58.2 CXX PRIVATE -DU_COMMON_IMPLEMENTATION)
set_target_properties(icuuc.58.2 PROPERTIES OUTPUT_NAME icuuc58)
set_target_properties(icuuc.58.2 PROPERTIES ARCHIVE_OUTPUT_NAME icuuc)
set_target_output_subdir(icuuc.58.2 RUNTIME_OUTPUT_DIRECTORY lib)
set_target_output_subdir(icuuc.58.2 ARCHIVE_OUTPUT_DIRECTORY lib)

add_library(icui18n.58.2 SHARED
    ${ICU_SOURCE_DIR}/i18n/ucln_in.cpp
    ${ICU_SOURCE_DIR}/i18n/decimfmt.cpp
    ${ICU_SOURCE_DIR}/i18n/decContext.c
    ${ICU_SOURCE_DIR}/i18n/i18n.rc
)
target_link_libraries(icui18n.58.2 PRIVATE icuuc.58.2 stubdata_icudata.58.2)
target_include_directories(icui18n.58.2 PRIVATE ${ICU_SOURCE_DIR}/i18n)
target_language_compile_options(icui18n.58.2 C PRIVATE -DU_I18N_IMPLEMENTATION)
target_language_compile_options(icui18n.58.2 CXX PRIVATE -DU_I18N_IMPLEMENTATION)
set_target_properties(icui18n.58.2 PROPERTIES OUTPUT_NAME icuin58)
set_target_properties(icui18n.58.2 PROPERTIES ARCHIVE_OUTPUT_NAME icuin)
set_target_output_subdir(icui18n.58.2 RUNTIME_OUTPUT_DIRECTORY lib)
set_target_output_subdir(icui18n.58.2 ARCHIVE_OUTPUT_DIRECTORY lib)

add_library(icuio.58.2 SHARED
    ${ICU_SOURCE_DIR}/io/locbund.cpp
    ${ICU_SOURCE_DIR}/io/ufile.c
    ${ICU_SOURCE_DIR}/io/ucln_io.cpp
    ${ICU_SOURCE_DIR}/io/io.rc
)
target_link_libraries(icuio.58.2 PRIVATE icuuc.58.2 stubdata_icudata.58.2 icui18n.58.2)
target_include_directories(icuio.58.2 PRIVATE ${ICU_SOURCE_DIR}/i18n)
target_language_compile_options(icuio.58.2 C PRIVATE -DU_IO_IMPLEMENTATION)
target_language_compile_options(icuio.58.2 CXX PRIVATE -DU_IO_IMPLEMENTATION)
target_language_include_directories(icuio.58.2 C PRIVATE ${ICU_SOURCE_DIR}/io)
target_language_include_directories(icuio.58.2 CXX PRIVATE ${ICU_SOURCE_DIR}/io)
set_target_properties(icuio.58.2 PROPERTIES OUTPUT_NAME icuio58)
set_target_properties(icuio.58.2 PROPERTIES ARCHIVE_OUTPUT_NAME icuio)
set_target_output_subdir(icuio.58.2 RUNTIME_OUTPUT_DIRECTORY lib)
set_target_output_subdir(icuio.58.2 ARCHIVE_OUTPUT_DIRECTORY lib)

add_library(icutu.58.2 SHARED
    ${ICU_SOURCE_DIR}/tools/toolutil/filestrm.c
    ${ICU_SOURCE_DIR}/tools/toolutil/ucm.c
    ${ICU_SOURCE_DIR}/tools/toolutil/ucln_tu.cpp
)
target_link_libraries(icutu.58.2 PRIVATE icui18n.58.2 icuuc.58.2 stubdata_icudata.58.2)
target_compile_options(icutu.58.2 PRIVATE ${compile_flags_1})
target_include_directories(icutu.58.2 PRIVATE ${ICU_SOURCE_DIR}/i18n)
target_language_include_directories(icutu.58.2 C PRIVATE ${ICU_SOURCE_DIR}/tools/toolutil)
set_target_properties(icutu.58.2 PROPERTIES OUTPUT_NAME icutu58)
set_target_properties(icutu.58.2 PROPERTIES ARCHIVE_OUTPUT_NAME icutu)
set_target_output_subdir(icutu.58.2 RUNTIME_OUTPUT_DIRECTORY lib)
set_target_output_subdir(icutu.58.2 ARCHIVE_OUTPUT_DIRECTORY lib)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/lib/sicudt.lib
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${ICU_PKGDATA} -O ${ICU_BUILD_OPTIONS_FILE} -q -c -s ${CMAKE_CURRENT_BINARY_DIR}/data/out/build/icudt58l -d ${CMAKE_CURRENT_BINARY_DIR}/lib -e icudt58 -T ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp -p icudt58l -L sicudt -m static -r 58 ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst
    DEPENDS
        ${ICU_BUILD_OPTIONS_FILE}
        ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst
    VERBATIM
)
add_custom_target(icudata.static ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/lib/sicudt.lib)

add_library(icui18n.static STATIC
    ${ICU_SOURCE_DIR}/i18n/ucln_in.cpp
    ${ICU_SOURCE_DIR}/i18n/decimfmt.cpp
    ${ICU_SOURCE_DIR}/i18n/decContext.c
)
target_compile_options(icui18n.static PRIVATE -DU_I18N_IMPLEMENTATION -DU_STATIC_IMPLEMENTATION)
target_include_directories(icui18n.static PRIVATE ${ICU_SOURCE_DIR}/i18n)
set_target_properties(icui18n.static PROPERTIES OUTPUT_NAME sicuin)
set_target_output_subdir(icui18n.static ARCHIVE_OUTPUT_DIRECTORY lib)

add_library(icuio.static STATIC
    ${ICU_SOURCE_DIR}/io/locbund.cpp
    ${ICU_SOURCE_DIR}/io/ufile.c
    ${ICU_SOURCE_DIR}/io/ucln_io.cpp
)
target_compile_options(icuio.static PRIVATE -DU_IO_IMPLEMENTATION -DU_STATIC_IMPLEMENTATION)
target_include_directories(icuio.static PRIVATE ${ICU_SOURCE_DIR}/i18n ${ICU_SOURCE_DIR}/io)
set_target_properties(icuio.static PROPERTIES OUTPUT_NAME sicuio)
set_target_output_subdir(icuio.static ARCHIVE_OUTPUT_DIRECTORY lib)

add_library(icutu.static STATIC
    ${ICU_SOURCE_DIR}/tools/toolutil/filestrm.c
    ${ICU_SOURCE_DIR}/tools/toolutil/ucm.c
    ${ICU_SOURCE_DIR}/tools/toolutil/ucln_tu.cpp
)
target_compile_options(icutu.static PRIVATE ${compile_flags_1} -DU_STATIC_IMPLEMENTATION)
target_include_directories(icutu.static PRIVATE ${ICU_SOURCE_DIR}/i18n)
target_language_include_directories(icutu.static C PRIVATE ${ICU_SOURCE_DIR}/tools/toolutil)
set_target_properties(icutu.static PROPERTIES OUTPUT_NAME sicutu)
set_target_output_subdir(icutu.static ARCHIVE_OUTPUT_DIRECTORY lib)

add_library(icuuc.static STATIC
    ${ICU_SOURCE_DIR}/common/ucnv.c
    ${ICU_SOURCE_DIR}/common/resbund.cpp
    ${ICU_SOURCE_DIR}/common/unistr_case_locale.cpp
    ${ICU_SOURCE_DIR}/common/uniset.cpp
)
target_compile_options(icuuc.static PRIVATE -DU_COMMON_IMPLEMENTATION -DU_STATIC_IMPLEMENTATION)
set_target_properties(icuuc.static PROPERTIES OUTPUT_NAME sicuuc)
set_target_output_subdir(icuuc.static ARCHIVE_OUTPUT_DIRECTORY lib)
