cmake_minimum_required(VERSION 3.8)

project(openssl C CXX)
if(NOT (CMAKE_SYSTEM STREQUAL "Linux" OR CMAKE_SYSTEM STREQUAL "Windows"))
    message(FATAL_ERROR "Current toolchain is not supported by this project [ ${CMAKE_SYSTEM_NAME} ${CMAKE_SYSTEM_PROCESSOR} ${CMAKE_SIZEOF_VOID_P} ${CMAKE_C_COMPILER_ID} ${CMAKE_CXX_COMPILER_ID} ]")
endif()
if(CMAKE_SYSTEM STREQUAL "Linux")
    enable_language(ASM)
endif()
if(CMAKE_SYSTEM STREQUAL "Windows")
    enable_language(ASM_NASM)
    enable_language(RC)
endif()

include(cmake_framework)
include(system)
find_thread_library()

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
if(CMAKE_SYSTEM STREQUAL "Linux")
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
endif()
if(CMAKE_SYSTEM STREQUAL "Windows")
    set(COMPILE_FLAGS
        -DAES_ASM
        -DECP_NISTZ256_ASM
        -DENGINESDIR="D:\\src\\3rd_party_gen\\.build_win\\externals\\openssl\\1.1.1\\openssl_package\\lib\\engines-1_1"
        -DGHASH_ASM
        -DL_ENDIAN
        -DMD5_ASM
        -DNDEBUG
        -DOPENSSLDIR="C:\\openssl"
        -DOPENSSL_BN_ASM_GF2m
        -DOPENSSL_BN_ASM_MONT
        -DOPENSSL_BN_ASM_PART_WORDS
        -DOPENSSL_CPUID_OBJ
        -DOPENSSL_IA32_SSE2
        -DOPENSSL_PIC
        -DOPENSSL_SYS_WIN32
        -DOPENSSL_USE_APPLINK
        -DPADLOCK_ASM
        -DPOLY1305_ASM
        -DRC4_ASM
        -DRMD160_ASM
        -DSHA1_ASM
        -DSHA256_ASM
        -DSHA512_ASM
        -DUNICODE
        -DVPAES_ASM
        -DWHIRLPOOL_ASM
        -DWIN32_LEAN_AND_MEAN
        -D_CRT_SECURE_NO_DEPRECATE
        -D_UNICODE
        -D_WIN32_WINNT=0x0501
        -D_WINSOCK_DEPRECATED_NO_WARNINGS
        /GL
        /Gw
        /Oy-
        /Zc:threadSafeInit-
        /arch:IA32
        /bigobj
        CACHE STRING ""
    )
endif()
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

if(CMAKE_SYSTEM STREQUAL "Linux")
    add_library(openssl_1_1.static
        ${SOURCE_DIR}/initialize.cpp
        ${CMAKE_CURRENT_BINARY_DIR}/crypto/aes/aes-x86_64.s
        ${SOURCE_DIR}/ssl/tls_srp.c
    )
    target_link_libraries(openssl_1_1.static PRIVATE Threads::Threads)
    target_compile_options(openssl_1_1.static PRIVATE ${COMPILE_FLAGS})
    target_include_directories(openssl_1_1.static PRIVATE ${INCLUDE_DIRS})
    set_target_properties(openssl_1_1.static PROPERTIES OUTPUT_NAME openssl_1_1)
endif()
if(CMAKE_SYSTEM STREQUAL "Windows")
    add_library(openssl_1_1
        ${CMAKE_CURRENT_BINARY_DIR}/libcrypto.def
        ${SOURCE_DIR}/crypto/dllmain.c
        ${CMAKE_CURRENT_BINARY_DIR}/libcrypto.rc
        ${CMAKE_CURRENT_BINARY_DIR}/crypto/aes/aes-586.asm
        ${SOURCE_DIR}/initialize.cpp
        ${SOURCE_DIR}/ssl/tls_srp.c
    )
    set_target_properties(openssl_1_1 PROPERTIES LINK_FLAGS "${LINK_FLAGS}")
    target_compile_options(openssl_1_1 PRIVATE ${COMPILE_FLAGS})
    target_include_directories(openssl_1_1 PRIVATE ${INCLUDE_DIRS})
endif()
