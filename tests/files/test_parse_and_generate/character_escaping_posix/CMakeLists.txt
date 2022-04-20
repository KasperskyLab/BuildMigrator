cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_executable(test ${SOURCE_DIR}/a.c)
target_compile_options(test PRIVATE
    "-DOPENSSL_DIR=\"/Program Files (x86)/OpenSSL\""
    -DASTERISK=*
    -DXERCES_DLL_NAME="xerces-c_3_2.dll\\0"
)
