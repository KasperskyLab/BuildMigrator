cmake_minimum_required(VERSION 3.13)

project(PROJECT CXX)
enable_language(RC)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

set_source_files_properties(${SOURCE_DIR}/version.rc PROPERTIES COMPILE_OPTIONS "-DWIN32;-D_WINDOWS;/l0x0409")
set_source_files_properties(${SOURCE_DIR}/dllmain.cpp PROPERTIES COMPILE_OPTIONS
    "/W3;/WX-;/diagnostics:classic;/Ob2;/Oy-;-DWIN32;-D_WINDOWS;-Dtest_EXPORTS;-D_WINDLL;-D_MBCS;/EHsc;/MD$<$<CONFIG:Debug>:d>;/GS;/fp:precise;/Zc:wchar_t;/Zc:forScope;/Zc:inline;/GR;/Gd;/analyze-;/FC;/errorReport:queue"
)
add_library(test_lib SHARED ${SOURCE_DIR}/version.rc ${SOURCE_DIR}/dllmain.cpp)
target_link_options(test_lib PRIVATE
    /ERRORREPORT:QUEUE
    /INCREMENTAL:NO
    /SUBSYSTEM:CONSOLE
    /TLBID:1
    /DYNAMICBASE
    /NXCOMPAT
    /SAFESEH
)
set_target_properties(test_lib PROPERTIES VERSION 1.2.3)

set_source_files_properties(${SOURCE_DIR}/main.cpp PROPERTIES COMPILE_OPTIONS
    "/W3;/WX-;/diagnostics:classic;/Ob2;/Oy-;-DWIN32;-D_WINDOWS;-D_MBCS;/EHsc;/MD$<$<CONFIG:Debug>:d>;/GS;/fp:precise;/Zc:wchar_t;/Zc:forScope;/Zc:inline;/GR;/Gd;/analyze-;/FC;/errorReport:queue"
)
add_executable(test_app ${SOURCE_DIR}/version.rc ${SOURCE_DIR}/main.cpp)
target_link_options(test_app PRIVATE
    /ERRORREPORT:QUEUE
    /INCREMENTAL:NO
    /SUBSYSTEM:CONSOLE
    /TLBID:1
    /DYNAMICBASE
    /NXCOMPAT
    /SAFESEH
)
set_target_properties(test_app PROPERTIES VERSION 1.2.3)
