cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/foo.h ${CMAKE_CURRENT_BINARY_DIR}/foo.h COPYONLY)

set_source_files_properties(${SOURCE_DIR}/foo.mm PROPERTIES COMPILE_OPTIONS
    "-Wall;-fno-common;-pthread;-g;-fPIC;-UNDEBUG;-DPACKAGE_NAME=\"\";-DPACKAGE_TARNAME=\"\";-DHAVE_SYSCALL=1;-D_PR_PTHREADS;-UHAVE_CVAR_BUILT_ON_SEM"
)
set_source_files_properties(${SOURCE_DIR}/foo.mm PROPERTIES INCLUDE_DIRECTORIES "${SOURCE_DIR};${CMAKE_CURRENT_BINARY_DIR}")
add_library(foo.static STATIC ${SOURCE_DIR}/foo.mm)
set_target_properties(foo.static PROPERTIES OUTPUT_NAME foo)
set_target_output_subdir(foo.static ARCHIVE_OUTPUT_DIRECTORY lib)
