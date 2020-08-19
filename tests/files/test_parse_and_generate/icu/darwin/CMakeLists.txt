cmake_minimum_required(VERSION 3.13)

project(icu LANGUAGES C CXX VERSION 58.2)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(ICU_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}/source" CACHE PATH "")
add_compile_options(
    -DU_ATTRIBUTE_DEPRECATED=
    -DU_HAVE_ATOMIC=1
    -DU_HAVE_STRTOD_L=1
    -fno-common
)
include_directories(${ICU_SOURCE_DIR}/common)
language_compile_options(CXX -fvisibility=hidden)
add_link_options(-Wl,-headerpad_max_install_names)
link_libraries(Threads::Threads m)
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

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/lib/libicudata.58.2.dylib
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${ICU_PKGDATA} -O ${ICU_BUILD_OPTIONS_FILE} -q -c -s ${CMAKE_CURRENT_BINARY_DIR}/data/out/build/icudt58l -d ${CMAKE_CURRENT_BINARY_DIR}/lib -e icudt58 -T ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp -p icudt58l -m dll -r 58.2 -L icudata ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst
    DEPENDS
        ${ICU_BUILD_OPTIONS_FILE}
        ${CMAKE_CURRENT_BINARY_DIR}/data/out/tmp/icudata.lst
    VERBATIM
)
add_custom_target(lib_icudata.58.2 ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/lib/libicudata.58.2.dylib)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/lib/libicudata.58.dylib
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_COMMAND} -E create_symlink libicudata.58.2.dylib ${CMAKE_CURRENT_BINARY_DIR}/lib/libicudata.58.dylib
    DEPENDS
        ${CMAKE_CURRENT_BINARY_DIR}/lib/libicudata.58.2.dylib
    VERBATIM
)
add_custom_target(lib_icudata.58 ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/lib/libicudata.58.dylib)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/lib/libicudata.dylib
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_COMMAND} -E create_symlink libicudata.58.2.dylib ${CMAKE_CURRENT_BINARY_DIR}/lib/libicudata.dylib
    DEPENDS
        ${CMAKE_CURRENT_BINARY_DIR}/lib/libicudata.58.2.dylib
    VERBATIM
)
add_custom_target(lib_icudata ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/lib/libicudata.dylib)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/stubdata)

add_library(stubdata_icudata.58.2 SHARED ${ICU_SOURCE_DIR}/stubdata/stubdata.c)
target_link_options(stubdata_icudata.58.2 PRIVATE "-install_name @loader_path/libicudata.58.dylib")
set_target_properties(stubdata_icudata.58.2 PROPERTIES OUTPUT_NAME icudata)
set_target_output_subdir(stubdata_icudata.58.2 LIBRARY_OUTPUT_DIRECTORY stubdata)
set_target_output_subdir(stubdata_icudata.58.2 RUNTIME_OUTPUT_DIRECTORY stubdata)
set_target_properties(stubdata_icudata.58.2 PROPERTIES VERSION 58.2)
set_target_properties(stubdata_icudata.58.2 PROPERTIES SOVERSION 58)

add_library(stubdata_icudata ALIAS stubdata_icudata.58.2)

add_library(icuuc.58.2 SHARED
    ${ICU_SOURCE_DIR}/common/ucnv.c
    ${ICU_SOURCE_DIR}/common/resbund.cpp
    ${ICU_SOURCE_DIR}/common/unistr_case_locale.cpp
    ${ICU_SOURCE_DIR}/common/uniset.cpp
)
target_link_options(icuuc.58.2 PRIVATE "-install_name @loader_path/libicuuc.58.dylib")
target_link_libraries(icuuc.58.2 PRIVATE stubdata_icudata.58.2)
target_compile_options(icuuc.58.2 PRIVATE -DU_COMMON_IMPLEMENTATION)
target_language_compile_options(icuuc.58.2 C PRIVATE -fvisibility=hidden)
set_target_properties(icuuc.58.2 PROPERTIES OUTPUT_NAME icuuc)
set_target_output_subdir(icuuc.58.2 LIBRARY_OUTPUT_DIRECTORY lib)
set_target_output_subdir(icuuc.58.2 RUNTIME_OUTPUT_DIRECTORY lib)
set_target_properties(icuuc.58.2 PROPERTIES VERSION 58.2)
set_target_properties(icuuc.58.2 PROPERTIES SOVERSION 58)

add_library(icuuc ALIAS icuuc.58.2)

