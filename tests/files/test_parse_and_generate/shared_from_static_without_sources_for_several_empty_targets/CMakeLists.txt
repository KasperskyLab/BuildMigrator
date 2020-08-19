cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(impl_c_s.static STATIC ${SOURCE_DIR}/impl_c.c)
set_target_properties(impl_c_s.static PROPERTIES OUTPUT_NAME impl_c_s)

# Workaround for CMake error: 'No SOURCES given to target' / 'no source files for target'
if(NOT EXISTS ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
    file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/empty.c "")
endif()
add_library(impl_c SHARED ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
target_link_options(impl_c PRIVATE "-z noexecstack" -Wl,-z,defs)
target_link_libraries(impl_c PRIVATE m -Wl,-whole-archive impl_c_s.static -Wl,-no-whole-archive)

add_library(impl_cpp_s.static STATIC ${SOURCE_DIR}/impl_cpp.cpp)
set_target_properties(impl_cpp_s.static PROPERTIES OUTPUT_NAME impl_cpp_s)

add_library(impl_cpp SHARED ${CMAKE_CURRENT_BINARY_DIR}/empty.c)
target_link_options(impl_cpp PRIVATE "-z noexecstack" -Wl,-z,defs)
target_link_libraries(impl_cpp PRIVATE
    m
    -Wl,-whole-archive
    impl_cpp_s.static
    -Wl,-no-whole-archive
)
