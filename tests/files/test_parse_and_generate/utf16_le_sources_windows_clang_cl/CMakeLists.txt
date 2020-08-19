cmake_minimum_required(VERSION 3.8)

project(PROJECT C)
enable_language(RC)

include(cmake_framework)
include(compiler_config)
include(system)
fix_asm_flags()
find_thread_library()

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
set(COMPILE_FLAGS "" CACHE STRING "")
set(LINK_FLAGS "" CACHE STRING "")
set(INCLUDE_DIRS ${CMAKE_CURRENT_BINARY_DIR}/include CACHE STRING "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/include)
configure_file(${CMAKE_CURRENT_LIST_DIR}/test.cur ${CMAKE_CURRENT_BINARY_DIR}/test.cur COPYONLY)
configure_file(${CMAKE_CURRENT_LIST_DIR}/include/foo.h ${CMAKE_CURRENT_BINARY_DIR}/include/foo.h COPYONLY)

add_executable(app ${SOURCE_DIR}/resources.rc ${SOURCE_DIR}/main.c)
set_target_properties(app PROPERTIES LINK_FLAGS "${LINK_FLAGS}")
target_compile_options(app PRIVATE ${COMPILE_FLAGS})
target_include_directories(app PRIVATE ${INCLUDE_DIRS})
