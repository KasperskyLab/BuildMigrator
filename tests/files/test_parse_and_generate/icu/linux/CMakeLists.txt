cmake_minimum_required(VERSION 3.13)

project(icu LANGUAGES C CXX VERSION 58.2)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(ICU_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}/source" CACHE PATH "")
add_compile_options(
    -ffunction-sections
    -fdata-sections
    -DU_HAVE_ELF_H=1
    -DU_HAVE_ATOMIC=1
    -DU_HAVE_STRTOD_L=1
    -DU_ATTRIBUTE_DEPRECATED=
)
include_directories(${ICU_SOURCE_DIR}/common)
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

find_program(ICU_PKGDATA pkgdata)
if(NOT ICU_PKGDATA)
    message(FATAL_ERROR "pkgdata not found")
endif()

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/lib/libicudata.a
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${ICU_PKGDATA} -O ${ICU_BUILD_OPTIONS_FILE} -q -c -s ${CMAKE_CURRENT_BINARY_DIR}/data/out/build/icudt58l -d ${CMAKE_CURRENT_BINARY_DIR}/lib -e icudt58 -T ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp -p icudt58l -m static -r 58.2 -L icudata ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst
    DEPENDS
        ${ICU_BUILD_OPTIONS_FILE}
        ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst
    VERBATIM
)
add_custom_target(icudata.static ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/lib/libicudata.a)

add_library(icui18n.static STATIC
    ${ICU_SOURCE_DIR}/i18n/ucln_in.cpp
    ${ICU_SOURCE_DIR}/i18n/decimfmt.cpp
    ${ICU_SOURCE_DIR}/i18n/decContext.c
    ${ICU_SOURCE_DIR}/i18n/decimfmtimpl.cpp
)
target_compile_options(icui18n.static PRIVATE -DU_I18N_IMPLEMENTATION)
target_include_directories(icui18n.static PRIVATE ${ICU_SOURCE_DIR}/i18n)
set_target_properties(icui18n.static PROPERTIES OUTPUT_NAME icui18n)
set_target_output_subdir(icui18n.static ARCHIVE_OUTPUT_DIRECTORY lib)

add_library(icuio.static STATIC
    ${ICU_SOURCE_DIR}/io/locbund.cpp
    ${ICU_SOURCE_DIR}/io/ufile.c
    ${ICU_SOURCE_DIR}/io/ucln_io.cpp
)
target_compile_options(icuio.static PRIVATE -DU_IO_IMPLEMENTATION)
target_include_directories(icuio.static PRIVATE ${ICU_SOURCE_DIR}/i18n)
set_target_properties(icuio.static PROPERTIES OUTPUT_NAME icuio)
set_target_output_subdir(icuio.static ARCHIVE_OUTPUT_DIRECTORY lib)

add_library(icutu.static STATIC
    ${ICU_SOURCE_DIR}/tools/toolutil/filestrm.c
    ${ICU_SOURCE_DIR}/tools/toolutil/ucm.c
    ${ICU_SOURCE_DIR}/tools/toolutil/ucln_tu.cpp
)
target_compile_options(icutu.static PRIVATE
    -DUNISTR_FROM_CHAR_EXPLICIT=explicit
    -DUNISTR_FROM_STRING_EXPLICIT=explicit
    -DU_TOOLUTIL_IMPLEMENTATION
)
target_include_directories(icutu.static PRIVATE ${ICU_SOURCE_DIR}/i18n)
set_target_properties(icutu.static PROPERTIES OUTPUT_NAME icutu)
set_target_output_subdir(icutu.static ARCHIVE_OUTPUT_DIRECTORY lib)

add_library(icuuc.static STATIC
    ${ICU_SOURCE_DIR}/common/ucnv.c
    ${ICU_SOURCE_DIR}/common/resbund.cpp
    ${ICU_SOURCE_DIR}/common/unistr_case_locale.cpp
    ${ICU_SOURCE_DIR}/common/uniset.cpp
)
target_compile_options(icuuc.static PRIVATE -DU_COMMON_IMPLEMENTATION)
set_target_properties(icuuc.static PROPERTIES OUTPUT_NAME icuuc)
set_target_output_subdir(icuuc.static ARCHIVE_OUTPUT_DIRECTORY lib)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/data/out)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/data/out/icudt58l.dat
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${ICU_PKGDATA} -O ${ICU_BUILD_OPTIONS_FILE} -q -c -s ${CMAKE_CURRENT_BINARY_DIR}/data/out/build/icudt58l -d ${CMAKE_CURRENT_BINARY_DIR}/data/out -e icudt58 -T ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp -p icudt58l -m common -r 58.2 ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst
    DEPENDS
        ${ICU_BUILD_OPTIONS_FILE}
        ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst
    VERBATIM
)
add_custom_target(data_out_icudata58l_dat ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/data/out/icudt58l.dat)