add_library(icui18n.58.2 SHARED
    ${ICU_SOURCE_DIR}/i18n/ucln_in.cpp
    ${ICU_SOURCE_DIR}/i18n/decimfmt.cpp
    ${ICU_SOURCE_DIR}/i18n/decContext.c
    ${ICU_SOURCE_DIR}/i18n/decimfmtimpl.cpp
)
target_link_options(icui18n.58.2 PRIVATE "-install_name @loader_path/libicui18n.58.dylib")
target_link_libraries(icui18n.58.2 PRIVATE icuuc.58.2 stubdata_icudata.58.2)
target_compile_options(icui18n.58.2 PRIVATE -DU_I18N_IMPLEMENTATION)
target_include_directories(icui18n.58.2 PRIVATE ${ICU_SOURCE_DIR}/i18n)
target_language_compile_options(icui18n.58.2 C PRIVATE -fvisibility=hidden)
set_target_properties(icui18n.58.2 PROPERTIES OUTPUT_NAME icui18n)
set_target_output_subdir(icui18n.58.2 LIBRARY_OUTPUT_DIRECTORY lib)
set_target_output_subdir(icui18n.58.2 RUNTIME_OUTPUT_DIRECTORY lib)
set_target_properties(icui18n.58.2 PROPERTIES VERSION 58.2)
set_target_properties(icui18n.58.2 PROPERTIES SOVERSION 58)

add_library(icui18n.58 ALIAS icui18n.58.2)

add_library(icui18n ALIAS icui18n.58.2)

add_library(icuio.58.2 SHARED
    ${ICU_SOURCE_DIR}/io/locbund.cpp
    ${ICU_SOURCE_DIR}/io/ufile.c
    ${ICU_SOURCE_DIR}/io/ucln_io.cpp
)
target_link_options(icuio.58.2 PRIVATE "-install_name @loader_path/libicuio.58.dylib")
target_link_libraries(icuio.58.2 PRIVATE icuuc.58.2 stubdata_icudata.58.2 icui18n.58.2)
target_compile_options(icuio.58.2 PRIVATE -DU_IO_IMPLEMENTATION)
target_include_directories(icuio.58.2 PRIVATE ${ICU_SOURCE_DIR}/i18n)
target_language_compile_options(icuio.58.2 C PRIVATE -fvisibility=hidden)
set_target_properties(icuio.58.2 PROPERTIES OUTPUT_NAME icuio)
set_target_output_subdir(icuio.58.2 LIBRARY_OUTPUT_DIRECTORY lib)
set_target_output_subdir(icuio.58.2 RUNTIME_OUTPUT_DIRECTORY lib)
set_target_properties(icuio.58.2 PROPERTIES VERSION 58.2)
set_target_properties(icuio.58.2 PROPERTIES SOVERSION 58)

add_library(icuio.58 ALIAS icuio.58.2)

add_library(icuio ALIAS icuio.58.2)

add_library(icutu.58.2 SHARED
    ${ICU_SOURCE_DIR}/tools/toolutil/filestrm.c
    ${ICU_SOURCE_DIR}/tools/toolutil/ucm.c
    ${ICU_SOURCE_DIR}/tools/toolutil/ucln_tu.cpp
)
target_link_options(icutu.58.2 PRIVATE "-install_name @loader_path/libicutu.58.dylib")
target_link_libraries(icutu.58.2 PRIVATE icui18n.58.2 icuuc.58.2 stubdata_icudata.58.2)
target_compile_options(icutu.58.2 PRIVATE
    -DU_TOOLUTIL_IMPLEMENTATION
    -DUNISTR_FROM_CHAR_EXPLICIT=explicit
    -DUNISTR_FROM_STRING_EXPLICIT=explicit
)
target_include_directories(icutu.58.2 PRIVATE ${ICU_SOURCE_DIR}/i18n)
target_language_compile_options(icutu.58.2 C PRIVATE -fvisibility=hidden)
set_target_properties(icutu.58.2 PROPERTIES OUTPUT_NAME icutu)
set_target_output_subdir(icutu.58.2 LIBRARY_OUTPUT_DIRECTORY lib)
set_target_output_subdir(icutu.58.2 RUNTIME_OUTPUT_DIRECTORY lib)
set_target_properties(icutu.58.2 PROPERTIES VERSION 58.2)
set_target_properties(icutu.58.2 PROPERTIES SOVERSION 58)

add_library(icutu.58 ALIAS icutu.58.2)

add_library(icutu ALIAS icutu.58.2)

add_library(icuuc.58 ALIAS icuuc.58.2)

add_library(stubdata_icudata.58 ALIAS stubdata_icudata.58.2)
