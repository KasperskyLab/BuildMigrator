include_guard(GLOBAL)

# Initialize Threads::Threads target
if(UNIX)
    set(CMAKE_THREAD_PREFER_PTHREAD ON)
    set(THREADS_PREFER_PTHREAD_FLAG ON)
    # Strange required variable
    # Bug: https://gitlab.kitware.com/cmake/cmake/issues/16920
    # Fixed in CMake 3.11
    set(THREADS_PTHREAD_ARG "2" CACHE STRING "" FORCE)
endif()
find_package(Threads REQUIRED)

function(language_compile_options LANG)
    set(flags ${ARGN})
    set(visual_studio_langs_with_genex_support C CXX)
    if(LANG STREQUAL "ASM_YASM" OR (CMAKE_GENERATOR MATCHES "Visual Studio" AND NOT LANG IN_LIST visual_studio_langs_with_genex_support))
        # ASM_YASM is not supported natively, it's an internal extension,
        # so generator expressions do not support ASM_YASM.

        # Visual Studio generator doesn't honor COMPILE_LANGUAGE generator expression for languages other than C, CXX

        if (CMAKE_GENERATOR MATCHES "Visual Studio")
            string(GENEX_STRIP "${flags}" flags_no_genex)
            if(NOT flags STREQUAL flags_no_genex)
                message(FATAL_ERROR "Flags contain generator expressions. When using Visual Studio generator, generator expressions are not supported in languages other than ${visual_studio_langs_with_genex_support}.")
            endif()
        endif()
        string(JOIN " " CMAKE_${LANG}_FLAGS ${CMAKE_${LANG}_FLAGS} ${flags})
        set(CMAKE_${LANG}_FLAGS ${CMAKE_${LANG}_FLAGS} PARENT_SCOPE)
    else()
        internal_make_list_genex_compatible(flags)
        add_compile_options($<$<COMPILE_LANGUAGE:${LANG}>:${flags}>)
    endif()
endfunction()

function(target_language_compile_options TARGET LANG VISIBILITY)
    internal_validate_visibility(VISIBILITY)
    set(flags ${ARGN})
    if(LANG STREQUAL "ASM_YASM")
        message(SEND_ERROR "Target scope does not support setting ASM_YASM-specific compile options")
    else()
        internal_make_list_genex_compatible(flags)
        target_compile_options(${TARGET} ${VISIBILITY} $<$<COMPILE_LANGUAGE:${LANG}>:${flags}>)
    endif()
endfunction()

function(language_include_directories LANG)
    set(dirs ${ARGN})
    if(LANG STREQUAL "ASM_YASM")
        message(SEND_ERROR "Directory scope does not support setting ASM_YASM-specific include directories")
    else()
        internal_make_list_genex_compatible(dirs)
        include_directories($<$<COMPILE_LANGUAGE:${LANG}>:${dirs}>)
    endif()
endfunction()

function(target_language_include_directories TARGET LANG VISIBILITY)
    internal_validate_visibility(VISIBILITY)
    set(dirs ${ARGN})
    if(LANG STREQUAL "ASM_YASM")
        message(SEND_ERROR "Target scope does not support setting ASM_YASM-specific include directories")
    else()
        internal_make_list_genex_compatible(dirs)
        target_include_directories(${TARGET} ${VISIBILITY} $<$<COMPILE_LANGUAGE:${LANG}>:${dirs}>)
    endif()
endfunction()

# VISIBILITY argument doesn't do anything, it's for compatibility only.
function(target_static_library_options TARGET VISIBILITY)
    get_target_property(target_type ${TARGET} TYPE)
    if(NOT target_type STREQUAL "STATIC_LIBRARY")
        message(SEND_ERROR "${TARGET} is not a static library")
        return()
    endif()
    internal_validate_visibility(VISIBILITY)
    set(flags ${ARGN})
    set_target_properties(${TARGET} PROPERTIES STATIC_LIBRARY_OPTIONS "${flags}")
endfunction()

function(shared_link_options)
    set(flags ${ARGN})
    internal_make_list_genex_compatible(flags)
    add_link_options($<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${flags}>)
endfunction()

function(executable_link_options)
    set(flags ${ARGN})
    internal_make_list_genex_compatible(flags)
    add_link_options($<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${flags}>)
endfunction()

