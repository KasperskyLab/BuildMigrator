cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/obj)

set_source_files_properties(${SOURCE_DIR}/file1.cpp PROPERTIES COMPILE_OPTIONS
    "/W3;/WX-;/diagnostics:classic;/Ob2;/Oi;/Ot;/Oy;/GF;/MT$<$<CONFIG:Debug>:d>;/GS;/Gy;/fp:precise;/Zc:wchar_t;/Zc:forScope;/Zc:inline;/GR-;/Gd;/wd4351;/wd4355;/wd4800;/wd4251;/wd4275;/wd4244;/wd4267;/errorReport:queue"
)
set_source_files_properties(${SOURCE_DIR}/file1.cpp PROPERTIES INCLUDE_DIRECTORIES "${SOURCE_DIR}")
set_source_files_properties(${SOURCE_DIR}/file2.cpp PROPERTIES COMPILE_OPTIONS
    "/W3;/WX-;/diagnostics:classic;/Ob2;/Oi;/Ot;/Oy;/GF;/MT$<$<CONFIG:Debug>:d>;/GS;/Gy;/fp:precise;/Zc:wchar_t;/Zc:forScope;/Zc:inline;/GR-;/Gd;/wd4351;/wd4355;/wd4800;/wd4251;/wd4275;/wd4244;/wd4267;/errorReport:queue"
)
set_source_files_properties(${SOURCE_DIR}/file2.cpp PROPERTIES INCLUDE_DIRECTORIES "${SOURCE_DIR}")
add_library(out_static.static STATIC ${SOURCE_DIR}/file1.cpp ${SOURCE_DIR}/file2.cpp)
set_target_properties(out_static.static PROPERTIES OUTPUT_NAME out_static)

set_source_files_properties(${SOURCE_DIR}/file3.cpp PROPERTIES COMPILE_OPTIONS
    "/W3;/WX-;/diagnostics:classic;/Ob2;/Oi;/Ot;/Oy;/GF;/MT$<$<CONFIG:Debug>:d>;/GS;/Gy;/fp:precise;/Zc:wchar_t;/Zc:forScope;/Zc:inline;/GR-;/Gd;/wd4351;/wd4355;/wd4800;/wd4251;/wd4275;/wd4244;/wd4267;/errorReport:queue"
)
set_source_files_properties(${SOURCE_DIR}/file3.cpp PROPERTIES INCLUDE_DIRECTORIES "${SOURCE_DIR}")
add_library(out_static2.static STATIC ${SOURCE_DIR}/file3.cpp)
set_target_properties(out_static2.static PROPERTIES OUTPUT_NAME out_static2)

add_executable(out ${SOURCE_DIR}/file1.cpp ${SOURCE_DIR}/file2.cpp)
target_link_options(out PRIVATE
    /ERRORREPORT:QUEUE
    /TLBID:1
    /DYNAMICBASE
    /NXCOMPAT
    /SubSystem:Console,5.02
)
