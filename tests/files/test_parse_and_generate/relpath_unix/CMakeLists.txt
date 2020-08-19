cmake_minimum_required(VERSION 3.13)

project(openssl C CXX)
enable_language(ASM)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(OPENSSL_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/crypto/include)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/crypto/aes/aes-x86_64.s ${CMAKE_CURRENT_BINARY_DIR}/crypto/aes/aes-x86_64.s COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/include/openssl/opensslconf.h ${CMAKE_CURRENT_BINARY_DIR}/include/openssl/opensslconf.h COPYONLY)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/ssl)

set_source_files_properties(${OPENSSL_SOURCE_DIR}/initialize.cpp PROPERTIES COMPILE_OPTIONS
    "-std=c++0x;-pthread;-Wall;-Wformat;-Wformat-security;-D_FORTIFY_SOURCE=2;-fno-rtti;-fno-exceptions;-Wa,--noexecstack;-g;-DOPENSSL_USE_NODELETE;-DL_ENDIAN;-DOPENSSL_PIC;-DOPENSSL_CPUID_OBJ;-DOPENSSL_IA32_SSE2;-DOPENSSL_BN_ASM_MONT;-DOPENSSL_BN_ASM_MONT5;-DOPENSSL_BN_ASM_GF2m;-DSHA1_ASM;-DSHA256_ASM;-DSHA512_ASM;-DKECCAK1600_ASM;-DRC4_ASM;-DMD5_ASM;-DAES_ASM;-DVPAES_ASM;-DBSAES_ASM;-DGHASH_ASM;-DECP_NISTZ256_ASM;-DX25519_ASM;-DPADLOCK_ASM;-DPOLY1305_ASM;-DOPENSSLDIR=\"/mnt/d/src/3rd_party_gen/.build_linux/externals/openssl/1.1.1/openssl_install/ssl\";-DENGINESDIR=\"/mnt/d/src/3rd_party_gen/.build_linux/externals/openssl/1.1.1/openssl_install/lib/engines-1.1\""
)
set_source_files_properties(${OPENSSL_SOURCE_DIR}/initialize.cpp PROPERTIES INCLUDE_DIRECTORIES
    "${CMAKE_CURRENT_BINARY_DIR};${CMAKE_CURRENT_BINARY_DIR}/crypto/include;${CMAKE_CURRENT_BINARY_DIR}/include;${OPENSSL_SOURCE_DIR};${OPENSSL_SOURCE_DIR}/crypto/include;${OPENSSL_SOURCE_DIR}/include"
)
set_source_files_properties(${CMAKE_CURRENT_BINARY_DIR}/crypto/aes/aes-x86_64.s PROPERTIES COMPILE_OPTIONS
    "-fPIC;-pthread;-Wa,--noexecstack;-Wall;-Wformat;-Wformat-security;-D_FORTIFY_SOURCE=2;-fno-rtti;-fno-exceptions;-g;-DOPENSSL_USE_NODELETE;-DL_ENDIAN;-DOPENSSL_PIC;-DOPENSSL_CPUID_OBJ;-DOPENSSL_IA32_SSE2;-DOPENSSL_BN_ASM_MONT;-DOPENSSL_BN_ASM_MONT5;-DOPENSSL_BN_ASM_GF2m;-DSHA1_ASM;-DSHA256_ASM;-DSHA512_ASM;-DKECCAK1600_ASM;-DRC4_ASM;-DMD5_ASM;-DAES_ASM;-DVPAES_ASM;-DBSAES_ASM;-DGHASH_ASM;-DECP_NISTZ256_ASM;-DX25519_ASM;-DPADLOCK_ASM;-DPOLY1305_ASM;-DOPENSSLDIR=\"/mnt/d/src/3rd_party_gen/.build_linux/externals/openssl/1.1.1/openssl_install/ssl\";-DENGINESDIR=\"/mnt/d/src/3rd_party_gen/.build_linux/externals/openssl/1.1.1/openssl_install/lib/engines-1.1\""
)
set_source_files_properties(${OPENSSL_SOURCE_DIR}/ssl/tls_srp.c PROPERTIES COMPILE_OPTIONS
    "-fPIC;-pthread;-Wa,--noexecstack;-Wall;-Wformat;-Wformat-security;-D_FORTIFY_SOURCE=2;-fno-rtti;-fno-exceptions;-g;-DOPENSSL_USE_NODELETE;-DL_ENDIAN;-DOPENSSL_PIC;-DOPENSSL_CPUID_OBJ;-DOPENSSL_IA32_SSE2;-DOPENSSL_BN_ASM_MONT;-DOPENSSL_BN_ASM_MONT5;-DOPENSSL_BN_ASM_GF2m;-DSHA1_ASM;-DSHA256_ASM;-DSHA512_ASM;-DKECCAK1600_ASM;-DRC4_ASM;-DMD5_ASM;-DAES_ASM;-DVPAES_ASM;-DBSAES_ASM;-DGHASH_ASM;-DECP_NISTZ256_ASM;-DX25519_ASM;-DPADLOCK_ASM;-DPOLY1305_ASM;-DOPENSSLDIR=\"/mnt/d/src/3rd_party_gen/.build_linux/externals/openssl/1.1.1/openssl_install/ssl\";-DENGINESDIR=\"/mnt/d/src/3rd_party_gen/.build_linux/externals/openssl/1.1.1/openssl_install/lib/engines-1.1\""
)
set_source_files_properties(${OPENSSL_SOURCE_DIR}/ssl/tls_srp.c PROPERTIES INCLUDE_DIRECTORIES
    "${CMAKE_CURRENT_BINARY_DIR};${CMAKE_CURRENT_BINARY_DIR}/crypto/include;${CMAKE_CURRENT_BINARY_DIR}/include;${OPENSSL_SOURCE_DIR};${OPENSSL_SOURCE_DIR}/crypto/include;${OPENSSL_SOURCE_DIR}/include"
)
add_library(openssl_1_1.static STATIC
    ${OPENSSL_SOURCE_DIR}/initialize.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/crypto/aes/aes-x86_64.s
    ${OPENSSL_SOURCE_DIR}/ssl/tls_srp.c
)
set_target_properties(openssl_1_1.static PROPERTIES OUTPUT_NAME openssl_1_1)
