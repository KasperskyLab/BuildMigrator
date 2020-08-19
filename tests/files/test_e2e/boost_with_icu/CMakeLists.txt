cmake_minimum_required(VERSION 3.15)

project(boost_with_icu)

add_subdirectory(icu)
set(ICU_INCLUDE_DIRS
    ${CMAKE_CURRENT_LIST_DIR}/icu/source/common
    ${CMAKE_CURRENT_LIST_DIR}/icu/source/i18n
    ${CMAKE_CURRENT_LIST_DIR}/icu/source/io
    CACHE STRING ""
)
add_subdirectory(boost)
