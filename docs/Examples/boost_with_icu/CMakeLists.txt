cmake_minimum_required(VERSION 3.13)

project(boost C CXX)
enable_language(ASM)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(extensions)

set(BOOST_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}/source" CACHE PATH "")
set(compile_flags_1
    -DBOOST_LOG_USE_AVX2
    -DBOOST_LOG_USE_SSSE3
    -DBOOST_LOG_WITHOUT_DEBUG_OUTPUT
)
set(compile_flags_2
    -DBOOST_ATOMIC_STATIC_LINK=1
    -DBOOST_CHRONO_STATIC_LINK=1
    -DBOOST_FILESYSTEM_STATIC_LINK=1
    -DBOOST_HAS_ICU=1
    -DBOOST_LOG_HAS_PTHREAD_MUTEX_ROBUST
    -DBOOST_LOG_USE_NATIVE_SYSLOG
    -DBOOST_LOG_WITHOUT_EVENT_LOG
    -DBOOST_SPIRIT_USE_PHOENIX_V3=1
    -DBOOST_THREAD_BUILD_LIB=1
    -DBOOST_THREAD_DONT_USE_CHRONO=1
    -DBOOST_THREAD_POSIX
    -DBOOST_THREAD_USE_LIB=1
    -DDATE_TIME_INLINE
    -D_XOPEN_SOURCE=600
    -D__STDC_CONSTANT_MACROS
    -Wall
    -fno-strict-aliasing
    -ftemplate-depth-1024
)
set(compile_flags_3 -DBOOST_THREAD_BUILD_LIB=1 -DBOOST_THREAD_POSIX -Wall)
set(ICU_INCLUDE_DIRS "" CACHE STRING "")
set(include_dirs_1 ${ICU_INCLUDE_DIRS} ${BOOST_SOURCE_DIR}/libs/log/src)
add_compile_options(
    -pthread
    -finline-functions
    -Wno-inline
    -fvisibility=hidden
    -DBOOST_ALL_NO_LIB=1
)
include_directories(${BOOST_SOURCE_DIR})
language_compile_options(CXX -fvisibility-inlines-hidden)
language_compile_options(ASM
    -x
    assembler-with-cpp
    -Wall
    -DBOOST_CONTEXT_SOURCE
    -DBOOST_DISABLE_ASSERTS
)

add_library(boost_atomic.static STATIC ${BOOST_SOURCE_DIR}/libs/atomic/src/lock_pool.cpp)
target_compile_options(boost_atomic.static PRIVATE -Wall -DBOOST_ATOMIC_SOURCE -DBOOST_ATOMIC_STATIC_LINK=1)
set_target_properties(boost_atomic.static PROPERTIES OUTPUT_NAME boost_atomic)

add_library(boost_chrono.static STATIC
    ${BOOST_SOURCE_DIR}/libs/chrono/src/chrono.cpp
    ${BOOST_SOURCE_DIR}/libs/chrono/src/thread_clock.cpp
    ${BOOST_SOURCE_DIR}/libs/chrono/src/process_cpu_clocks.cpp
)
target_compile_options(boost_chrono.static PRIVATE -Wall -Wextra -Wno-long-long -DBOOST_All_STATIC_LINK=1)
set_target_properties(boost_chrono.static PROPERTIES OUTPUT_NAME boost_chrono)

add_library(boost_container.static STATIC
    ${BOOST_SOURCE_DIR}/libs/container/src/alloc_lib.c
    ${BOOST_SOURCE_DIR}/libs/container/src/dlmalloc.cpp
    ${BOOST_SOURCE_DIR}/libs/container/src/global_resource.cpp
    ${BOOST_SOURCE_DIR}/libs/container/src/monotonic_buffer_resource.cpp
    ${BOOST_SOURCE_DIR}/libs/container/src/pool_resource.cpp
    ${BOOST_SOURCE_DIR}/libs/container/src/synchronized_pool_resource.cpp
    ${BOOST_SOURCE_DIR}/libs/container/src/unsynchronized_pool_resource.cpp
)
target_compile_options(boost_container.static PRIVATE -Wall -DBOOST_CONTAINER_STATIC_LINK=1)
set_target_properties(boost_container.static PROPERTIES OUTPUT_NAME boost_container)

