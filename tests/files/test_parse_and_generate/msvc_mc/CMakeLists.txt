cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)
enable_language(RC)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/generated)

find_program(MC mc)
if(NOT MC)
    message(FATAL_ERROR "mc not found")
endif()

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/generated/manifest.h
    ${CMAKE_CURRENT_BINARY_DIR}/generated/manifest.rc
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${MC} -h ${CMAKE_CURRENT_BINARY_DIR}/generated -r ${CMAKE_CURRENT_BINARY_DIR}/generated ${SOURCE_DIR}/manifest.mc
    DEPENDS
        ${SOURCE_DIR}/manifest.mc
    VERBATIM
)
add_custom_target(generated_manifest_h ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/generated/manifest.h
    ${CMAKE_CURRENT_BINARY_DIR}/generated/manifest.rc)

add_executable(main
    ${SOURCE_DIR}/main.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/generated/manifest.rc
)
target_language_include_directories(main CXX PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
add_dependencies(main generated_manifest_h)
