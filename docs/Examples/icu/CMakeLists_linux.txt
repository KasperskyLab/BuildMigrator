cmake_minimum_required(VERSION 3.13)

project(icu CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(ICU_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}/source" CACHE PATH "")
add_compile_options(
    -ffunction-sections
    -fdata-sections
    -D_REENTRANT
    -DU_HAVE_ELF_H=1
    -DU_ENABLE_DYLOAD=0
    -DU_HAVE_STRTOD_L=1
    -DU_HAVE_XLOCALE_H=0
    -DU_ATTRIBUTE_DEPRECATED=
    -W
    -Wall
    -pedantic
    -Wpointer-arith
    -Wwrite-strings
    -Wno-long-long
    -std=c++11
)
include_directories(${ICU_SOURCE_DIR}/common)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/data/icupkg.inc ${CMAKE_CURRENT_BINARY_DIR}/data/icupkg.inc COPYONLY)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/data/out/build/icudt67l)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/lib)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp)

find_program(ICU_ICUPKG icupkg)
if(NOT ICU_ICUPKG)
    message(FATAL_ERROR "icupkg not found")
endif()

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${ICU_ICUPKG} -d ${CMAKE_CURRENT_BINARY_DIR}/data/out/build/icudt67l --list -x * ${ICU_SOURCE_DIR}/data/in/icudt67l.dat -o ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst
    DEPENDS
        ${ICU_SOURCE_DIR}/data/in/icudt67l.dat
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
        ${ICU_PKGDATA} -O ${CMAKE_CURRENT_BINARY_DIR}/data/icupkg.inc -q -c -s ${CMAKE_CURRENT_BINARY_DIR}/data/out/build/icudt67l -d ${CMAKE_CURRENT_BINARY_DIR}/lib -e icudt67 -T ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp -p icudt67l -m static -r 67.1 -L icudata ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst
    DEPENDS
        ${CMAKE_CURRENT_BINARY_DIR}/data/icupkg.inc
        ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst
    VERBATIM
)
add_custom_target(lib_icudata.static ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/lib/libicudata.a)

include(ICUI18N_STATIC_SRC.cmake)
add_library(icui18n.static STATIC ${ICUI18N_STATIC_SRC})
target_compile_options(icui18n.static PRIVATE -DU_I18N_IMPLEMENTATION)
target_include_directories(icui18n.static PRIVATE ${ICU_SOURCE_DIR}/i18n)
set_target_properties(icui18n.static PROPERTIES OUTPUT_NAME icui18n)
set_target_output_subdir(icui18n.static ARCHIVE_OUTPUT_DIRECTORY lib)

add_library(icuio.static STATIC
    ${ICU_SOURCE_DIR}/io/locbund.cpp
    ${ICU_SOURCE_DIR}/io/ufile.cpp
    ${ICU_SOURCE_DIR}/io/ufmt_cmn.cpp
    ${ICU_SOURCE_DIR}/io/uprintf.cpp
    ${ICU_SOURCE_DIR}/io/uprntf_p.cpp
    ${ICU_SOURCE_DIR}/io/uscanf.cpp
    ${ICU_SOURCE_DIR}/io/uscanf_p.cpp
    ${ICU_SOURCE_DIR}/io/ustdio.cpp
    ${ICU_SOURCE_DIR}/io/sprintf.cpp
    ${ICU_SOURCE_DIR}/io/sscanf.cpp
    ${ICU_SOURCE_DIR}/io/ustream.cpp
    ${ICU_SOURCE_DIR}/io/ucln_io.cpp
)
target_compile_options(icuio.static PRIVATE -DU_IO_IMPLEMENTATION)
target_include_directories(icuio.static PRIVATE ${ICU_SOURCE_DIR}/io ${ICU_SOURCE_DIR}/i18n)
set_target_properties(icuio.static PROPERTIES OUTPUT_NAME icuio)
set_target_output_subdir(icuio.static ARCHIVE_OUTPUT_DIRECTORY lib)

add_library(icutu.static STATIC
    ${ICU_SOURCE_DIR}/tools/toolutil/filestrm.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/package.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/pkgitems.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/swapimpl.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/toolutil.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/unewdata.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/collationinfo.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/denseranges.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/ucm.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/ucmstate.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/uoptions.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/uparse.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/ucbuf.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/xmlparser.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/writesrc.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/pkg_icu.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/pkg_genc.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/pkg_gencmn.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/ppucd.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/flagparser.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/filetools.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/udbgutil.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/dbgutil.cpp
    ${ICU_SOURCE_DIR}/tools/toolutil/ucln_tu.cpp
)
target_compile_options(icutu.static PRIVATE
    -DUNISTR_FROM_CHAR_EXPLICIT=explicit
    -DUNISTR_FROM_STRING_EXPLICIT=explicit
    -DU_TOOLUTIL_IMPLEMENTATION
)
target_include_directories(icutu.static PRIVATE ${ICU_SOURCE_DIR}/tools/toolutil ${ICU_SOURCE_DIR}/i18n)
set_target_properties(icutu.static PROPERTIES OUTPUT_NAME icutu)
set_target_output_subdir(icutu.static ARCHIVE_OUTPUT_DIRECTORY lib)

include(ICUUC_STATIC_SRC.cmake)
add_library(icuuc.static STATIC ${ICUUC_STATIC_SRC})
target_compile_options(icuuc.static PRIVATE
    "-DDEFAULT_ICU_PLUGINS=\"/usr/local/lib/icu\" "
    -DU_COMMON_IMPLEMENTATION
)
set_target_properties(icuuc.static PROPERTIES OUTPUT_NAME icuuc)
set_target_output_subdir(icuuc.static ARCHIVE_OUTPUT_DIRECTORY lib)

add_library(stubdata_icudata.static STATIC ${ICU_SOURCE_DIR}/stubdata/stubdata.cpp)
set_target_properties(stubdata_icudata.static PROPERTIES OUTPUT_NAME icudata)
set_target_output_subdir(stubdata_icudata.static ARCHIVE_OUTPUT_DIRECTORY stubdata)
