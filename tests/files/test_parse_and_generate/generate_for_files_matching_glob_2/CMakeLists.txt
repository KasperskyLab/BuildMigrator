cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/lib)

add_library(_0-9__dll SHARED ${SOURCE_DIR}/dllmain_b.c)
set_target_properties(_0-9__dll PROPERTIES OUTPUT_NAME [0-9])
set_target_output_subdir(_0-9__dll RUNTIME_OUTPUT_DIRECTORY lib)
set_target_output_subdir(_0-9__dll ARCHIVE_OUTPUT_DIRECTORY lib)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/bin)

add_executable(_0-9__exe ${SOURCE_DIR}/main_b.c)
set_target_properties(_0-9__exe PROPERTIES OUTPUT_NAME [0-9])
set_target_output_subdir(_0-9__exe RUNTIME_OUTPUT_DIRECTORY bin)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/README.[0-9] ${CMAKE_CURRENT_BINARY_DIR}/README.[0-9] COPYONLY)
