cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(ALIAS ${SOURCE_DIR}/alias CACHE STRING "")
configure_file(${SOURCE_DIR}/main.cpp ${CMAKE_CURRENT_BINARY_DIR}/main_cp.cpp COPYONLY)

add_executable(main_cp ${CMAKE_CURRENT_BINARY_DIR}/main_cp.cpp)

add_executable(main ${SOURCE_DIR}/main.cpp)
configure_file(${SOURCE_DIR}/main.cpp ${CMAKE_CURRENT_BINARY_DIR}/main_ln.cpp COPYONLY)

add_executable(main_ln ${CMAKE_CURRENT_BINARY_DIR}/main_ln.cpp)
configure_file(${SOURCE_DIR}/main.cpp ${CMAKE_CURRENT_BINARY_DIR}/main_mv.cpp COPYONLY)

add_executable(main_mv ${CMAKE_CURRENT_BINARY_DIR}/main_mv.cpp)
configure_file(${CMAKE_CURRENT_BINARY_DIR}/main_cp.cpp ${CMAKE_CURRENT_BINARY_DIR}/main_cp_ln.cpp COPYONLY)

add_executable(main_cp_ln ${CMAKE_CURRENT_BINARY_DIR}/main_cp_ln.cpp)
configure_file(${ALIAS}/alias.cpp ${CMAKE_CURRENT_BINARY_DIR}/alias.cpp COPYONLY)

add_executable(alias ${CMAKE_CURRENT_BINARY_DIR}/alias.cpp)
