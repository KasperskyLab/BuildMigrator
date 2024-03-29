cmake_minimum_required(VERSION 3.13)

project(openssl LANGUAGES C CXX VERSION 1.1.1)
enable_language(ASM)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(OPENSSL_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}/source" CACHE PATH "")
configure_file(${CMAKE_CURRENT_LIST_DIR}/darwin/include/openssl/opensslconf.h ${CMAKE_CURRENT_BINARY_DIR}/include/openssl/opensslconf.h COPYONLY)

set_source_files_properties(${OPENSSL_SOURCE_DIR}/apps/app_rand.c PROPERTIES COMPILE_OPTIONS
    "-fPIC;-DL_ENDIAN;-DOPENSSL_PIC;-DOPENSSL_CPUID_OBJ;-DOPENSSL_IA32_SSE2;-DOPENSSL_BN_ASM_MONT;-DOPENSSL_BN_ASM_MONT5;-DOPENSSL_BN_ASM_GF2m;-DSHA1_ASM;-DSHA256_ASM;-DSHA512_ASM;-DKECCAK1600_ASM;-DRC4_ASM;-DMD5_ASM;-DAES_ASM;-DVPAES_ASM;-DBSAES_ASM;-DGHASH_ASM;-DECP_NISTZ256_ASM;-DX25519_ASM;-DPADLOCK_ASM;-DPOLY1305_ASM;-DOPENSSLDIR=\"/usr/local/ssl\";-DENGINESDIR=\".\""
)
set_source_files_properties(${OPENSSL_SOURCE_DIR}/apps/app_rand.c PROPERTIES INCLUDE_DIRECTORIES
    "${CMAKE_CURRENT_BINARY_DIR};${CMAKE_CURRENT_BINARY_DIR}/include;${OPENSSL_SOURCE_DIR};${OPENSSL_SOURCE_DIR}/include"
)
add_library(apps.static STATIC ${OPENSSL_SOURCE_DIR}/apps/app_rand.c)
set_target_properties(apps.static PROPERTIES OUTPUT_NAME apps)
set_target_output_subdir(apps.static ARCHIVE_OUTPUT_DIRECTORY apps)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/crypto/include)
configure_file(${CMAKE_CURRENT_LIST_DIR}/darwin/crypto/aes/aes-x86_64.s ${CMAKE_CURRENT_BINARY_DIR}/crypto/aes/aes-x86_64.s COPYONLY)