add_library(boost_context.static STATIC
    ${BOOST_SOURCE_DIR}/libs/context/src/asm/make_x86_64_sysv_elf_gas.S
    ${BOOST_SOURCE_DIR}/libs/context/src/asm/jump_x86_64_sysv_elf_gas.S
    ${BOOST_SOURCE_DIR}/libs/context/src/asm/ontop_x86_64_sysv_elf_gas.S
    ${BOOST_SOURCE_DIR}/libs/context/src/posix/stack_traits.cpp
)
target_language_compile_options(boost_context.static CXX PRIVATE -Wall -DBOOST_CONTEXT_SOURCE -DBOOST_DISABLE_ASSERTS)
set_target_properties(boost_context.static PROPERTIES OUTPUT_NAME boost_context)

add_library(boost_contract.static STATIC ${BOOST_SOURCE_DIR}/libs/contract/src/contract.cpp)
target_compile_options(boost_contract.static PRIVATE -Wall -DBOOST_CONTRACT_STATIC_LINK)
set_target_properties(boost_contract.static PROPERTIES OUTPUT_NAME boost_contract)

add_library(boost_coroutine.static STATIC
    ${BOOST_SOURCE_DIR}/libs/coroutine/src/detail/coroutine_context.cpp
    ${BOOST_SOURCE_DIR}/libs/coroutine/src/exceptions.cpp
    ${BOOST_SOURCE_DIR}/libs/coroutine/src/posix/stack_traits.cpp
)
target_compile_options(boost_coroutine.static PRIVATE
    ${compile_flags_3}
    -DBOOST_CHRONO_STATIC_LINK=1
    -DBOOST_COROUTINES_SOURCE
    -DBOOST_DISABLE_ASSERTS
    -DBOOST_THREAD_USE_LIB=1
)
set_target_properties(boost_coroutine.static PROPERTIES OUTPUT_NAME boost_coroutine)

add_library(boost_date_time.static STATIC
    ${BOOST_SOURCE_DIR}/libs/date_time/src/gregorian/greg_month.cpp
)
target_compile_options(boost_date_time.static PRIVATE -Wall -DDATE_TIME_INLINE)
set_target_properties(boost_date_time.static PROPERTIES OUTPUT_NAME boost_date_time)

add_library(boost_exception.static STATIC
    ${BOOST_SOURCE_DIR}/libs/exception/src/clone_current_exception_non_intrusive.cpp
)
target_compile_options(boost_exception.static PRIVATE -Wall)
set_target_properties(boost_exception.static PROPERTIES OUTPUT_NAME boost_exception)

add_library(boost_fiber.static STATIC
    ${BOOST_SOURCE_DIR}/libs/fiber/src/algo/algorithm.cpp
    ${BOOST_SOURCE_DIR}/libs/fiber/src/algo/round_robin.cpp
    ${BOOST_SOURCE_DIR}/libs/fiber/src/algo/shared_work.cpp
    ${BOOST_SOURCE_DIR}/libs/fiber/src/algo/work_stealing.cpp
    ${BOOST_SOURCE_DIR}/libs/fiber/src/barrier.cpp
    ${BOOST_SOURCE_DIR}/libs/fiber/src/condition_variable.cpp
    ${BOOST_SOURCE_DIR}/libs/fiber/src/context.cpp
    ${BOOST_SOURCE_DIR}/libs/fiber/src/fiber.cpp
    ${BOOST_SOURCE_DIR}/libs/fiber/src/future.cpp
    ${BOOST_SOURCE_DIR}/libs/fiber/src/mutex.cpp
    ${BOOST_SOURCE_DIR}/libs/fiber/src/properties.cpp
    ${BOOST_SOURCE_DIR}/libs/fiber/src/recursive_mutex.cpp
    ${BOOST_SOURCE_DIR}/libs/fiber/src/recursive_timed_mutex.cpp
    ${BOOST_SOURCE_DIR}/libs/fiber/src/timed_mutex.cpp
    ${BOOST_SOURCE_DIR}/libs/fiber/src/scheduler.cpp
)
target_compile_options(boost_fiber.static PRIVATE
    -Wall
    -DBOOST_DISABLE_ASSERTS
    -DBOOST_FIBERS_SOURCE
    -DBOOST_FILESYSTEM_STATIC_LINK=1
)
set_target_properties(boost_fiber.static PROPERTIES OUTPUT_NAME boost_fiber)

