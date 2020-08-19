cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)
enable_language(RC)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

set_source_files_properties(${SOURCE_DIR}/sqlite3.rc PROPERTIES COMPILE_OPTIONS /l0x0409)
set_source_files_properties(${SOURCE_DIR}/DllMain.cpp PROPERTIES COMPILE_OPTIONS
    "/W3;/WX-;/diagnostics:classic;/sdl-;/Oi;/Oy-;/GL;-DWIN32;-D_WINDOWS;-D_USRDLL;-DSQLITE_EXPORTS;-DNO_TCL;-DTHREADSAFE=1;-DSQLITE_ENABLE_COLUMN_METADATA;-DSQLITE_ENABLE_UNLOCK_NOTIFY;-DSQLITE_HAS_CODEC;-DSQLITE_ENABLE_DBSTAT_VTAB;-D_WINDLL;-D_MBCS;/EHsc;/MD$<$<CONFIG:Debug>:d>;/GS;/Gy;/fp:precise;/Zc:wchar_t;/Zc:forScope;/Zc:inline;/Gd;/analyze-;/FC;/errorReport:queue;/Zc:threadSafeInit-;/Gw"
)
set_source_files_properties(${SOURCE_DIR}/sqlite3.c PROPERTIES COMPILE_OPTIONS
    "/W3;/WX-;/diagnostics:classic;/sdl-;/Oi;/Oy-;/GL;-DWIN32;-D_WINDOWS;-D_USRDLL;-DSQLITE_EXPORTS;-DNO_TCL;-DTHREADSAFE=1;-DSQLITE_ENABLE_COLUMN_METADATA;-DSQLITE_ENABLE_UNLOCK_NOTIFY;-DSQLITE_HAS_CODEC;-DSQLITE_ENABLE_DBSTAT_VTAB;-D_WINDLL;-D_MBCS;/EHsc;/MD$<$<CONFIG:Debug>:d>;/GS;/Gy;/fp:precise;/Zc:wchar_t;/Zc:forScope;/Zc:inline;/Gd;/analyze-;/FC;/errorReport:queue;/Zc:threadSafeInit-;/Gw"
)
add_library(dblite SHARED
    ${SOURCE_DIR}/sqlite3.rc
    ${SOURCE_DIR}/DllMain.cpp
    ${SOURCE_DIR}/sqlite3.c
)
target_link_options(dblite PRIVATE
    /ERRORREPORT:QUEUE
    /INCREMENTAL:NO
    /DEF:${SOURCE_DIR}/sqlite3.x86.def
    /MANIFEST
    "/MANIFESTUAC:level='asInvoker' uiAccess='false'"
    /manifest:embed
    /SUBSYSTEM:WINDOWS
    /OPT:REF
    /OPT:ICF
    /LTCG:incremental
    /TLBID:1
    /DYNAMICBASE
    /NXCOMPAT
    /SAFESEH
)
target_link_libraries(dblite PRIVATE odbc32 odbccp32)
