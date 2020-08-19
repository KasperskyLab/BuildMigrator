cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(a SHARED ${SOURCE_DIR}/a.c)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/a.o ${CMAKE_CURRENT_BINARY_DIR}/a.o COPYONLY)

set_source_files_properties(${CMAKE_CURRENT_BINARY_DIR}/a.o PROPERTIES EXTERNAL_OBJECT ON)
add_library(test SHARED ${CMAKE_CURRENT_BINARY_DIR}/a.o)
set_target_properties(test PROPERTIES LINKER_LANGUAGE C)
target_link_options(test PRIVATE -Wl,-z,relro,-z,now)
target_link_libraries(test PRIVATE Threads::Threads)