add_library(boost_filesystem.static STATIC
    ${BOOST_SOURCE_DIR}/libs/filesystem/src/codecvt_error_category.cpp
    ${BOOST_SOURCE_DIR}/libs/filesystem/src/exception.cpp
    ${BOOST_SOURCE_DIR}/libs/filesystem/src/directory.cpp
    ${BOOST_SOURCE_DIR}/libs/filesystem/src/operations.cpp
    ${BOOST_SOURCE_DIR}/libs/filesystem/src/path.cpp
    ${BOOST_SOURCE_DIR}/libs/filesystem/src/path_traits.cpp
    ${BOOST_SOURCE_DIR}/libs/filesystem/src/portability.cpp
    ${BOOST_SOURCE_DIR}/libs/filesystem/src/unique_path.cpp
    ${BOOST_SOURCE_DIR}/libs/filesystem/src/utf8_codecvt_facet.cpp
    ${BOOST_SOURCE_DIR}/libs/filesystem/src/windows_file_codecvt.cpp
)
target_compile_options(boost_filesystem.static PRIVATE
    -Wall
    -DBOOST_FILESYSTEM_SOURCE
    -DBOOST_FILESYSTEM_STATIC_LINK=1
)
set_target_properties(boost_filesystem.static PROPERTIES OUTPUT_NAME boost_filesystem)

add_library(boost_graph.static STATIC
    ${BOOST_SOURCE_DIR}/libs/graph/src/read_graphviz_new.cpp
    ${BOOST_SOURCE_DIR}/libs/graph/src/graphml.cpp
)
target_compile_options(boost_graph.static PRIVATE -Wall -DBOOST_HAS_ICU=1)
target_include_directories(boost_graph.static PRIVATE ${ICU_INCLUDE_DIRS} ${BOOST_SOURCE_DIR}/libs/graph/src)
set_target_properties(boost_graph.static PROPERTIES OUTPUT_NAME boost_graph)

add_library(boost_iostreams.static STATIC
    ${BOOST_SOURCE_DIR}/libs/iostreams/src/file_descriptor.cpp
    ${BOOST_SOURCE_DIR}/libs/iostreams/src/mapped_file.cpp
)
target_compile_options(boost_iostreams.static PRIVATE
    -Wall
    -DBOOST_IOSTREAMS_LZMA_NO_MULTITHREADED=1
    -DBOOST_IOSTREAMS_USE_DEPRECATED
)
set_target_properties(boost_iostreams.static PROPERTIES OUTPUT_NAME boost_iostreams)

include(BOOST_LOCALE_STATIC_SRC.cmake)
add_library(boost_locale.static STATIC ${BOOST_LOCALE_STATIC_SRC})
target_compile_options(boost_locale.static PRIVATE
    ${compile_flags_3}
    -DBOOST_CHRONO_STATIC_LINK=1
    -DBOOST_LOCALE_NO_WINAPI_BACKEND=1
    -DBOOST_LOCALE_WITH_ICONV=1
    -DBOOST_LOCALE_WITH_ICU=1
    -DBOOST_SYSTEM_STATIC_LINK=1
    -DBOOST_THREAD_NO_LIB=1
    -DBOOST_THREAD_USE_LIB=1
)
target_include_directories(boost_locale.static PRIVATE ${ICU_INCLUDE_DIRS})
set_target_properties(boost_locale.static PROPERTIES OUTPUT_NAME boost_locale)

