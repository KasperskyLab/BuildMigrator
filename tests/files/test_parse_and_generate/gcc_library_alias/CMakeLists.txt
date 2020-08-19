cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(ALIAS1 ${CMAKE_CURRENT_BINARY_DIR}/libimpl1.a CACHE STRING "")
set(ALIAS2 ${CMAKE_CURRENT_BINARY_DIR}/libimpl2.a CACHE STRING "")

add_library(util.static STATIC ${SOURCE_DIR}/util.c)
set_target_properties(util.static PROPERTIES OUTPUT_NAME util)

# Workaround for CMake error: 'No SOURCES given to target' / 'no source files for target'
if(NOT EXISTS ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
    file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/empty.c "")
endif()
add_library(public SHARED ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
target_link_libraries(public PRIVATE m ${ALIAS1} ${ALIAS2} util.static)
