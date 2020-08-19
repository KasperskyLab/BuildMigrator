cmake_minimum_required(VERSION 3.13)

project(PROJECT C CXX)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}" CACHE PATH "")
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/IncludeDIR2)

set_source_files_properties(${SOURCE_DIR}/Bar.CPP PROPERTIES INCLUDE_DIRECTORIES ${CMAKE_CURRENT_BINARY_DIR}/IncludeDIR2)
add_executable(application ${SOURCE_DIR}/Bar.CPP)
set_target_properties(application PROPERTIES OUTPUT_NAME ApplicatioN)

add_library(my_library SHARED ${SOURCE_DIR}/DoesNotExist.C ${SOURCE_DIR}/Bar.CPP)
set_target_properties(my_library PROPERTIES OUTPUT_NAME My_Library)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/IncludeDir1)

set_source_files_properties(${SOURCE_DIR}/SubDir/foo.cpp PROPERTIES INCLUDE_DIRECTORIES ${CMAKE_CURRENT_BINARY_DIR}/IncludeDir1)
add_library(test1.static STATIC ${SOURCE_DIR}/SubDir/foo.cpp)
target_link_libraries(test1.static PRIVATE my_library)
set_target_properties(test1.static PROPERTIES OUTPUT_NAME LIBTEST1)

add_library(test2.static STATIC ${SOURCE_DIR}/SubDir/foo.cpp)
target_link_libraries(test2.static PRIVATE my_library)
set_target_properties(test2.static PROPERTIES OUTPUT_NAME LIBTEST2)
configure_file(${CMAKE_CURRENT_LIST_DIR}/prebuilt/FILES/SomeFile.txt ${CMAKE_CURRENT_BINARY_DIR}/FILES/SomeFile.txt COPYONLY)
