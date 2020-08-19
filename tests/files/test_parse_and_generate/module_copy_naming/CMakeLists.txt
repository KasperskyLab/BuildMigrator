cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(utils.2.0.0 SHARED ${SOURCE_DIR}/library.cpp)
target_link_libraries(utils.2.0.0 PRIVATE m)
set_target_properties(utils.2.0.0 PROPERTIES OUTPUT_NAME utils)
set_target_properties(utils.2.0.0 PROPERTIES VERSION 2.0.0)

add_executable(app ${SOURCE_DIR}/main.cpp)
target_link_libraries(app PRIVATE utils.2.0.0)
