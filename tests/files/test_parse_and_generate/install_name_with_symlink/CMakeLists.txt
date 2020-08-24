cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(jsoncpp SHARED ${SOURCE_DIR}/libjsoncpp.cpp)
target_link_options(jsoncpp PRIVATE
    -Wl,-headerpad_max_install_names
    -install_name
    libjsoncpp.1.dylib
)
target_compile_options(jsoncpp PRIVATE -std=c++11 -fstack-protector)
set_target_properties(jsoncpp PROPERTIES VERSION 1.7.2)
set_target_properties(jsoncpp PROPERTIES SOVERSION 1.0.0)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/libjsoncpp.1.dylib
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_COMMAND} -E create_symlink libjsoncpp.1.7.2.dylib ${CMAKE_CURRENT_BINARY_DIR}/libjsoncpp.1.dylib
    DEPENDS
        jsoncpp
    VERBATIM
)
add_custom_target(libjsoncpp_1_dylib ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/libjsoncpp.1.dylib)

add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/libjsoncpp.dylib
    COMMAND
        ${CMAKE_COMMAND} -E env
        ${CMAKE_COMMAND} -E create_symlink libjsoncpp.1.7.2.dylib ${CMAKE_CURRENT_BINARY_DIR}/libjsoncpp.dylib
    DEPENDS
        jsoncpp
    VERBATIM
)
add_custom_target(libjsoncpp_dylib ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/libjsoncpp.dylib)
