cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
include_directories(${SOURCE_DIR})

add_library(b.static STATIC ${SOURCE_DIR}/b.cpp)
set_target_properties(b.static PROPERTIES OUTPUT_NAME b)

set_source_files_properties(${SOURCE_DIR}/a.cpp PROPERTIES COMPILE_OPTIONS -DMSG_A="a")
add_library(a1 SHARED ${SOURCE_DIR}/main.cpp ${SOURCE_DIR}/a.cpp)
target_link_libraries(a1 PRIVATE b.static)

add_library(a2 SHARED ${SOURCE_DIR}/main.cpp ${SOURCE_DIR}/a.cpp)
target_link_libraries(a2 PRIVATE b.static)

add_executable(a3 ${SOURCE_DIR}/main.cpp ${SOURCE_DIR}/a.cpp)
target_link_libraries(a3 PRIVATE b.static)

add_executable(a4 ${SOURCE_DIR}/main.cpp ${SOURCE_DIR}/a.cpp)
target_link_libraries(a4 PRIVATE b.static)
