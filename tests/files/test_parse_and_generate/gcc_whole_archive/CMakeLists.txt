cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(impl1.static STATIC ${SOURCE_DIR}/impl.c)
set_target_properties(impl1.static PROPERTIES OUTPUT_NAME impl1)

add_library(impl2.static STATIC ${SOURCE_DIR}/impl.c)
set_target_properties(impl2.static PROPERTIES OUTPUT_NAME impl2)

add_library(util.static STATIC ${SOURCE_DIR}/util.c)
set_target_properties(util.static PROPERTIES OUTPUT_NAME util)

# Workaround for CMake error: 'No SOURCES given to target' / 'no source files for target'
if(NOT EXISTS ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
    file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/empty.c "")
endif()
add_library(public SHARED ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
target_link_options(public PRIVATE "-z noexecstack" -Wl,-z,defs)
target_link_libraries(public PRIVATE
    m
    -Wl,-whole-archive
    impl1.static
    impl2.static
    -Wl,-no-whole-archive
    util.static
)