function(static_library_options)
    set(flags ${ARGN})
    string(JOIN " " CMAKE_STATIC_LINKER_FLAGS ${CMAKE_STATIC_LINKER_FLAGS} ${flags})
    set(CMAKE_STATIC_LINKER_FLAGS ${CMAKE_STATIC_LINKER_FLAGS} PARENT_SCOPE)
endfunction()

function(source_compile_options PATH)
    set(flags ${ARGN})
    set_source_files_properties(${PATH} PROPERTIES COMPILE_OPTIONS "${flags}")
endfunction()

function(source_include_directories PATH)
    set(dirs ${ARGN})
    set_source_files_properties(${PATH} PROPERTIES INCLUDE_DIRECTORIES "${dirs}")
endfunction()

# LANGUAGE [PATH [PATH ...]]
function(set_language LANGUAGE)
    set(files ${ARGN})
    set_source_files_properties(${files} PROPERTIES LANGUAGE ${LANGUAGE})
endfunction()

# Append PATH to TARGET's output directory
# Valid PROPERTY values:
# * ARCHIVE_OUTPUT_DIRECTORY
# * LIBRARY_OUTPUT_DIRECTORY
# * RUNTIME_OUTPUT_DIRECTORY
function(set_target_output_subdir TARGET PROPERTY PATH)
    get_target_property(root ${TARGET} ${PROPERTY})
    if(root)
        set(root ${root}/)
    else()
        set(root)
    endif()
    get_cmake_property(is_multi_config GENERATOR_IS_MULTI_CONFIG)
    if(is_multi_config)
        if(root AND IS_ABSOLUTE "${root}")
            file(RELATIVE_PATH root ${CMAKE_BINARY_DIR} ${root})
        endif()
        set(PATH ${CMAKE_BINARY_DIR}/${CMAKE_CFG_INTDIR}/${root}/${PATH})
        foreach(cfg ${CMAKE_CONFIGURATION_TYPES})
            string(TOUPPER ${cfg} cfg)
            set_target_properties(${TARGET} PROPERTIES ${PROPERTY}_${cfg} ${PATH})
        endforeach()
    else()
        set_target_properties(${TARGET} PROPERTIES ${PROPERTY} ${root}${PATH})
    endif()
endfunction()

