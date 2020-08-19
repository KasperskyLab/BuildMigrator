cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/lib)

add_library(_a SHARED ${SOURCE_DIR}/dllmain_a.c)
set_target_properties(_a PROPERTIES OUTPUT_NAME lib_a)
set_target_output_subdir(_a RUNTIME_OUTPUT_DIRECTORY lib)
set_target_output_subdir(_a ARCHIVE_OUTPUT_DIRECTORY lib)

add_library(_b SHARED ${SOURCE_DIR}/dllmain_b.c)
set_target_properties(_b PROPERTIES OUTPUT_NAME lib_b)
set_target_output_subdir(_b RUNTIME_OUTPUT_DIRECTORY lib)
set_target_output_subdir(_b ARCHIVE_OUTPUT_DIRECTORY lib)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/bin)

add_executable(app_a ${SOURCE_DIR}/main_a.c)
set_target_output_subdir(app_a RUNTIME_OUTPUT_DIRECTORY bin)

add_executable(app_b ${SOURCE_DIR}/main_b.c)
set_target_output_subdir(app_b RUNTIME_OUTPUT_DIRECTORY bin)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/README.md ${CMAKE_CURRENT_BINARY_DIR}/README.md COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/README.txt ${CMAKE_CURRENT_BINARY_DIR}/README.txt COPYONLY)
