cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

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

add_library(object_lib_1 OBJECT ${SOURCE_DIR}/common1.cpp ${SOURCE_DIR}/common2.cpp)
target_compile_options(object_lib_1 PRIVATE -DA=1)
target_include_directories(object_lib_1 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
add_dependencies(object_lib_1 generated_manifest_h)

add_executable(a ${SOURCE_DIR}/a.cpp $<TARGET_OBJECTS:object_lib_1>)

add_library(object_lib_2 OBJECT ${SOURCE_DIR}/common1.cpp ${SOURCE_DIR}/common2.cpp)
target_compile_options(object_lib_2 PRIVATE -DB=1)
target_include_directories(object_lib_2 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
add_dependencies(object_lib_2 generated_manifest_h)

add_executable(b ${SOURCE_DIR}/b.cpp $<TARGET_OBJECTS:object_lib_2>)
