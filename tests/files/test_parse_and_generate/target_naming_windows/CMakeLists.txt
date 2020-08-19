cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/impl/libtest)

add_library(libtest_dll SHARED ${SOURCE_DIR}/libtest.cpp)
set_target_properties(libtest_dll PROPERTIES OUTPUT_NAME libtest)
set_target_output_subdir(libtest_dll RUNTIME_OUTPUT_DIRECTORY impl/libtest)
set_target_output_subdir(libtest_dll ARCHIVE_OUTPUT_DIRECTORY impl/libtest)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/impl/test)

add_library(impl_test_test SHARED ${SOURCE_DIR}/test.cpp)
set_target_properties(impl_test_test PROPERTIES OUTPUT_NAME test)
set_target_output_subdir(impl_test_test RUNTIME_OUTPUT_DIRECTORY impl/test)
set_target_output_subdir(impl_test_test ARCHIVE_OUTPUT_DIRECTORY impl/test)

add_library(test.static STATIC ${SOURCE_DIR}/dllmain.cpp)
target_link_libraries(test.static PRIVATE libtest_dll)
set_target_properties(test.static PROPERTIES OUTPUT_NAME libtest)

add_library(test SHARED ${SOURCE_DIR}/dllmain.cpp)
target_link_libraries(test PRIVATE impl_test_test)

add_library(lib.static STATIC ${SOURCE_DIR}/lib.cpp)
set_target_properties(lib.static PROPERTIES OUTPUT_NAME lib)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/impl)

add_library(impl_lib.static STATIC ${SOURCE_DIR}/lib.cpp)
set_target_properties(impl_lib.static PROPERTIES OUTPUT_NAME lib)
set_target_output_subdir(impl_lib.static ARCHIVE_OUTPUT_DIRECTORY impl)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/test)

add_library(lib SHARED ${SOURCE_DIR}/lib.cpp)
target_link_libraries(lib PRIVATE impl_lib.static)
set_target_output_subdir(lib RUNTIME_OUTPUT_DIRECTORY test)
set_target_output_subdir(lib ARCHIVE_OUTPUT_DIRECTORY test)

add_executable(app ${SOURCE_DIR}/main.cpp)

add_executable(test_app ${SOURCE_DIR}/main.cpp)
set_target_properties(test_app PROPERTIES OUTPUT_NAME app)
set_target_output_subdir(test_app RUNTIME_OUTPUT_DIRECTORY test)