set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/attribute_name.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/attribute_set.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/attribute_value_set.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/code_conversion.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/core.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/record_ostream.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/severity_level.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/global_logger_storage.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/named_scope.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/process_name.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/process_id.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/thread_id.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/timer.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/exceptions.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/default_attribute_names.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/default_sink.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/text_ostream_backend.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/text_file_backend.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/text_multifile_backend.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/thread_specific.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/once_block.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/timestamp.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/threadsafe_queue.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/event.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/trivial.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/spirit_encoding.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/format_parser.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/date_time_format_parser.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/named_scope_format_parser.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/permissions.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/dump.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/dump_avx2.cpp PROPERTIES COMPILE_OPTIONS "-mavx;-mavx2;-fabi-version=0")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/dump_ssse3.cpp PROPERTIES COMPILE_OPTIONS "-msse;-msse2;-msse3;-mssse3")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/posix/ipc_reliable_message_queue.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/posix/object_name.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/log/src/syslog_backend.cpp PROPERTIES COMPILE_OPTIONS "${compile_flags_1}")
include(BOOST_LOG_STATIC_SRC.cmake)
add_library(boost_log.static STATIC ${BOOST_LOG_STATIC_SRC})
target_compile_options(boost_log.static PRIVATE ${compile_flags_2} -DBOOST_LOG_BUILDING_THE_LIB=1)
target_include_directories(boost_log.static PRIVATE ${include_dirs_1})
set_target_properties(boost_log.static PROPERTIES OUTPUT_NAME boost_log)

add_library(boost_log_setup.static STATIC
    ${BOOST_SOURCE_DIR}/libs/log/src/setup/parser_utils.cpp
    ${BOOST_SOURCE_DIR}/libs/log/src/setup/init_from_stream.cpp
    ${BOOST_SOURCE_DIR}/libs/log/src/setup/init_from_settings.cpp
    ${BOOST_SOURCE_DIR}/libs/log/src/setup/settings_parser.cpp
    ${BOOST_SOURCE_DIR}/libs/log/src/setup/filter_parser.cpp
    ${BOOST_SOURCE_DIR}/libs/log/src/setup/formatter_parser.cpp
    ${BOOST_SOURCE_DIR}/libs/log/src/setup/default_filter_factory.cpp
    ${BOOST_SOURCE_DIR}/libs/log/src/setup/matches_relation_factory.cpp
    ${BOOST_SOURCE_DIR}/libs/log/src/setup/default_formatter_factory.cpp
)
target_compile_options(boost_log_setup.static PRIVATE
    ${compile_flags_2}
    -DBOOST_LOG_SETUP_BUILDING_THE_LIB=1
    -DBOOST_LOG_USE_AVX2
    -DBOOST_LOG_USE_SSSE3
)
target_include_directories(boost_log_setup.static PRIVATE ${include_dirs_1})
set_target_properties(boost_log_setup.static PROPERTIES OUTPUT_NAME boost_log_setup)

add_library(boost_nowide.static STATIC
    ${BOOST_SOURCE_DIR}/libs/nowide/src/cstdio.cpp
    ${BOOST_SOURCE_DIR}/libs/nowide/src/cstdlib.cpp
    ${BOOST_SOURCE_DIR}/libs/nowide/src/iostream.cpp
)
target_compile_options(boost_nowide.static PRIVATE -Wall)
set_target_properties(boost_nowide.static PROPERTIES OUTPUT_NAME boost_nowide)

add_library(boost_program_options.static STATIC
    ${BOOST_SOURCE_DIR}/libs/program_options/src/cmdline.cpp
    ${BOOST_SOURCE_DIR}/libs/program_options/src/config_file.cpp
    ${BOOST_SOURCE_DIR}/libs/program_options/src/options_description.cpp
    ${BOOST_SOURCE_DIR}/libs/program_options/src/parsers.cpp
    ${BOOST_SOURCE_DIR}/libs/program_options/src/variables_map.cpp
    ${BOOST_SOURCE_DIR}/libs/program_options/src/value_semantic.cpp
    ${BOOST_SOURCE_DIR}/libs/program_options/src/positional_options.cpp
    ${BOOST_SOURCE_DIR}/libs/program_options/src/utf8_codecvt_facet.cpp
    ${BOOST_SOURCE_DIR}/libs/program_options/src/convert.cpp
    ${BOOST_SOURCE_DIR}/libs/program_options/src/winmain.cpp
    ${BOOST_SOURCE_DIR}/libs/program_options/src/split.cpp
)
target_compile_options(boost_program_options.static PRIVATE -Wall)
set_target_properties(boost_program_options.static PROPERTIES OUTPUT_NAME boost_program_options)

