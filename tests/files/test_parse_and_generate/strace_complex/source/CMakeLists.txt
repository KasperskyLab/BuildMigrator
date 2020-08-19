project(strace_test)

add_library(lib
    STATIC
    lib.c
)

add_executable(main main.cpp)
target_link_libraries(main lib)