cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/build1.h ${CMAKE_CURRENT_BINARY_DIR}/build1.h COPYONLY)

add_executable(main1 ${SOURCE_DIR}/main.cpp)
target_compile_options(main1 PRIVATE -DBUILD1)
target_include_directories(main1 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/build2.h ${CMAKE_CURRENT_BINARY_DIR}/build2.h COPYONLY)

add_executable(main2 ${SOURCE_DIR}/main.cpp)
target_compile_options(main2 PRIVATE -DBUILD2)
target_include_directories(main2 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
