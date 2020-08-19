cmake_minimum_required(VERSION 3.13)

project(PROJECT C)
enable_language(RC)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/intermediate/libcurl)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/curl_package/lib)

set_source_files_properties(${SOURCE_DIR}/lib/libcurl.rc PROPERTIES COMPILE_OPTIONS "-D_USING_V110_SDK71_;-D_UNICODE;-DUNICODE;/l0x0409")
set_source_files_properties(${SOURCE_DIR}/lib/altsvc.c PROPERTIES COMPILE_OPTIONS
    "/W4;/WX-;/Ob1;/Oy-;-DBUILDING_LIBCURL;-DCURL_STATICLIB;-DUSE_SSLEAY;-DUSE_OPENSSL;-DUSE_IPV6;-DUSE_WINDOWS_SSPI;-DENABLE_IPV6;-DCURL_DISABLE_LDAP;-DUNICODE;-DHAVE_LIBZ;-DHAVE_ZLIB_H;-DUSE_NGHTTP2;-DNGHTTP2_STATICLIB;-D_USING_V110_SDK71_;-D_UNICODE;/GF;/EHsc;/MD$<$<CONFIG:Debug>:d>;/GS;/Gy;/fp:precise;/Zc:wchar_t;/Zc:forScope;/Zc:inline;/Gd;/analyze-;/errorReport:queue;/Gw;/guard:cf"
)
set_source_files_properties(${SOURCE_DIR}/lib/altsvc.c PROPERTIES INCLUDE_DIRECTORIES
    "${SOURCE_DIR}/include;${SOURCE_DIR}/lib;Z:/zlib_package/include;Z:/openssl_package/include;Z:/nghttp2_package/include"
)
set_source_files_properties(${SOURCE_DIR}/lib/asyn-ares.c PROPERTIES COMPILE_OPTIONS
    "/W4;/WX-;/Ob1;/Oy-;-DBUILDING_LIBCURL;-DCURL_STATICLIB;-DUSE_SSLEAY;-DUSE_OPENSSL;-DUSE_IPV6;-DUSE_WINDOWS_SSPI;-DENABLE_IPV6;-DCURL_DISABLE_LDAP;-DUNICODE;-DHAVE_LIBZ;-DHAVE_ZLIB_H;-DUSE_NGHTTP2;-DNGHTTP2_STATICLIB;-D_USING_V110_SDK71_;-D_UNICODE;/GF;/EHsc;/MD$<$<CONFIG:Debug>:d>;/GS;/Gy;/fp:precise;/Zc:wchar_t;/Zc:forScope;/Zc:inline;/Gd;/analyze-;/errorReport:queue;/Gw;/guard:cf"
)
set_source_files_properties(${SOURCE_DIR}/lib/asyn-ares.c PROPERTIES INCLUDE_DIRECTORIES
    "${SOURCE_DIR}/include;${SOURCE_DIR}/lib;Z:/zlib_package/include;Z:/openssl_package/include;Z:/nghttp2_package/include"
)
set_source_files_properties(${SOURCE_DIR}/lib/vtls/wolfssl.c PROPERTIES COMPILE_OPTIONS
    "/W4;/WX-;/Ob1;/Oy-;-DBUILDING_LIBCURL;-DCURL_STATICLIB;-DUSE_SSLEAY;-DUSE_OPENSSL;-DUSE_IPV6;-DUSE_WINDOWS_SSPI;-DENABLE_IPV6;-DCURL_DISABLE_LDAP;-DUNICODE;-DHAVE_LIBZ;-DHAVE_ZLIB_H;-DUSE_NGHTTP2;-DNGHTTP2_STATICLIB;-D_USING_V110_SDK71_;-D_UNICODE;/GF;/EHsc;/MD$<$<CONFIG:Debug>:d>;/GS;/Gy;/fp:precise;/Zc:wchar_t;/Zc:forScope;/Zc:inline;/Gd;/analyze-;/errorReport:queue;/Gw;/guard:cf"
)
set_source_files_properties(${SOURCE_DIR}/lib/vtls/wolfssl.c PROPERTIES INCLUDE_DIRECTORIES
    "${SOURCE_DIR}/include;${SOURCE_DIR}/lib;Z:/zlib_package/include;Z:/openssl_package/include;Z:/nghttp2_package/include"
)
add_library(curl.static STATIC
    ${SOURCE_DIR}/lib/libcurl.rc
    ${SOURCE_DIR}/lib/altsvc.c
    ${SOURCE_DIR}/lib/asyn-ares.c
    ${SOURCE_DIR}/lib/vtls/wolfssl.c
)
set_target_properties(curl.static PROPERTIES OUTPUT_NAME libcurl)
set_target_output_subdir(curl.static ARCHIVE_OUTPUT_DIRECTORY curl_package/lib)
