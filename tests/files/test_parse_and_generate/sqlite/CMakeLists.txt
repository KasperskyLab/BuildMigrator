cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
add_compile_options(
    -DPACKAGE_NAME="sqlite"
    -DPACKAGE_TARNAME="sqlite"
    -DPACKAGE_VERSION="3.31.1"
    "-DPACKAGE_STRING=\"sqlite 3.31.1\""
    -DPACKAGE_BUGREPORT="http://www.sqlite.org"
    -DPACKAGE_URL=""
    -DPACKAGE="sqlite"
    -DVERSION="3.31.1"
    -DLT_OBJDIR=".libs/"
    -DHAVE_DECL_STRERROR_R=0
    -D_REENTRANT=1
    -DSQLITE_THREADSAFE=1
    -DSQLITE_ENABLE_FTS4
    -DSQLITE_ENABLE_FTS5
    -DSQLITE_ENABLE_JSON1
    -DSQLITE_ENABLE_RTREE
    -DSQLITE_ENABLE_GEOPOLY
    -DSQLITE_ENABLE_COLUMN_METADATA
    -DSQLITE_ENABLE_MEMSYS3
    -DSQLITE_ENABLE_UNLOCK_NOTIFY
    -std=gnu99
    -fPIC
    -pthread
    -D__AURORA__
    -B/opt/aurora/tooling/opt/cross/bin/armv7hl-meego-linux-gnueabi-
)
include_directories(${CMAKE_CURRENT_BINARY_DIR} ${SOURCE_DIR})
add_link_options(-pthread)
link_libraries(${CMAKE_DL_LIBS} m)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/.libs)

add_library(sqlite3.0.8.6 SHARED ${SOURCE_DIR}/sqlite3.c)
set_target_properties(sqlite3.0.8.6 PROPERTIES OUTPUT_NAME sqlite3)
set_target_output_subdir(sqlite3.0.8.6 LIBRARY_OUTPUT_DIRECTORY .libs)
set_target_output_subdir(sqlite3.0.8.6 RUNTIME_OUTPUT_DIRECTORY .libs)
set_target_properties(sqlite3.0.8.6 PROPERTIES VERSION 0.8.6)
set_target_properties(sqlite3.0.8.6 PROPERTIES SOVERSION 0)

add_library(libsqlite3_so ALIAS sqlite3.0.8.6)

add_executable(sqlite3 ${SOURCE_DIR}/shell.c ${SOURCE_DIR}/sqlite3.c)
target_compile_options(sqlite3 PRIVATE
    -DSQLITE_ENABLE_EXPLAIN_COMMENTS
    -DSQLITE_ENABLE_DBPAGE_VTAB
    -DSQLITE_ENABLE_STMTVTAB
    -DSQLITE_ENABLE_DBSTAT_VTAB
    -DSQLITE_NOHAVE_SYSTEM
)

add_library(sqlite3.static STATIC ${SOURCE_DIR}/sqlite3.c)
set_target_properties(sqlite3.static PROPERTIES OUTPUT_NAME sqlite3)
set_target_output_subdir(sqlite3.static ARCHIVE_OUTPUT_DIRECTORY .libs)
