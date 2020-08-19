cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
shared_link_options(-pthread -Wl,-z,now -Wl,-z,relro)

add_library(shared1 SHARED ${SOURCE_DIR}/1.c)
target_link_options(shared1 PRIVATE -static-libgcc)
target_link_libraries(shared1 PRIVATE m)

add_library(shared2 SHARED ${SOURCE_DIR}/2.c)
target_link_libraries(shared2 PRIVATE m rt)

add_executable(app ${SOURCE_DIR}/3.c)