add_library(boost_random.static STATIC ${BOOST_SOURCE_DIR}/libs/random/src/random_device.cpp)
target_compile_options(boost_random.static PRIVATE -Wall -DBOOST_SYSTEM_STATIC_LINK=1)
set_target_properties(boost_random.static PROPERTIES OUTPUT_NAME boost_random)

add_library(boost_regex.static STATIC
    ${BOOST_SOURCE_DIR}/libs/regex/src/c_regex_traits.cpp
    ${BOOST_SOURCE_DIR}/libs/regex/src/cpp_regex_traits.cpp
    ${BOOST_SOURCE_DIR}/libs/regex/src/cregex.cpp
    ${BOOST_SOURCE_DIR}/libs/regex/src/fileiter.cpp
    ${BOOST_SOURCE_DIR}/libs/regex/src/icu.cpp
    ${BOOST_SOURCE_DIR}/libs/regex/src/instances.cpp
    ${BOOST_SOURCE_DIR}/libs/regex/src/posix_api.cpp
    ${BOOST_SOURCE_DIR}/libs/regex/src/regex.cpp
    ${BOOST_SOURCE_DIR}/libs/regex/src/regex_debug.cpp
    ${BOOST_SOURCE_DIR}/libs/regex/src/regex_raw_buffer.cpp
    ${BOOST_SOURCE_DIR}/libs/regex/src/regex_traits_defaults.cpp
    ${BOOST_SOURCE_DIR}/libs/regex/src/static_mutex.cpp
    ${BOOST_SOURCE_DIR}/libs/regex/src/w32_regex_traits.cpp
    ${BOOST_SOURCE_DIR}/libs/regex/src/wc_regex_traits.cpp
    ${BOOST_SOURCE_DIR}/libs/regex/src/wide_posix_api.cpp
    ${BOOST_SOURCE_DIR}/libs/regex/src/winstances.cpp
    ${BOOST_SOURCE_DIR}/libs/regex/src/usinstances.cpp
)
target_compile_options(boost_regex.static PRIVATE -Wall -DBOOST_HAS_ICU=1)
target_include_directories(boost_regex.static PRIVATE ${ICU_INCLUDE_DIRS})
set_target_properties(boost_regex.static PROPERTIES OUTPUT_NAME boost_regex)

include(BOOST_SERIALIZATION_STATIC_SRC.cmake)
add_library(boost_serialization.static STATIC ${BOOST_SERIALIZATION_STATIC_SRC})
target_compile_options(boost_serialization.static PRIVATE -Wall -ftemplate-depth-255)
set_target_properties(boost_serialization.static PROPERTIES OUTPUT_NAME boost_serialization)

add_library(boost_wserialization.static STATIC
    ${BOOST_SOURCE_DIR}/libs/serialization/src/basic_text_wiprimitive.cpp
    ${BOOST_SOURCE_DIR}/libs/serialization/src/basic_text_woprimitive.cpp
    ${BOOST_SOURCE_DIR}/libs/serialization/src/text_wiarchive.cpp
    ${BOOST_SOURCE_DIR}/libs/serialization/src/text_woarchive.cpp
    ${BOOST_SOURCE_DIR}/libs/serialization/src/polymorphic_text_wiarchive.cpp
    ${BOOST_SOURCE_DIR}/libs/serialization/src/polymorphic_text_woarchive.cpp
    ${BOOST_SOURCE_DIR}/libs/serialization/src/xml_wgrammar.cpp
    ${BOOST_SOURCE_DIR}/libs/serialization/src/xml_wiarchive.cpp
    ${BOOST_SOURCE_DIR}/libs/serialization/src/xml_woarchive.cpp
    ${BOOST_SOURCE_DIR}/libs/serialization/src/polymorphic_xml_wiarchive.cpp
    ${BOOST_SOURCE_DIR}/libs/serialization/src/polymorphic_xml_woarchive.cpp
)
target_compile_options(boost_wserialization.static PRIVATE -Wall -ftemplate-depth-255)
set_target_properties(boost_wserialization.static PROPERTIES OUTPUT_NAME boost_wserialization)

