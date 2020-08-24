cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(impl1.static STATIC ${SOURCE_DIR}/impl.c)
set_target_properties(impl1.static PROPERTIES OUTPUT_NAME impl1)

# Workaround for CMake error: 'No SOURCES given to target' / 'no source files for target'
if(NOT EXISTS ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
    file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/empty.c "")
endif()
add_library(impl SHARED ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
target_link_options(impl PRIVATE -z noexecstack -Wl,-z,defs)
target_link_libraries(impl PRIVATE m -Wl,-whole-archive impl1.static -Wl,-no-whole-archive)
