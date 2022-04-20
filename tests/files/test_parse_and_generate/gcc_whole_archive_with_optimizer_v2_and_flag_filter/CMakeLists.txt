cmake_minimum_required(VERSION 3.13)

project(PROJECT C)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")

add_library(common.static STATIC ${SOURCE_DIR}/common.c)
target_compile_options(common.static PRIVATE -DCOMMON=1)
set_target_properties(common.static PROPERTIES OUTPUT_NAME common)

add_library(test SHARED ${SOURCE_DIR}/a.c ${SOURCE_DIR}/b.c)
target_link_options(test PRIVATE -g)
target_link_libraries(test PRIVATE
    -Wl,-whole-archive
    common.static
    ${CMAKE_DL_LIBS}
    -Wl,-no-whole-archive
)
target_compile_options(test PRIVATE -DTEST=1)
set_target_properties(test PROPERTIES VERSION 3.0.0)
set_target_properties(test PROPERTIES SOVERSION 3)
