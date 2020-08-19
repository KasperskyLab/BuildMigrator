cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
add_link_options(-pthread -static-libgcc -Wl,-z,now -Wl,-z,relro)
link_libraries(m)

add_executable(app ${SOURCE_DIR}/1.c)

add_library(shared SHARED ${SOURCE_DIR}/2.c)

add_library(extra.static STATIC ${SOURCE_DIR}/3.c)
set_target_properties(extra.static PROPERTIES OUTPUT_NAME extra)
