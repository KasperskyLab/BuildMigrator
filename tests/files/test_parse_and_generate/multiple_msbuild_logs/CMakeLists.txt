cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
add_compile_options(
    /W4
    /WX-
    /Ob1
    /Oy-
    -DBUILDING_LIBCURL
    -DCURL_STATICLIB
    -DUSE_SSLEAY
    -DUSE_OPENSSL
    -DUSE_IPV6
    -DUSE_WINDOWS_SSPI
    -DENABLE_IPV6
    -DCURL_DISABLE_LDAP
    -DUNICODE
    -DHAVE_LIBZ
    -DHAVE_ZLIB_H
    -DUSE_NGHTTP2
    -DNGHTTP2_STATICLIB
    -D_USING_V110_SDK71_
    -D_UNICODE
    /GF
    /EHsc
    /GS
    /Gy
    /fp:precise
    /Zc:wchar_t
    /Zc:forScope
    /Zc:inline
    /Gd
    /analyze-
    /errorReport:queue
    /Gw
    /guard:cf
)
include_directories(
    ${SOURCE_DIR}/include
    ${SOURCE_DIR}/lib
    Z:/zlib_package/include
    Z:/openssl_package/include
    Z:/nghttp2_package/include
)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/intermediate/libcurl)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/curl_package/lib)

add_library(curl.static STATIC ${SOURCE_DIR}/lib/a.c)
target_compile_options(curl.static PRIVATE /MD$<$<CONFIG:Debug>:d>)
set_target_properties(curl.static PROPERTIES OUTPUT_NAME libcurl)
set_target_output_subdir(curl.static ARCHIVE_OUTPUT_DIRECTORY curl_package/lib)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/intermediate/libcurlmt)

add_library(curlmt.static STATIC ${SOURCE_DIR}/lib/b.c)
target_compile_options(curlmt.static PRIVATE /MT$<$<CONFIG:Debug>:d>)
set_target_properties(curlmt.static PROPERTIES OUTPUT_NAME libcurlmt)
set_target_output_subdir(curlmt.static ARCHIVE_OUTPUT_DIRECTORY curl_package/lib)