# Add Yasm (Yasm Modular Assembler) sources to TARGET.
# 
# Usage:
# 
# target_yasm_sources(<target>
#     <INTERFACE|PUBLIC|PRIVATE> [items1...]
#     [<INTERFACE|PUBLIC|PRIVATE> [items2...] ...])
# 
# IMPORTANT: target_yasm_sources won't receive any target flags that were set after
#            it is called! Call target_compile_options, target_include_dirs, etc
#            before target_yasm_sources.
# 
# Specifies Yasm-compatible sources to use when compiling a given target.
# The named <target> must have been created by a command such as add_executable()
# or add_library() and must not be an ALIAS target.
# 
# The INTERFACE, PUBLIC and PRIVATE keywords are required to specify the scope of
# the following arguments. PRIVATE and PUBLIC items will populate the SOURCES property
# of <target>. PUBLIC and INTERFACE items will populate the INTERFACE_SOURCES property
# of <target>. (IMPORTED targets only support INTERFACE items.) The following arguments
# specify sources. Repeated calls for the same <target> append items in the order called.
# 
# Unlike target_sources, arguments to target_yasm_sources cannot use generator expressions.
# That's because generator expressions do not yet provide $<TARGET_PROPERTY:> equivalent for
# source files.
# 
# Variables that control this function's default behavior:
#  * CMAKE_ASM_YASM_COMPILER: Path to Yasm compiler. Required if Yasm cannot be found in PATH.
#  * CMAKE_ASM_YASM_ARCHITECTURE: -a flag value. Optional.
#  * CMAKE_ASM_YASM_MACHINE: -m flag value. Optional.
#  * CMAKE_ASM_YASM_OBJECT_FORMAT: -f flag value. Optional.
#  * CMAKE_ASM_YASM_FLAGS: global compilation flags. Optional.
# 
# Supported source file, target and directory properties:
#  * COMPILE_DEFINITIONS
#  * INCLUDE_DIRECTORIES
#  * COMPILE_OPTIONS
# 
# Currently only Visual Studio generator for Win32/x64 architecture is tested and supported.
# 
# All Yasm flags: http://www.tortall.net/projects/yasm/manual/html/manual.html#yasm-options
function(target_yasm_sources TARGET)
    # Validate arguments
    set(sources ${ARGN})
    if(NOT sources)
        message(SEND_ERROR "At least one source file must be specified")
        return()
    endif()

    # Validate/set variables
    if(NOT CMAKE_ASM_YASM_COMPILER)
        find_program(CMAKE_ASM_YASM_COMPILER yasm)
        if(NOT CMAKE_ASM_YASM_COMPILER)
            message(SEND_ERROR "Cannot find Yasm compiler anywhere on the system. Please put it into your PATH or specify it in CMAKE_ASM_YASM_COMPILER.")
            return()
        endif()
    endif()

    if(WIN32)
        if(CMAKE_SIZEOF_VOID_P EQUAL 8)
            if(NOT CMAKE_ASM_YASM_OBJECT_FORMAT)
                set(CMAKE_ASM_YASM_OBJECT_FORMAT win64)
            endif()
        else()
            if(NOT CMAKE_ASM_YASM_OBJECT_FORMAT)
                set(CMAKE_ASM_YASM_OBJECT_FORMAT win32)
            endif()
        endif()
    else()
        message(SEND_ERROR "Only Windows is currently supported.")
        return()
    endif()

    # Setup common flags
    set(flag_objformat -f ${CMAKE_ASM_YASM_OBJECT_FORMAT})
    set(flag_arch)
    if(CMAKE_ASM_YASM_ARCHITECTURE)
        set(flag_arch -a ${CMAKE_ASM_YASM_ARCHITECTURE})
    endif()
    set(flag_machine)
    if(CMAKE_ASM_YASM_MACHINE)
        set(flag_machine -m ${CMAKE_ASM_YASM_MACHINE})
    endif()

    # Transforms "a;b;c" into "-Da;-Db;-Dc"
    macro(format_definition_flags FLAGS)
        if(${FLAGS})
            set(${FLAGS} "$<$<BOOL:${${FLAGS}}>:-D$<JOIN:${${FLAGS}},;-D>>")
        endif()
    endmacro()
    # Transforms "a;b;c" into "-Ia;-Ib;-Ic"
    macro(format_include_dir_flags FLAGS)
        if(${FLAGS})
            set(${FLAGS} "$<$<BOOL:${${FLAGS}}>:-I$<JOIN:${${FLAGS}},;-I>>")
        endif()
    endmacro()

    get_target_property(target_compile_defs ${TARGET} COMPILE_DEFINITIONS)
    if(NOT target_compile_defs)
        set(target_compile_defs)
    endif()
    get_target_property(target_include_dirs ${TARGET} INCLUDE_DIRECTORIES)
    if(NOT target_include_dirs)
        set(target_include_dirs)
    endif()
    get_target_property(target_compile_opts ${TARGET} COMPILE_OPTIONS)
    if(NOT target_compile_opts)
        set(target_compile_opts)
    endif()

    format_definition_flags(directory_compile_defs)
    format_definition_flags(target_compile_defs)
    format_include_dir_flags(directory_include_dirs)
    format_include_dir_flags(target_include_dirs)

    # Create custom compilations command for each source file
    # Append resulting objects files to TARGET
    set(scope)
    set(scope_enum INTERFACE PUBLIC PRIVATE)
    foreach(arg ${sources})
        if(arg IN_LIST scope_enum)
            set(scope ${arg})
            continue()
        else()
            set(srcfile ${arg})
        endif()
        if(NOT IS_ABSOLUTE "${srcfile}")
            set(srcfile ${CMAKE_CURRENT_SOURCE_DIR}/${srcfile})
        endif()

        internal_get_unique_object_path(${TARGET} ${srcfile} objfile)

        get_source_file_property(source_compile_defs ${srcfile} COMPILE_DEFINITIONS)
        if(NOT source_compile_defs)
            set(source_compile_defs)
        endif()
        get_source_file_property(source_include_dirs ${srcfile} INCLUDE_DIRECTORIES)
        if(NOT source_include_dirs)
            set(source_include_dirs)
        endif()

        format_definition_flags(source_compile_defs)
        format_include_dir_flags(source_include_dirs)

        get_source_file_property(source_compile_opts ${srcfile} COMPILE_OPTIONS)
        if(source_compile_opts STREQUAL "NOTFOUND")
            set(source_compile_opts)
        endif()

        if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
            separate_arguments(global_flags WINDOWS_COMMAND ${CMAKE_ASM_YASM_FLAGS})
        else()
            separate_arguments(global_flags UNIX_COMMAND ${CMAKE_ASM_YASM_FLAGS})
        endif()
        set(command ${CMAKE_ASM_YASM_COMPILER}
                ${flag_objformat}
                ${flag_arch}
                ${flag_machine}
                ${global_flags}
                ${target_include_dirs}
                ${source_include_dirs}
                ${target_compile_defs}
                ${source_compile_defs}
                ${target_compile_opts}
                ${source_compile_opts}
                ${srcfile}
                -o ${objfile}
        )
        # $<COMPILE_LANGUAGE:XXX> generator expression is not supported in commands.
        # Disable conditionals containing COMPILE_LANGUAGE
        string(REGEX REPLACE [[\$<\$<COMPILE_LANGUAGE:[0-9a-zA-Z_-]+>:]] "$<0:" command "${command}")
        string(REGEX REPLACE [[\$<IF\$<COMPILE_LANGUAGE:[0-9a-zA-Z_-]+>,]] "$<IF:0," command "${command}")
        add_custom_command(OUTPUT ${objfile}
            COMMAND ${CMAKE_COMMAND} -E echo "${command}" # pretty-print command before running
            COMMAND "${command}"
            DEPENDS "${srcfile}"
            COMMAND_EXPAND_LISTS
            VERBATIM
        )
        set_source_files_properties(${objfile} PROPERTIES EXTERNAL_OBJECT ON)
        target_sources(${TARGET} ${scope} ${objfile})
    endforeach()
