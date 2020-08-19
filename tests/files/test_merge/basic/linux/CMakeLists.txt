# CMAKE_SYSTEM STREQUAL "Linux"
cmake_minimum_required(VERSION 3.8)

project(openssl C CXX)
enable_language(ASM)

include(cmake_framework)
include(system)
find_thread_library()

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(COMPILE_FLAGS
    -DAES_ASM
    -DBSAES_ASM
    -DECP_NISTZ256_ASM
    -DENGINESDIR="/mnt/d/src/3rd_party_gen/.build_linux/externals/openssl/1.1.1/openssl_install/lib/engines-1.1"
    -DGHASH_ASM
    -DKECCAK1600_ASM
    -DL_ENDIAN
    -DMD5_ASM
    -DNDEBUG
    -DOPENSSLDIR="/mnt/d/src/3rd_party_gen/.build_linux/externals/openssl/1.1.1/openssl_install/ssl"
    -DOPENSSL_BN_ASM_GF2m
    -DOPENSSL_BN_ASM_MONT
    -DOPENSSL_BN_ASM_MONT5
    -DOPENSSL_CPUID_OBJ
    -DOPENSSL_IA32_SSE2
    -DOPENSSL_PIC
    -DOPENSSL_USE_NODELETE
    -DPADLOCK_ASM
    -DPOLY1305_ASM
    -DRC4_ASM
    -DSHA1_ASM
    -DSHA256_ASM
    -DSHA512_ASM
    -DVPAES_ASM
    -DX25519_ASM
    -D_FORTIFY_SOURCE=2
    -Wa,--noexecstack
    -fPIC
    -fno-exceptions
    -fno-rtti
    -m64
    -std=c++0x
    CACHE STRING ""
)
set(LINK_FLAGS "" CACHE STRING "")
set(INCLUDE_DIRS
    ${CMAKE_CURRENT_BINARY_DIR}
    ${CMAKE_CURRENT_BINARY_DIR}/crypto/include
    ${CMAKE_CURRENT_BINARY_DIR}/include
    ${SOURCE_DIR}
    ${SOURCE_DIR}/crypto/include
    ${SOURCE_DIR}/include
    CACHE STRING ""
)

set(copy_prebuilt_artifacts_DIR prebuilt)
set(copy_prebuilt_artifacts_DEST ${CMAKE_CURRENT_BINARY_DIR})
file(GLOB_RECURSE _files RELATIVE ${CMAKE_CURRENT_LIST_DIR}/${copy_prebuilt_artifacts_DIR} ${copy_prebuilt_artifacts_DIR}/*)
foreach(_f ${_files})
    configure_file(${copy_prebuilt_artifacts_DIR}/${_f} ${copy_prebuilt_artifacts_DEST}/${_f} COPYONLY)
endforeach()

add_library(openssl_1_1.static
    ${SOURCE_DIR}/initialize.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/crypto/aes/aes-x86_64.s
    ${SOURCE_DIR}/ssl/tls_srp.c
)
target_link_libraries(openssl_1_1.static PRIVATE Threads::Threads)
target_compile_options(openssl_1_1.static PRIVATE ${COMPILE_FLAGS})
target_include_directories(openssl_1_1.static PRIVATE ${INCLUDE_DIRS})
set_target_properties(openssl_1_1.static PROPERTIES OUTPUT_NAME openssl_1_1)
