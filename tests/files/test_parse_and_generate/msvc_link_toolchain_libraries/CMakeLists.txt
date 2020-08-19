cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(test SHARED ${SOURCE_DIR}/test.cpp)
target_link_options(test PRIVATE /SUBSYSTEM:CONSOLE,5.01)
target_link_libraries(test PRIVATE
    dbghelp
    dnsapi
    msimg32
    odbc32
    odbccp32
    shlwapi
    usp10
    version
    wininet
    winmm
    ws2_32
    delayimp
)
set_target_properties(test PROPERTIES ARCHIVE_OUTPUT_NAME test.dll)
