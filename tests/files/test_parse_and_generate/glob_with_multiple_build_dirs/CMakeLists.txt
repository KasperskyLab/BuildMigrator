cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_executable(main1 ${SOURCE_DIR}/1.c)
target_compile_options(main1 PRIVATE -DBUILD1)
target_include_directories(main1 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})

add_executable(main2 ${SOURCE_DIR}/2.c)
target_compile_options(main2 PRIVATE -DBUILD2)
target_include_directories(main2 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/data/1.dat ${CMAKE_CURRENT_BINARY_DIR}/data/1.dat COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/data/2.dat ${CMAKE_CURRENT_BINARY_DIR}/data/2.dat COPYONLY)