add_library(boost_stacktrace_addr2line.static STATIC ${BOOST_SOURCE_DIR}/libs/stacktrace/src/addr2line.cpp)
target_compile_options(boost_stacktrace_addr2line.static PRIVATE -Wall)
set_target_properties(boost_stacktrace_addr2line.static PROPERTIES OUTPUT_NAME boost_stacktrace_addr2line)

add_library(boost_stacktrace_backtrace.static STATIC ${BOOST_SOURCE_DIR}/libs/stacktrace/src/backtrace.cpp)
target_compile_options(boost_stacktrace_backtrace.static PRIVATE -Wall)
set_target_properties(boost_stacktrace_backtrace.static PROPERTIES OUTPUT_NAME boost_stacktrace_backtrace)

add_library(boost_stacktrace_basic.static STATIC ${BOOST_SOURCE_DIR}/libs/stacktrace/src/basic.cpp)
target_compile_options(boost_stacktrace_basic.static PRIVATE -Wall)
set_target_properties(boost_stacktrace_basic.static PROPERTIES OUTPUT_NAME boost_stacktrace_basic)

add_library(boost_stacktrace_noop.static STATIC ${BOOST_SOURCE_DIR}/libs/stacktrace/src/noop.cpp)
target_compile_options(boost_stacktrace_noop.static PRIVATE -Wall)
set_target_properties(boost_stacktrace_noop.static PROPERTIES OUTPUT_NAME boost_stacktrace_noop)

add_library(boost_system.static STATIC ${BOOST_SOURCE_DIR}/libs/system/src/error_code.cpp)
target_compile_options(boost_system.static PRIVATE -Wall -DBOOST_SYSTEM_STATIC_LINK=1)
set_target_properties(boost_system.static PROPERTIES OUTPUT_NAME boost_system)

add_library(boost_prg_exec_monitor.static STATIC
    ${BOOST_SOURCE_DIR}/libs/test/src/execution_monitor.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/debug.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/cpp_main.cpp
)
target_compile_options(boost_prg_exec_monitor.static PRIVATE -Wall -Wno-variadic-macros)
set_target_properties(boost_prg_exec_monitor.static PROPERTIES OUTPUT_NAME boost_prg_exec_monitor)

add_library(boost_test_exec_monitor.static STATIC
    ${BOOST_SOURCE_DIR}/libs/test/src/compiler_log_formatter.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/debug.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/decorator.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/execution_monitor.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/framework.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/plain_report_formatter.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/progress_monitor.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/results_collector.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/results_reporter.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/test_framework_init_observer.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/test_main.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/test_tools.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/test_tree.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/unit_test_log.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/unit_test_main.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/unit_test_monitor.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/unit_test_parameters.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/junit_log_formatter.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/xml_log_formatter.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/xml_report_formatter.cpp
)
target_compile_options(boost_test_exec_monitor.static PRIVATE -Wall -Wno-variadic-macros)
set_target_properties(boost_test_exec_monitor.static PROPERTIES OUTPUT_NAME boost_test_exec_monitor)

add_library(boost_unit_test_framework.static STATIC
    ${BOOST_SOURCE_DIR}/libs/test/src/compiler_log_formatter.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/debug.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/decorator.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/execution_monitor.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/framework.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/plain_report_formatter.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/progress_monitor.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/results_collector.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/results_reporter.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/test_framework_init_observer.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/test_tools.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/test_tree.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/unit_test_log.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/unit_test_main.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/unit_test_monitor.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/unit_test_parameters.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/junit_log_formatter.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/xml_log_formatter.cpp
    ${BOOST_SOURCE_DIR}/libs/test/src/xml_report_formatter.cpp
)
target_compile_options(boost_unit_test_framework.static PRIVATE -Wall -Wno-variadic-macros)
set_target_properties(boost_unit_test_framework.static PROPERTIES OUTPUT_NAME boost_unit_test_framework)

add_library(boost_thread.static STATIC
    ${BOOST_SOURCE_DIR}/libs/thread/src/pthread/thread.cpp
    ${BOOST_SOURCE_DIR}/libs/thread/src/pthread/once.cpp
    ${BOOST_SOURCE_DIR}/libs/thread/src/future.cpp
)
target_compile_options(boost_thread.static PRIVATE
    ${compile_flags_3}
    -Wextra
    -Wno-long-long
    -Wno-unused-parameter
    -Wunused-function
    -pedantic
    -DBOOST_THREAD_DONT_USE_CHRONO
)
set_target_properties(boost_thread.static PROPERTIES OUTPUT_NAME boost_thread)

