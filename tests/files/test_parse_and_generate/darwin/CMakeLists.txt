cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

set_source_files_properties(${SOURCE_DIR}/foo.c PROPERTIES COMPILE_OPTIONS
    "-Wall;-fno-common;-pthread;-g;-fPIC;-UNDEBUG;-DPACKAGE_NAME=\"\";-DPACKAGE_TARNAME=\"\";-DHAVE_SYSCALL=1;-D_PR_PTHREADS;-UHAVE_CVAR_BUILT_ON_SEM"
)
set_source_files_properties(${SOURCE_DIR}/foo.c PROPERTIES INCLUDE_DIRECTORIES "${SOURCE_DIR}")
add_library(foo1.static STATIC ${SOURCE_DIR}/foo.c)
set_target_properties(foo1.static PROPERTIES OUTPUT_NAME foo1)
set_target_output_subdir(foo1.static ARCHIVE_OUTPUT_DIRECTORY lib)

add_library(foo2.static STATIC ${SOURCE_DIR}/foo.c)
set_target_properties(foo2.static PROPERTIES OUTPUT_NAME foo2)
set_target_output_subdir(foo2.static ARCHIVE_OUTPUT_DIRECTORY lib)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/libbar.def ${CMAKE_CURRENT_BINARY_DIR}/libbar.def COPYONLY)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/lib)

set_source_files_properties(${SOURCE_DIR}/bar.c PROPERTIES COMPILE_OPTIONS
    "-DDARWIN;-fasm-blocks;-mpascal-strings;-gdwarf-2;-Wno-error;-fPIC;-fno-common;-Werror;-Wall;-Wno-array-bounds;-Wno-unevaluated-expression;-Wno-parentheses-equality;-Wshadow"
)
set_source_files_properties(${SOURCE_DIR}/bar.c PROPERTIES INCLUDE_DIRECTORIES "${SOURCE_DIR}")
add_library(bar SHARED ${SOURCE_DIR}/bar.c)
target_link_options(bar PRIVATE
    -all_load
    -install_name
    @executable_path/libbar.dylib
    -headerpad_max_install_names
    -stdlib=libc++
    -exported_symbols_list
    ${CMAKE_CURRENT_BINARY_DIR}/libbar.def
    -Wl,-search_paths_first
    -Wl,-headerpad_max_install_names
)
target_link_libraries(bar PRIVATE foo1.static)
set_target_output_subdir(bar LIBRARY_OUTPUT_DIRECTORY lib)
set_target_output_subdir(bar RUNTIME_OUTPUT_DIRECTORY lib)
set_target_properties(bar PROPERTIES VERSION 1)
set_target_properties(bar PROPERTIES SOVERSION 1)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/bin)

set_source_files_properties(${SOURCE_DIR}/main.cpp PROPERTIES COMPILE_OPTIONS
    "-fasm-blocks;-mpascal-strings;-gdwarf-2;-Wno-error;-std=c++0x;-fPIC;-fno-common;-Werror;-Wall;-Wno-array-bounds;-Wno-unevaluated-expression;-Wno-parentheses-equality;-Wshadow"
)
set_source_files_properties(${SOURCE_DIR}/main.cpp PROPERTIES INCLUDE_DIRECTORIES "${SOURCE_DIR}")
add_executable(test ${SOURCE_DIR}/main.cpp)
target_link_options(test PRIVATE -Wl,-dead_strip)
target_link_libraries(test PRIVATE foo1.static bar foo2.static)
set_target_output_subdir(test RUNTIME_OUTPUT_DIRECTORY bin)
