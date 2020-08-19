cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(a_o OBJECT ${SOURCE_DIR}/a.c)

add_library(a SHARED $<TARGET_OBJECTS:a_o>)
set_target_properties(a PROPERTIES LINKER_LANGUAGE C)

add_library(d.o ALIAS a_o)