add_library(boost_timer.static STATIC
    ${BOOST_SOURCE_DIR}/libs/timer/src/auto_timers_construction.cpp
    ${BOOST_SOURCE_DIR}/libs/timer/src/cpu_timer.cpp
)
target_compile_options(boost_timer.static PRIVATE
    -Wall
    -DBOOST_CHRONO_STATIC_LINK=1
    -DBOOST_TIMER_STATIC_LINK=1
)
set_target_properties(boost_timer.static PROPERTIES OUTPUT_NAME boost_timer)

add_library(boost_type_erasure.static STATIC
    ${BOOST_SOURCE_DIR}/libs/type_erasure/src/dynamic_binding.cpp
)
target_compile_options(boost_type_erasure.static PRIVATE
    ${compile_flags_3}
    -DBOOST_CHRONO_STATIC_LINK=1
    -DBOOST_SYSTEM_STATIC_LINK=1
    -DBOOST_THREAD_USE_LIB=1
)
set_target_properties(boost_type_erasure.static PROPERTIES OUTPUT_NAME boost_type_erasure)

set_source_files_properties(${BOOST_SOURCE_DIR}/libs/wave/src/instantiate_cpp_exprgrammar.cpp PROPERTIES COMPILE_OPTIONS -Wall)
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/wave/src/instantiate_cpp_grammar.cpp PROPERTIES COMPILE_OPTIONS -Wall)
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/wave/src/instantiate_cpp_literalgrs.cpp PROPERTIES COMPILE_OPTIONS -Wall)
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/wave/src/instantiate_defined_grammar.cpp PROPERTIES COMPILE_OPTIONS -Wall)
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/wave/src/instantiate_predef_macros.cpp PROPERTIES COMPILE_OPTIONS -Wall)
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/wave/src/instantiate_re2c_lexer.cpp PROPERTIES COMPILE_OPTIONS -Wall)
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/wave/src/instantiate_re2c_lexer_str.cpp PROPERTIES COMPILE_OPTIONS -Wall)
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/wave/src/token_ids.cpp PROPERTIES COMPILE_OPTIONS -Wall)
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/wave/src/wave_config_constant.cpp PROPERTIES COMPILE_OPTIONS -Wall)
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/wave/src/cpplexer/re2clex/aq.cpp PROPERTIES COMPILE_OPTIONS -Wall)
set_source_files_properties(${BOOST_SOURCE_DIR}/libs/wave/src/cpplexer/re2clex/cpp_re.cpp PROPERTIES COMPILE_OPTIONS -w)
add_library(boost_wave.static STATIC
    ${BOOST_SOURCE_DIR}/libs/wave/src/instantiate_cpp_exprgrammar.cpp
    ${BOOST_SOURCE_DIR}/libs/wave/src/instantiate_cpp_grammar.cpp
    ${BOOST_SOURCE_DIR}/libs/wave/src/instantiate_cpp_literalgrs.cpp
    ${BOOST_SOURCE_DIR}/libs/wave/src/instantiate_defined_grammar.cpp
    ${BOOST_SOURCE_DIR}/libs/wave/src/instantiate_predef_macros.cpp
    ${BOOST_SOURCE_DIR}/libs/wave/src/instantiate_re2c_lexer.cpp
    ${BOOST_SOURCE_DIR}/libs/wave/src/instantiate_re2c_lexer_str.cpp
    ${BOOST_SOURCE_DIR}/libs/wave/src/token_ids.cpp
    ${BOOST_SOURCE_DIR}/libs/wave/src/wave_config_constant.cpp
    ${BOOST_SOURCE_DIR}/libs/wave/src/cpplexer/re2clex/aq.cpp
    ${BOOST_SOURCE_DIR}/libs/wave/src/cpplexer/re2clex/cpp_re.cpp
)
target_compile_options(boost_wave.static PRIVATE -DBOOST_THREAD_USE_LIB=1)
set_target_properties(boost_wave.static PROPERTIES OUTPUT_NAME boost_wave)
