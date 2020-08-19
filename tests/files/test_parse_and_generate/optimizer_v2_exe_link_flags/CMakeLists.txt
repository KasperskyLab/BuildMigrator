cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
executable_link_options(-pthread -Wl,-z,now -Wl,-z,relro)

add_executable(app1 ${SOURCE_DIR}/1.c)
target_link_options(app1 PRIVATE -static-libgcc)
target_link_libraries(app1 PRIVATE m)

add_executable(app2 ${SOURCE_DIR}/2.c)
target_link_libraries(app2 PRIVATE m rt)

add_library(shared SHARED ${SOURCE_DIR}/3.c)
