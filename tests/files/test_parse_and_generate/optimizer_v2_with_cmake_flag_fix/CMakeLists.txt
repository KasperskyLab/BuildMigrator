cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/includedir1)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/includedir2)

add_library(foo_cpp_1 OBJECT ${SOURCE_DIR}/foo.cpp)
target_compile_options(foo_cpp_1 PRIVATE -DFOO)
target_include_directories(foo_cpp_1 PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/includedir1)

add_library(st.static STATIC $<TARGET_OBJECTS:foo_cpp_1>)
set_target_properties(st.static PROPERTIES LINKER_LANGUAGE C)
set_target_properties(st.static PROPERTIES OUTPUT_NAME st)

add_library(object_lib_2 OBJECT ${SOURCE_DIR}/bar1.cpp ${SOURCE_DIR}/bar2.cpp)
target_include_directories(object_lib_2 PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/includedir2)

add_executable(ex $<TARGET_OBJECTS:foo_cpp_1> $<TARGET_OBJECTS:object_lib_2>)
set_target_properties(ex PROPERTIES LINKER_LANGUAGE C)

add_library(object_lib_1 OBJECT ${SOURCE_DIR}/bar1.cpp ${SOURCE_DIR}/bar2.cpp)
target_compile_options(object_lib_1 PRIVATE -DBAR2)
target_include_directories(object_lib_1 PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/includedir2)

add_library(sh1 SHARED $<TARGET_OBJECTS:foo_cpp_1> $<TARGET_OBJECTS:object_lib_1>)
set_target_properties(sh1 PROPERTIES LINKER_LANGUAGE C)

add_library(sh2 SHARED ${SOURCE_DIR}/baz.c)