endfunction()

# Get unique object file path for target.
# Algorithm is similar to what CMake does internally.
# 1. target_name=t, source=s.cpp => <t's binary dir>/t.dir/s.cpp.obj
# 2. target_name=t, source=1/s.cpp => <t's binary dir>/t.dir/1/s.cpp.obj
# 3. target_name=t, source=../s.cpp => <t's binary dir>/t.dir/<full path to s.cpp>/s.cpp.obj
# 4. multi-config generators: <target binary dir>/<target name>.dir/<config>/<source>.obj
function(internal_get_unique_object_path TARGET SOURCE OUT_VAR)
    if(WIN32)
        set(object_ext .obj)
    else()
        set(object_ext .o)
    endif()
    get_target_property(target_source_dir ${TARGET} SOURCE_DIR)
    file(RELATIVE_PATH source_rel ${target_source_dir} ${SOURCE})
    if(source_rel MATCHES "^(\\.\\.|[a-zA-Z]:|/)")
        # Source file is not under target_source_dir, we'll have to replicate its full path under ${TARGET}.dir/
        get_filename_component(source_rel ${SOURCE} ABSOLUTE)
        # remove drive letter etc
        string(REGEX REPLACE "^file:" "" source_rel ${source_rel})
        string(REGEX REPLACE "^[/\\]+" "" source_rel ${source_rel})
        string(REGEX REPLACE "^([a-zA-Z]:[/\\])" "" source_rel ${source_rel})
    endif()
    get_target_property(target_binary_dir ${TARGET} BINARY_DIR)
    set(config_subdir)
    if(CMAKE_CFG_INTDIR AND NOT CMAKE_CFG_INTDIR STREQUAL ".")
        set(config_subdir /${CMAKE_CFG_INTDIR})
    endif()
    set(${OUT_VAR} ${target_binary_dir}/${TARGET}.dir${config_subdir}/${source_rel}${object_ext} PARENT_SCOPE)
endfunction()

function(internal_make_list_genex_compatible VAR)
    string(JOIN $<SEMICOLON> joined_var ${${VAR}})
    set(${VAR} "${joined_var}" PARENT_SCOPE)
endfunction()

macro(internal_validate_visibility VAR)
    set(__valid_visibility INTERFACE PUBLIC PRIVATE)
    if(NOT ${VAR} IN_LIST __valid_visibility)
        message(SEND_ERROR "${VAR} must be one of supported values: ${__valid_visibility}")
    endif()
endmacro()
