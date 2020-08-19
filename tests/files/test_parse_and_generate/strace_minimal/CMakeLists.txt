cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/CMakeFiles/lib.dir)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/CMakeFiles/main.dir)

add_library(lib.static STATIC ${SOURCE_DIR}/lib.c ${SOURCE_DIR}/main.cpp)
set_target_properties(lib.static PROPERTIES OUTPUT_NAME lib)

add_executable(main ${SOURCE_DIR}/main.cpp)
target_link_libraries(main PRIVATE lib.static)
