cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
add_link_options(/LTCG /WX)
static_library_options(/LTCG /WX)
link_libraries(comctl32 ws2_32 delayimp)

add_library(common.static STATIC ${SOURCE_DIR}/2.c)
set_target_properties(common.static PROPERTIES OUTPUT_NAME common)

add_library(shared SHARED ${SOURCE_DIR}/1.c)
target_link_libraries(shared PRIVATE common.static)

add_executable(app ${SOURCE_DIR}/3.c)
target_link_libraries(app PRIVATE common.static)