set_source_files_properties(${OPENSSL_SOURCE_DIR}/initialize.cpp PROPERTIES COMPILE_OPTIONS
    "-fPIC;-DL_ENDIAN;-DOPENSSL_PIC;-DOPENSSL_CPUID_OBJ;-DOPENSSL_IA32_SSE2;-DOPENSSL_BN_ASM_MONT;-DOPENSSL_BN_ASM_MONT5;-DOPENSSL_BN_ASM_GF2m;-DSHA1_ASM;-DSHA256_ASM;-DSHA512_ASM;-DKECCAK1600_ASM;-DRC4_ASM;-DMD5_ASM;-DAES_ASM;-DVPAES_ASM;-DBSAES_ASM;-DGHASH_ASM;-DECP_NISTZ256_ASM;-DX25519_ASM;-DPADLOCK_ASM;-DPOLY1305_ASM;-DOPENSSLDIR=\"/usr/local/ssl\";-DENGINESDIR=\".\""
)
set_source_files_properties(${OPENSSL_SOURCE_DIR}/initialize.cpp PROPERTIES INCLUDE_DIRECTORIES
    "${CMAKE_CURRENT_BINARY_DIR};${CMAKE_CURRENT_BINARY_DIR}/crypto/include;${CMAKE_CURRENT_BINARY_DIR}/include;${OPENSSL_SOURCE_DIR};${OPENSSL_SOURCE_DIR}/crypto/include;${OPENSSL_SOURCE_DIR}/include"
)
set_source_files_properties(${OPENSSL_SOURCE_DIR}/ssl.c PROPERTIES COMPILE_OPTIONS
    "-fPIC;-DL_ENDIAN;-DOPENSSL_PIC;-DOPENSSL_CPUID_OBJ;-DOPENSSL_IA32_SSE2;-DOPENSSL_BN_ASM_MONT;-DOPENSSL_BN_ASM_MONT5;-DOPENSSL_BN_ASM_GF2m;-DSHA1_ASM;-DSHA256_ASM;-DSHA512_ASM;-DKECCAK1600_ASM;-DRC4_ASM;-DMD5_ASM;-DAES_ASM;-DVPAES_ASM;-DBSAES_ASM;-DGHASH_ASM;-DECP_NISTZ256_ASM;-DX25519_ASM;-DPADLOCK_ASM;-DPOLY1305_ASM;-DOPENSSLDIR=\"/usr/local/ssl\";-DENGINESDIR=\".\""
)
set_source_files_properties(${OPENSSL_SOURCE_DIR}/ssl.c PROPERTIES INCLUDE_DIRECTORIES
    "${CMAKE_CURRENT_BINARY_DIR};${CMAKE_CURRENT_BINARY_DIR}/crypto/include;${CMAKE_CURRENT_BINARY_DIR}/include;${OPENSSL_SOURCE_DIR};${OPENSSL_SOURCE_DIR}/crypto/include;${OPENSSL_SOURCE_DIR}/include"
)
set_source_files_properties(${CMAKE_CURRENT_BINARY_DIR}/crypto/aes/aes-x86_64.s PROPERTIES COMPILE_OPTIONS
    "-fPIC;-DL_ENDIAN;-DOPENSSL_PIC;-DOPENSSL_CPUID_OBJ;-DOPENSSL_IA32_SSE2;-DOPENSSL_BN_ASM_MONT;-DOPENSSL_BN_ASM_MONT5;-DOPENSSL_BN_ASM_GF2m;-DSHA1_ASM;-DSHA256_ASM;-DSHA512_ASM;-DKECCAK1600_ASM;-DRC4_ASM;-DMD5_ASM;-DAES_ASM;-DVPAES_ASM;-DBSAES_ASM;-DGHASH_ASM;-DECP_NISTZ256_ASM;-DX25519_ASM;-DPADLOCK_ASM;-DPOLY1305_ASM;-DOPENSSLDIR=\"/usr/local/ssl\";-DENGINESDIR=\".\""
)
add_library(openssl_1_1 SHARED
    ${OPENSSL_SOURCE_DIR}/initialize.cpp
    ${OPENSSL_SOURCE_DIR}/ssl.c
    ${CMAKE_CURRENT_BINARY_DIR}/crypto/aes/aes-x86_64.s
)
set_target_properties(openssl_1_1 PROPERTIES VERSION 1.1)
set_target_properties(openssl_1_1 PROPERTIES SOVERSION 1.1)
configure_file(${CMAKE_CURRENT_LIST_DIR}/darwin/apps/progs.h ${CMAKE_CURRENT_BINARY_DIR}/apps/progs.h COPYONLY)

set_source_files_properties(${OPENSSL_SOURCE_DIR}/apps/asn1pars.c PROPERTIES COMPILE_OPTIONS -fPIC)
set_source_files_properties(${OPENSSL_SOURCE_DIR}/apps/asn1pars.c PROPERTIES INCLUDE_DIRECTORIES
    "${CMAKE_CURRENT_BINARY_DIR};${CMAKE_CURRENT_BINARY_DIR}/include;${CMAKE_CURRENT_BINARY_DIR}/apps;${OPENSSL_SOURCE_DIR};${OPENSSL_SOURCE_DIR}/include"
)
add_executable(openssl ${OPENSSL_SOURCE_DIR}/apps/asn1pars.c)
target_link_libraries(openssl PRIVATE apps.static openssl_1_1)
set_target_output_subdir(openssl RUNTIME_OUTPUT_DIRECTORY apps)
