cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/header.h ${CMAKE_CURRENT_BINARY_DIR}/header.h COPYONLY)

add_executable(main1 ${SOURCE_DIR}/main.cpp)
target_include_directories(main1 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})

add_executable(main2 ${SOURCE_DIR}/main.cpp)
target_include_directories(main2 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})

add_executable(main3 ${SOURCE_DIR}/main.cpp)
target_include_directories(main3 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})

add_executable(main4 ${SOURCE_DIR}/main.cpp)
target_include_directories(main4 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})

add_executable(main5 ${SOURCE_DIR}/main.cpp)
target_include_directories(main5 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})

add_executable(main6 ${SOURCE_DIR}/main.cpp)
target_include_directories(main6 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})

add_executable(main7 ${SOURCE_DIR}/main.cpp)
target_include_directories(main7 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})

add_executable(main8 ${SOURCE_DIR}/main.cpp)
target_include_directories(main8 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})

add_executable(main9 ${SOURCE_DIR}/main.cpp)
target_include_directories(main9 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
