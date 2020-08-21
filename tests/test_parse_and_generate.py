import os
import shutil
import subprocess
import sys
import unittest

__module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, __module_dir)
import base  # noqa: E402
from build_migrator.helpers import get_command_target  # noqa: E402


class TestParseAndGenerate(base.TestBase):
    def test_generate_from_build_log_with_absolute_paths_unix(self):
        """Check that build log that uses absolute paths can be processed correctly (Unix / GCC)
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("abspath_unix")
        prebuilt_dir = os.path.join(self.test_method_out_dir, "out", "prebuilt")

        # ignore_compile_flags: workaround for SailfishOS
        self.parse_and_generate(
            "linux", project="openssl", ignore_compile_flags=["-m(32|64)"]
        )

        path = os.path.join(prebuilt_dir, "crypto/aes/aes-x86_64.s")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(prebuilt_dir, "include/openssl/opensslconf.h")
        self.assertTrue(os.path.exists(path), path)

    def test_generate_from_build_log_with_relative_paths_unix(self):
        """Check that build log that uses relative paths can be processed correctly (Unix / GCC)
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("relpath_unix")

        # ignore_compile_flags: workaround for SailfishOS
        self.parse_and_generate(
            "linux", project="openssl", ignore_compile_flags=["-m(32|64)"]
        )

        prebuilt_dir = os.path.join(self.test_method_out_dir, "out", "prebuilt")
        path = os.path.join(prebuilt_dir, "crypto/aes/aes-x86_64.s")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(prebuilt_dir, "include/openssl/opensslconf.h")
        self.assertTrue(os.path.exists(path), path)

    def test_generate_from_build_log_with_absolute_paths_windows(self):
        """Check that build log that uses absolute paths can be processed correctly (Windows / MSVC)
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("abspath_windows")

        self.parse_and_generate("windows", project="openssl")

        prebuilt_dir = os.path.join(self.test_method_out_dir, "out", "prebuilt")
        path = os.path.join(prebuilt_dir, "crypto/aes/aes-586.asm")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(prebuilt_dir, "include/openssl/opensslconf.h")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(prebuilt_dir, "libcrypto.rc")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(prebuilt_dir, "libcrypto.def")
        self.assertTrue(os.path.exists(path), path)

    def test_generate_from_build_log_with_relative_paths_windows(self):
        """Check that build log that uses relative paths can be processed correctly (Windows / MSVC)
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("relpath_windows")

        self.parse_and_generate("windows", project="openssl")

        prebuilt_dir = os.path.join(self.test_method_out_dir, "out", "prebuilt")
        path = os.path.join(prebuilt_dir, "crypto/aes/aes-586.asm")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(prebuilt_dir, "include/openssl/opensslconf.h")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(prebuilt_dir, "libcrypto.rc")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(prebuilt_dir, "libcrypto.def")
        self.assertTrue(os.path.exists(path), path)

    def test_generate_from_build_log_with_cp_ln_mv(self):
        """Check that files that were copied during build are not treated as prebuilt files
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("cp_ln_mv")

        alias_dir = os.path.normpath(
            os.path.join(os.getcwd(), self.test_method_dir, "source/alias")
        ).replace("\\", "/")
        alias_cpp = os.path.normpath(os.path.join(alias_dir, "alias.cpp")).replace(
            "\\", "/"
        )
        self.parse_and_generate(
            "linux",
            path_aliases=[[alias_dir, "@ALIAS@"], [alias_cpp, "@ALIAS@/alias.cpp"]],
        )

    def test_generate_from_build_log_with_complex_command(self):
        """Check that complex command lists are processed correctly
        Currently, "correctly" means that each command in list should be converted to CMake,
        regardless of whether it's actually been executed during build.
        Example:
         * rm abc && gcc ... || cd ../source && touch ../build/abc && gcc ...
        Note: additional commands that generate the same target are ignored
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("complex_command")

        self.parse_and_generate("linux")

    def test_build_in_source(self):
        """Check that building in source is supported
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("build_in_source")

        self.parse_and_generate(
            "linux", build_dirs=[os.path.join(self.test_method_dir, "source/build")]
        )

    def test_response_file_unix(self):
        """Check that build logs with response files can be processed correctly (Unix / GCC)
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("response_file_unix")

        self.parse_and_generate("linux")

    def test_response_file_windows(self):
        """Check that build logs with response files can be processed correctly (Windows / MSVC)
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("response_file_windows")

        self.parse_and_generate("windows")

    def test_response_file_removed(self):
        """Check that build logs with *already removed* response files can be processed correctly, if their content was added to log
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("response_file_removed")

        self.parse_and_generate("linux")

    def test_response_file_not_found(self):
        """
        Check that build logs with nonexistent response files,
        which content was not added to build log,
        can still be correctly processed if such
        response files are not essential.
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("response_file_not_found")

        self.parse_and_generate("windows")

    def test_complex_command_with_response_files(self):
        """Check that complex command with multiple commands containing response files work (Windows / MSVC)
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("complex_command_with_response_files")

        self.parse_and_generate("windows")

    def test_multiple_build_dirs(self):
        """Check that parsing with multiple build dirs is supported
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("multiple_build_dirs")

        self.parse_and_generate("linux")

    def test_multiple_logs(self):
        """Check that converting multiple logs into one CMakeLists.txt is supported
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("multiple_logs")

        self.parse_and_generate("linux")

    def test_working_directory_change(self):
        """Check that working directory changes are processed correctly
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("working_directory_change")

        self.parse_and_generate("linux")

    def test_external_path_relocatable(self):
        """Check that files not under build or source dirs don't break the parser
        Due to max_relpath_level == 2 and external path being only one level up the source dir,
        it results in a relocatable path
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("external_path_relocatable")

        self.parse_and_generate(
            "linux",
            max_relpath_level=2,
            build_dirs=[os.path.join(self.test_method_dir, "source/build")],
        )

    def test_external_path_not_relocatable(self):
        """Check that files not under build or source dirs don't break the parser
        Due to max_relpath_level == 0 the external path becomes not relocatable
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("external_path_not_relocatable")

        self.parse_and_generate("linux", max_relpath_level=0)

    def test_external_path_alias(self):
        """Check that files not under build or source directory can be made relocatable using path aliases
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("external_path_alias")

        path = os.path.normpath(os.path.join(self.test_method_dir, "external")).replace(
            "\\", "/"
        )
        self.parse_and_generate(
            "linux",
            max_relpath_level=0,
            path_aliases=[[path, "@external_include_dir@"]],
        )
        
    def test_external_path_alias_with_optimizer_v2(self):
        """Check that files not under build or source directory can link with externally defined target which provides necessary include directories
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("external_path_alias_with_optimizer_v2")

        path = os.path.normpath(os.path.join(self.test_method_dir, "external")).replace(
            "\\", "/"
        )
        self.parse_and_generate(
            "linux",
            max_relpath_level=0,
            path_aliases=[
                [path + "/include", "@external_include_dir@"],
                [path + "/lib/libexternal.a", "@external_lib@"]
            ],
            flag_optimizer_ver="2",
            aggressive_optimization=True
        )


    def test_resolve_library_unix(self):
        """Test shared/static library resolution for Unix / GCC
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("resolve_library_unix")

        self.parse_and_generate("linux")

    def test_resolve_library_windows(self):
        """Test shared/static library resolution for Windows / MSVC
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("resolve_library_windows")

        self.parse_and_generate("windows", presets=["windows", "autotools"])

    def test_ninja(self):
        """Check that Ninja-style logs can be processed correctly
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("ninja")

        self.parse_and_generate("linux", presets=["linux", "ninja"])

    def test_darwin(self):
        """Check that Mac OS X / Darwin logs can be processed correctly
        """

        if not self.has_clang:
            self.skipTest("Clang not found in PATH")

        self.set_test_data_subdir("darwin")

        self.parse_and_generate("darwin", ignore_compile_flags=[r"^-arch "])

        path = os.path.join(self.test_method_out_dir, "out/prebuilt", "libbar.def")
        self.assertTrue(os.path.exists(path), path)

    def test_darwin_mm(self):
        """Check that logs with .mm files can be processed correctly on Mac OS X / Darwin
        """

        if not self.has_clang:
            self.skipTest("Clang not found in PATH")

        self.set_test_data_subdir("darwin_mm")

        self.parse_and_generate("darwin", ignore_compile_flags=[r"^-arch "])

    def test_strace_complex(self):
        """Check that complex strace logs can be parsed correctly
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("strace_complex")

        self.parse_and_generate(
            "linux",
            presets=["linux", "strace"],
            path_aliases=[[r"/usr/bin/cc", "gcc"], [r"/usr/bin/c++", "g++"]],
        )

    def test_strace_minimal(self):
        """Check that simple, but exaustive, strace logs can be parsed correctly
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("strace_minimal")

        self.parse_and_generate("linux", presets=["linux", "strace"])

    def test_strace_multiple_logs(self):
        """Check that converting multiple strace logs into one CMakeLists.txt is supported
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("strace_multiple_logs")

        self.parse_and_generate("linux", presets=["linux", "strace"])

    def test_strace_response_file(self):
        """Check that strace logs with response files can be parsed correctly
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("strace_response_file")

        self.parse_and_generate("linux", presets=["linux", "strace"])

    def test_strace_replace(self):
        """Check that --replace_strace flag works
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("strace_replace")

        self.parse_and_generate(
            "linux",
            presets=["linux", "strace"],
            replace_strace=[
                # fix gcc path
                ('"where-is-gcc"', '"gcc"'),
                # fix source file path
                ('source/incorrect-path.c"', 'source/f.c"'),
                # skip unsupported utility that will otherwise be handled by gnu_ar.py
                ('"not-ar"', '"unsupported"'),
            ],
        )

    def test_multiple_asm_compilers(self):
        """
        Check that target using object files from multiple different
        assembler compilers can be generated correctly.
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("multiple_asm_compilers")

        self.parse_and_generate("windows", log_type="msbuild")

    def test_rc_dependencies(self):
        """
        Check that .rc file dependencies are discovered and processed correctly
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("rc_dependencies")

        self.parse_and_generate("windows")

    def test_ms_assembler_dependencies(self):
        """
        Check that MS assembler (ML.EXE) source file dependencies are discovered and processed
        correctly
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("ms_assembler_dependencies")

        self.parse_and_generate("windows")

    def test_nasm_dependencies(self):
        """
        Check that NASM source file dependencies are discovered and processed
        correctly:
        1. #included files
        2. -P option: pre-included files
        """

        if not self.has_nasm or not self.has_msvc:
            self.skipTest("NASM or MSVC not found in PATH")

        self.set_test_data_subdir("nasm_dependencies")

        self.parse_and_generate("windows", presets=["windows", "autotools"])

    def test_yasm_nasm_dependencies(self):
        """
        Check that YASM (NASM mode) source file dependencies are discovered and processed
        correctly:
        1. #included files
        2. -P option: pre-included files
        """
        if not self.has_yasm or not self.has_msvc:
            self.skipTest("YASM or MSVC not found in PATH")

        self.set_test_data_subdir("yasm_nasm_dependencies")

        self.parse_and_generate("windows")

    def test_yasm_gas_dependencies(self):
        """
        Check that YASM (GNU assembler mode) source file dependencies are discovered and processed
        correctly (#included files)
        """
        if not self.has_yasm or not self.has_msvc:
            self.skipTest("YASM or MSVC not found in PATH")

        self.set_test_data_subdir("yasm_gas_dependencies")

        self.parse_and_generate("windows")

    def test_gcc_assembler_dependencies(self):
        """
        Check that GCC (GNU) assembler file dependencies are discovered and processed
        correctly (#included files)
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("gcc_assembler_dependencies")

        # ignore_compile_flags: workaround for SailfishOS
        self.parse_and_generate(
            "linux", log_type="make", ignore_compile_flags=["-m(32|64)"]
        )

    def test_msbuild_multiline_commands(self):
        """
        MSBuild sometimes separates Link and Lib arguments by newline
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("msbuild_multiline_commands")

        self.parse_and_generate(
            "windows",
            log_type="msbuild",
            path_aliases=[
                [
                    r"C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\VC\Tools\MSVC\14.12.25827\bin\HostX64\x64\CL.exe",
                    "cl.exe",
                ]
            ],
        )

    def test_msbuild_multiline_commands_2(self):
        """
        MSBuild sometimes separates Link and Lib arguments by newline
        (second version)
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("msbuild_multiline_commands_2")

        self.parse_and_generate(
            "windows",
            log_type="msbuild",
            path_aliases=[
                [
                    r"C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\CL.exe",
                    "cl.exe",
                ],
                [
                    r"C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\Lib.exe",
                    "lib.exe",
                ],
            ],
        )

    def test_gcc_whole_archive(self):
        """Check that GCC linker option -Wl,--whole-archive is supported
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("gcc_whole_archive")

        self.parse_and_generate("linux", log_type="make")

    def test_library_alias(self):
        """Check that library aliases work (GCC)
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("gcc_library_alias")

        alias_dir = os.path.normpath(
            os.path.join(os.getcwd(), self.test_method_dir, "build")
        ).replace("\\", "/")
        alias1 = os.path.normpath(os.path.join(alias_dir, "libimpl1.a")).replace(
            "\\", "/"
        )
        alias2 = os.path.normpath(os.path.join(alias_dir, "libimpl2.a")).replace(
            "\\", "/"
        )
        self.parse_and_generate(
            "linux",
            log_type="make",
            path_aliases=[[alias1, "@ALIAS1@"], [alias2, "@ALIAS2@"]],
        )

    def test_lib_from_symlink_object(self):
        """Check that library can be created with symlink to object file
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("lib_from_symlink_object")

        self.parse_and_generate("linux", presets=["linux", "strace"])

    def test_lib_from_symlink_object_without_optimizations(self):
        """
        Check that library can be created with symlink to object file
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("lib_from_symlink_object")

        self.parse_and_generate(
            "linux",
            cmakelists_name="CMakeLists_no_optimizations.txt",
            dont_optimize=True,
            presets=["linux", "strace"],
        )

    def test_object_lib_copy_is_top_level_target(self):

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("object_lib_copy_is_top_level_target")

        self.parse_and_generate(
            "linux", presets=["linux", "autotools"], targets=["liba.so", "d.o"]
        )

    def test_merge_object_libs_and_copy_object_is_top_level_target(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir(
            "merge_object_libs_and_copy_object_is_top_level_target"
        )

        self.parse_and_generate(
            "linux",
            presets=["linux", "autotools"],
            targets=["liba.so", "liba_foo.so", "liba_mixed.so", "a3.o"],
            cmakelists_name="CMakeLists.txt",
            flag_optimizer_ver="2",
        )

    def test_gcc_ar_extract_objects_from_archive(self):
        """Check that object extracted from built library can be properly used in another target
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("gcc_ar_extract_objects_from_archive")

        self.parse_and_generate("linux", presets=["linux", "strace"])

    def test_msvc_link_toolchain_libraries(self):
        """
        Generate CMakeLists.txt for linker command that uses
        many unknown toolchain libraries (MSVC).
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("msvc_link_toolchain_libraries")

        self.parse_and_generate("windows")

    def test_complex_flag_value_msvc(self):
        """
        Generate CMakeLists.txt for target with complex flag value:
        -DVALUES={ "1.a", "2.b", "3.c" }
        (MSVC)
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("complex_flag_value_msvc")

        self.parse_and_generate("windows")

    def test_complex_flag_value_gcc_make(self):
        """
        Generate CMakeLists.txt for target with complex flag value:
        -DVALUES={ "1.a", "2.b", "3.c" }
        (GCC)
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("complex_flag_value_gcc_make")

        self.parse_and_generate("linux", log_type="make")

    def test_complex_flag_value_gcc_strace(self):
        """
        Generate CMakeLists.txt for target with complex flag value:
        -DVALUES={ "1.a", "2.b", "3.c" }
        (GCC)
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("complex_flag_value_gcc_strace")

        self.parse_and_generate("linux", presets=["linux", "strace"])

    def _same_source_with_different_flags_gcc(self, **kwargs):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("same_source_with_different_flags_gcc")

        self.parse_and_generate("linux", log_type="make", **kwargs)

    def test_same_source_with_different_flags_v2_gcc(self):
        """
        Generate CMakeLists.txt for target that uses multiple object files
        compiled from the same source file.
        (GCC, optimizer v2)
        """

        self._same_source_with_different_flags_gcc(
            cmakelists_name="CMakeLists_v2.txt", flag_optimizer_ver="2"
        )

    def _same_source_with_different_flags_msvc_c(self, **kwargs):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("same_source_with_different_flags_msvc_c")

        self.parse_and_generate("windows", **kwargs)

    def _same_source_with_different_flags_msvc_asm(self, **kwargs):
        if not (self.has_msvc and self.has_yasm and self.has_nasm):
            self.skipTest("MSVC or YASM or NASM not found in PATH")

        self.set_test_data_subdir("same_source_with_different_flags_msvc_asm")

        self.parse_and_generate("windows", **kwargs)

    def test_same_source_with_different_flags_v2_msvc_c(self):
        """
        Generate CMakeLists.txt that uses multiple object files
        compiled from the same C/C++ file.
        (MSVC, flag optimizer v2)
        """

        self._same_source_with_different_flags_msvc_c(
            cmakelists_name="CMakeLists_v2.txt", flag_optimizer_ver="2"
        )

    def test_same_source_with_different_flags_v2_msvc_asm(self):
        """
        Generate CMakeLists.txt that uses multiple object files
        compiled from the same assembler file.
        Generated CMakeLists.txt is currently incorrect and won't build:
        NASM/MASM sources do not inherit target's flags (CMake bug?).
        target_yasm_sources() is designed to behave similar to NASM/MASM,
        hence it doesn't inherit flags, too. But this behavior can be
        easily changed, unlike CMake implementation.
        (MSVC, flag optimizer v2)
        """

        self.skipTest("CMake does not proparage target flags to NASM/MASM sources")

        self._same_source_with_different_flags_msvc_asm(
            cmakelists_name="CMakeLists_v2.txt", flag_optimizer_ver="2"
        )

    def test_merge_object_libs_gcc(self):
        """
        Generate CMakeLists.txt for target that uses merged object files
        compiled from the same source file.
        (GCC, optimizer v2)
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("merge_object_libs_gcc")

        self.parse_and_generate("linux", log_type="make", flag_optimizer_ver="2")

    def test_merge_object_libs_msvc_c(self):
        """
        Generate CMakeLists.txt that uses multiple object files
        compiled from the same C/C++ file.
        (MSVC, flag optimizer v2)
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("merge_object_libs_msvc_c")

        self.parse_and_generate("windows", flag_optimizer_ver="2")

    def test_merge_object_libs_msvc_asm(self):
        """
        Generate CMakeLists.txt that uses merged object files
        compiled from the same assembler file.
        Generated CMakeLists.txt is currently incorrect and won't build:
        NASM/MASM sources do not inherit target's flags (CMake bug?).
        target_yasm_sources() is designed to behave similar to NASM/MASM,
        hence it doesn't inherit flags, too. But this behavior can be
        easily changed, unlike CMake implementation.
        (MSVC, flag optimizer v2)
        """

        self.skipTest("CMake does not proparage target flags to NASM/MASM sources")
        if not (self.has_msvc and self.has_yasm and self.has_nasm):
            self.skipTest("MSVC or YASM or NASM not found in PATH")

        self.set_test_data_subdir("same_source_with_different_flags_msvc_asm")

        self.parse_and_generate("windows", flag_optimizer_ver="2")

    def test_merge_object_libs_with_generated_sources_msvc(self):
        """
        Generate CMakeLists.txt that uses multiple object files
        compiled from the same generated C/C++ file.
        Also generate list only for dll target to ensure that proper dependencies are set
        (MSVC, flag optimizer v2)
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("merge_object_libs_with_generated_sources_msvc")

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            extra_targets=[
                get_command_target(
                    "generate_cpp1",
                    "generate_cpp",
                    ["@source_dir@/test1.descr", "@build_dir@/generated/test1.cpp"],
                    "@build_dir@/generated/test1.cpp",
                    dependencies=["@source_dir@/test1.descr"],
                ),
                get_command_target(
                    "generate_cpp2",
                    "generate_cpp",
                    ["@source_dir@/test2.descr", "@build_dir@/generated/test2.cpp"],
                    "@build_dir@/generated/test2.cpp",
                    dependencies=["@source_dir@/test2.descr"],
                ),
            ],
            targets=["test1.dll", "test2.dll", "test3.dll"],
        )

    def test_call_compiler_without_specified_flags(self):
        """
        clang-cl produces a warning (as error) when called with /Brepro
        """
        if not self.has_clang_cl:
            self.skipTest("clang-cl not found in PATH")

        self.set_test_data_subdir("clang_cl")

        self.parse_and_generate("windows", ignore_compile_flags=["^/Brepro$"])

    def test_prebuilt_object_file_msvc(self):
        """
        Check that CMakeLists.txt can be generated for targets
        with object files that were compiled outside current build.
        (MSVC)
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("prebuilt_object_file_msvc")

        self.parse_and_generate("windows")

        object_file = os.path.join(self.test_method_out_dir, "out/prebuilt/2.o")
        self.assertTrue(os.path.exists(object_file), object_file)

        object_file = os.path.join(self.test_method_out_dir, "out/prebuilt/dir/3.obj")
        self.assertTrue(os.path.exists(object_file), object_file)

    def test_prebuilt_object_file_gcc(self):
        """
        Check that CMakeLists.txt can be generated for targets
        with object files that were compiled outside current build.
        (GCC)
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("prebuilt_object_file_gcc")

        self.parse_and_generate("linux", log_type="make")

        object_file = os.path.join(self.test_method_out_dir, "out/prebuilt", "2.o")
        self.assertTrue(os.path.exists(object_file), object_file)

        object_file = os.path.join(
            self.test_method_out_dir, "out/prebuilt", "dir", "3.o"
        )
        self.assertTrue(os.path.exists(object_file), object_file)

    def test_msvc_import_lib(self):
        """
        Check that import libraries are correctly resolved to their dll.
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("msvc_import_lib")

        self.parse_and_generate("windows")

    def test_msvc_implib_and_static_lib_1(self):
        """
        Check that import libraries are correctly resolved to their dll
        in presence of static libraries with overlapping name:
        * static lib: liba.lib (defined first)
        * dynamic lib: liba.dll.lib + liba.lib
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("msvc_implib_and_static_lib_1")

        self.parse_and_generate("windows")

    def test_msvc_implib_and_static_lib_2(self):
        """
        Check that import libraries are correctly resolved to their dll
        in presence of static libraries with overlapping name:
        * dynamic lib: liba.dll.lib + liba.lib (defined first)
        * static lib: liba.lib
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("msvc_implib_and_static_lib_2")

        self.parse_and_generate("windows")

    def test_prebuilt_libs_gcc(self):
        """
        Check that CMakeLists.txt can be generated for targets
        with libraries that were compiled outside current build.
        (GCC)
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("prebuilt_libs_gcc")

        self.parse_and_generate("linux", log_type="make")

    def test_prebuilt_libs_msvc(self):
        """
        Check that CMakeLists.txt can be generated for targets
        with libraries that were compiled outside current build.
        (MSVC)
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("prebuilt_libs_msvc")

        self.parse_and_generate("windows")

    def test_spaces_in_path_msvc(self):
        """
        Check that CMakeLists.txt can be generated for targets
        with include / lib / source paths containing space
        characters.
        (MSVC)
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("spaces_in_path_msvc")

        self.parse_and_generate("windows")

    def test_system_object_files_msvc(self):
        """
        Check that "Link Options" can be parsed correctly.
        https://docs.microsoft.com/en-us/cpp/c-runtime-library/link-options
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("system_object_files_msvc")

        self.parse_and_generate("windows")

    def test_target_naming_and_output_subdirs_windows(self):
        """
        Check that CMakeLists.txt can be generated correctly for
        artifacts with same name in different directories.
        (MSVC, Windows)
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("target_naming_windows")

        self.parse_and_generate("windows", preserve_output_path=True)

    def test_gcc_ignore_compile_options_during_linking(self):
        """
        Ignore compiler flags if no source files specified (GCC)
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("gcc_ignore_compile_options_during_linking")

        self.parse_and_generate("linux", log_type="make")

    def test_gcc_skip_object_files(self):
        """
        Compile an executable directly: gcc a.c b.c -o test
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("gcc_skip_object_files")

        self.parse_and_generate("linux", log_type="make")

    def test_msvc_ignore_object_files(self):
        """
        Compile a library/exe directly with MSVC
        """
        self.skipTest("Not implemented yet")
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("msvc_ignore_object_files")

        self.parse_and_generate("windows")

    def test_duplicate_flags_gcc(self):
        """
        Check that duplicate compiler and linker flags are removed correctly (GCC)
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("duplicate_flags_gcc")

        self.parse_and_generate("linux", log_type="make")

    def test_duplicate_flags_msvc(self):
        """
        Check that duplicate compiler and linker flags are removed correctly (MSVC)
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("duplicate_flags_msvc")

        self.parse_and_generate("windows")

    def test_windows_line_endings(self):
        """
        Parse build log with Windows line endings
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("windows_line_endings")

        self.parse_and_generate("windows")

    def test_linux_line_endings(self):
        """
        Parse build log with Linux line endings
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("linux_line_endings")

        self.parse_and_generate("linux", log_type="make")

    def test_mac_line_endings(self):
        """
        Parse build log with Mac line endings
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("mac_line_endings")

        self.parse_and_generate("darwin", log_type="make")

    def test_utf8_log_msvc(self):
        """
        Parse log in UTF-8 with non-ASCII characters
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("utf8_log_msvc")

        self.parse_and_generate("windows")

    def test_utf8_log_gcc(self):
        """
        Parse log in UTF-8 with non-ASCII characters
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("utf8_log_gcc")

        self.parse_and_generate("linux", log_type="make")

    def test_utf8_log_invalid_characters_msvc(self):
        """
        Parse log in UTF-8 with non-ASCII characters and invalid byte sequences
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("utf8_log_invalid_characters_msvc")

        self.parse_and_generate("windows")

    def test_utf8_log_invalid_characters_gcc(self):
        """
        Parse log in UTF-8 with non-ASCII characters and invalid byte sequences
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("utf8_log_invalid_characters_gcc")

        self.parse_and_generate("linux", log_type="make")

    def test_module_copy_naming(self):
        """
        Check that 'module_copy' target names do not clash with other targets
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("module_copy_naming")

        self.parse_and_generate("linux", log_type="make")

    def _generate_for_selected_targets(self, **kwargs):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("generate_for_selected_targets")

        build_dir = os.path.join(self.test_method_dir, "build")
        out_dir = os.path.join(self.test_method_out_dir, "out")

        # git doesn't support empty directories
        empty_dir = os.path.join(build_dir, "empty_dir")
        if not os.path.exists(empty_dir):
            os.mkdir(empty_dir)

        targets = [
            "a.static",  # target name
            os.path.join(build_dir, "libb.so.2.0.1"),  # library path
            os.path.join(build_dir, "LICENSE"),  # file path
            os.path.join(build_dir, "resources"),  # directory path
            os.path.join(build_dir, "1/2/3"),  # directory path
            empty_dir,
        ]
        self.parse_and_generate("linux", log_type="make", targets=targets, **kwargs)

        prebuilt_subdir = kwargs.get("prebuilt_subdir", "prebuilt")
        out_dir = os.path.join(self.test_method_out_dir, "out")
        if prebuilt_subdir:
            out_dir = os.path.join(out_dir, prebuilt_subdir)
        path = os.path.join(out_dir, "resources", "1.txt")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(out_dir, "resources", "2.txt")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(out_dir, "1/2/3", "1.txt")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(out_dir, "1/2/3", "2.txt")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(out_dir, "1", "file.txt")
        self.assertFalse(os.path.exists(path), path)

    def test_generate_for_selected_targets(self):
        """
        Check that --targets argument works for target names as well as
        file and directory paths.
        """
        self._generate_for_selected_targets()

    def test_generate_for_selected_targets_with_prebuilt_subdir(self):
        """
        Check that --targets argument works for target names as well as
        file and directory paths.
        If --prebuilt_subdir is specified, files should be
        put in that subdirectory.
        """
        self._generate_for_selected_targets(
            cmakelists_name="CMakeLists_with_prebuilt_subdir.txt",
            prebuilt_subdir="linux",
        )

    def test_generate_for_selected_targets_with_multiple_build_logs(self):
        """
        Check that --targets argument works correctly together with
        multi-file build logs
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir(
            "generate_for_selected_targets_with_multiple_build_logs"
        )

        build_dir = os.path.join(self.test_method_dir, "build")
        targets = [
            "a.static",  # target name
            os.path.join(build_dir, "libb.so.2.0.1"),  # library path
            os.path.join(build_dir, "LICENSE"),  # file path
        ]

        self.parse_and_generate("linux", log_type="make", targets=targets)

    def test_generate_for_selected_targets_with_path_aliases(self):
        """
        Check that --targets argument works correctly together with
        --path_alias
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("generate_for_selected_targets_with_path_aliases")

        build_dir = os.path.join(self.test_method_dir, "build")
        targets = [
            "a.static",  # target name
            os.path.join(build_dir, "libb.so.2.0.1"),  # library path
        ]
        sqlite_include_dir = os.path.join(build_dir, "sqlite_include")
        sqlite_h_path = os.path.join(sqlite_include_dir, "sqlite.h")
        self.parse_and_generate(
            "linux",
            log_type="make",
            targets=targets,
            path_aliases=[
                [sqlite_include_dir, "@EXTERNAL_DIR@"],
                [sqlite_h_path, "@EXTERNAL_DIR@/sqlite.h"],
            ],
            default_var_values=[["EXTERNAL_DIR", "sqlite/src"]],
            max_relpath_level=0,
        )

    def test_generate_targets_selected_using_recursive_glob(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("generate_targets_selected_using_recursive_glob")

        self.parse_and_generate("linux", log_type="make", targets=["*.so"])

    def test_empty_build_dir_generate_targets_selected_using_path(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("test_empty_build_dir")

        self.parse_and_generate(
            "linux",
            log_type="make",
            targets=["out/libb.so"],
            cmakelists_name="CMakeLists1.txt",
        )

    def test_empty_build_dir_generate_targets_selected_using_nonrecursive_glob(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("test_empty_build_dir")

        self.parse_and_generate(
            "linux",
            log_type="make",
            targets=["./*.so", "*/libc.a"],
            cmakelists_name="CMakeLists2.txt",
        )

    def test_empty_build_dir_generate_targets_selected_using_recursive_glob(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("test_empty_build_dir")

        self.parse_and_generate(
            "linux", log_type="make", targets=["*.a"], cmakelists_name="CMakeLists3.txt"
        )

    def test_object_library_msvc(self):
        """
        Check that object file target that are not used by other targets
        turn into add_library(OBJECT).
        (MSVC)
        """
        self.skipTest("Not implemented")

    def test_object_library_gcc(self):
        """
        Check that object file target that are not used by other targets
        turn into add_library(OBJECT).
        (GCC)
        """
        self.skipTest("Not implemented")

    def test_shared_from_static_without_sources(self):
        """Check that building shared library from static library is supported with fake source file
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("shared_from_static_without_sources")

        self.parse_and_generate("linux", log_type="make")

    def test_shared_from_static_without_sources_for_cpp(self):
        """Check that building shared library from static library is supported with fake source file for c++ projects
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("shared_from_static_without_sources_for_cpp")

        self.parse_and_generate("linux", log_type="make")

    def test_shared_from_static_without_sources_for_several_empty_targets(self):
        """Check that building shared library from static library is supported with fake source file for several empty targets
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir(
            "shared_from_static_without_sources_for_several_empty_targets"
        )

        self.parse_and_generate("linux", log_type="make")

    def test_target_with_yasm_sources_only(self):
        if not self.has_msvc or not self.has_yasm:
            self.skipTest("YASM or MSVC not found in PATH")

        self.set_test_data_subdir("target_with_yasm_sources_only")

        self.parse_and_generate("windows")

    def test_check_order_of_link_flags(self):
        """Check that order of link flags is not changed
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("check_order_of_link_flags")

        self.parse_and_generate("linux", log_type="make")

    def _group_common_flags_clang_cl(self, **kwargs):
        if not (
            self.has_msvc and self.has_clang_cl and self.has_yasm and self.has_nasm
        ):
            self.skipTest("MSVC or clang-cl or YASM or NASM not found in PATH")

        self.set_test_data_subdir("group_common_flags_clang_cl")

        self.parse_and_generate("windows", **kwargs)

    def test_group_common_flags_clang_cl_v2(self):
        """
        Test 2nd version of common flag grouping algorithm.
        Work in progress, but generated CMakeLists.txt builds correctly.
        (clang-cl, lld-link, nasm, yasm, masm, rc)
        """

        self._group_common_flags_clang_cl(
            cmakelists_name="CMakeLists_v2.txt", flag_optimizer_ver="2"
        )

    def test_ignore_compile_flags_msvc(self):
        """
        Test --ignore_compile_flags + MSVC
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        # This path is referenced in build logs
        self.assertTrue(os.path.exists("C:/Windows/System32"))

        self.set_test_data_subdir("ignore_compile_flags_msvc")

        ignore_compile_flags = [r"(?i).*c:[/\\]Windows[/\\].*", r"(?i).*bad_include$"]
        self.parse_and_generate("windows", ignore_compile_flags=ignore_compile_flags)

    def test_ignore_compile_flags_clang_cl(self):
        """
        Test --ignore_compile_flags + clang-cl
        """

        if not self.has_msvc or not self.has_clang_cl:
            self.skipTest("MSVC or clang-cl not found in PATH")

        # This path is referenced in build logs
        self.assertTrue(os.path.exists("C:/Windows/System32"))

        self.set_test_data_subdir("ignore_compile_flags_clang_cl")

        ignore_compile_flags = [r"(?i).*c:[/\\]Windows[/\\].*", r"(?i).*bad_include$"]
        self.parse_and_generate("windows", ignore_compile_flags=ignore_compile_flags)

    def test_ignore_link_flags_msvc(self):
        """
        Test --ignore_link_flags + MSVC
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        # This path is referenced in build logs
        self.assertTrue(os.path.exists("C:/Windows/System32"))

        self.set_test_data_subdir("ignore_link_flags_msvc")

        ignore_link_flags = [r"(?i).*c:[/\\]Windows[/\\].*", r"(?i).*bad_lib$"]
        self.parse_and_generate("windows", ignore_link_flags=ignore_link_flags)

    def test_too_many_source_files(self):
        """
        Test that in case a target has >30 source files,
        source file list moves to external file.
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("too_many_source_files")

        self.parse_and_generate("linux")

        source_list = os.path.join(
            self.test_method_out_dir, "out/APP_SRC.cmake"
        )
        self.assertTrue(os.path.exists(source_list), source_list)

    def test_too_many_source_files_with_prebuilt_subdir(self):
        """
        Test that in case a target has >30 source files,
        source file list moves to external file.
        If --prebuilt_subdir is specified, source list should be
        created in that subdirectory.
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("too_many_source_files_with_prebuilt_subdir")

        self.parse_and_generate("linux", prebuilt_subdir="linux")

        source_list = os.path.join(self.test_method_out_dir, "out/APP_SRC.cmake")
        self.assertTrue(os.path.exists(source_list), source_list)

    def test_capture_sources(self):
        """
        Check that --capture_sources option works correctly
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("capture_sources")

        self.parse_and_generate(
            "linux", capture_sources=["a.h", "include/config.h"], targets=["a"],
        )

        out_dir = os.path.join(self.test_method_out_dir, "out")
        path = os.path.join(out_dir, "a.h")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(out_dir, "include/config.h")
        self.assertTrue(os.path.exists(path), path)

    def test_capture_sources_many_files(self):
        """
        Check that --capture_sources option works correctly
        when source file are grouped together into a 'directory' target.
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("capture_sources_many_files")

        self.parse_and_generate(
            "linux",
            capture_sources=["capture/*.h"],
            targets=["a"],
            source_subdir="source",
        )

        out_dir = os.path.join(self.test_method_out_dir, "out/source/capture")
        for num in range(0, 10):
            path = os.path.join(out_dir, str(num) + ".h")
            self.assertTrue(os.path.exists(path), path)

    def test_generate_for_selected_compiled_targets_with_common_deps(self):
        """
        Generate CMakeLists.txt only for selected targets with common dependencies.
        Check that common dependencies won't duplicate in resulting object model.
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir(
            "generate_for_selected_compiled_targets_with_common_deps"
        )

        self.parse_and_generate("linux", log_type="make", targets=["app_a", "app_b"])

    def test_rename_target(self):
        """
        Check that --rename flag works correctly
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("rename_target")

        self.parse_and_generate(
            "linux", log_type="make", rename_patterns=[["rename_me", "test"]]
        )

    def _required_target_not_found(self, **kwargs):
        self.assertRaisesRegexp(
            ValueError,
            "Required target not found",
            self.parse_and_generate,
            "linux",
            **kwargs
        )

    def _required_target_not_found_setup(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("required_target_not_found")

    def test_required_target_not_found_1(self):
        """
        Check that parser produces and error if one of the required
        targets is not found (--targets flag).
        --targets specifies cmake target name
        """
        self._required_target_not_found_setup()
        self._required_target_not_found(targets=["notfound"])

    def test_required_target_not_found_2(self):
        """
        Check that parser produces and error if one of the required
        targets is not found (--targets flag).
        --targets specifies path
        """
        self._required_target_not_found_setup()
        build_dir = os.path.join(self.test_method_dir, "build")
        self._required_target_not_found(
            targets=[os.path.join(build_dir, "libnotfound.so")]
        )

    def test_filename_case_windows(self):
        """
        Check that original filenames are preserved
        (Windows / MSVC)
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("filename_case_windows")

        build_dir = os.path.join(self.test_method_dir, "build")
        targets = [
            "application",
            "my_library",
            "test1.static",
            "test2.static",
            os.path.join(build_dir, "FILES/SomeFile.txt"),
        ]
        self.parse_and_generate("windows", targets=targets)

    def test_utf16_le_sources_windows_msvc(self):
        """
        Check that UTF-16 LE files can be parsed correctly on Windows (MSVC)
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("utf16_le_sources_windows_msvc")

        self.parse_and_generate("windows")

    def test_utf16_le_sources_windows_clang_cl(self):
        """
        Check that UTF-16 LE files can be parsed correctly on Windows (clang-cl)
        """

        self.skipTest("clang-cl does not support UTF-16")

        if not self.has_msvc or not self.has_clang_cl:
            self.skipTest("MSVC or clang-cl not found in PATH")

        self.set_test_data_subdir("utf16_le_sources_windows_clang_cl")

        self.parse_and_generate("windows")

    def test_target_with_flag_duplicates_optimizer_v2(self):
        """
        Target with multiple sources, each having non-empty
        compilation flags and include directories with duplicates
        + flag optimizer v2
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("target_with_flag_duplicates_optimizer_v2")

        self.parse_and_generate("linux", log_type="make", flag_optimizer_ver="2")

    def test_msvc_manifest_files(self):
        """
        Check that /MANIFESTINPUT and /MANIFESTFILE are handled correctly
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("msvc_manifest_files")

        self.parse_and_generate("windows")

    def test_optimizer_v2_move_common_flags_from_sources_to_target_1(self):
        """
        Move common compilation and include flags from sources to parent target
        (GCC)
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir(
            "optimizer_v2_move_common_flags_from_sources_to_target_1"
        )

        self.parse_and_generate(
            "linux", flag_optimizer_ver="2", log_type="make"
        )

    def test_optimizer_v2_move_common_flags_from_sources_to_target_2(self):
        """
        Move common compilation and include flags from sources to parent target
        Part of sources come from object files, another part is compiled directly
        in one compile+link call.
        (GCC)
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir(
            "optimizer_v2_move_common_flags_from_sources_to_target_2"
        )

        self.parse_and_generate(
            "linux", flag_optimizer_ver="2", log_type="make"
        )

    def test_optimizer_v2_move_common_flags_from_sources_to_target_3(self):
        """
        Move common compilation and include flags from sources to parent target
        Check that optimizations take place AFTER flag filter
        (MSVC)
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir(
            "optimizer_v2_move_common_flags_from_sources_to_target_3"
        )

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            keep_flags=[".+"],
            delete_flags=["ignore"],
            aggressive_optimization=True,
        )

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            keep_flags=[".+"],
            delete_flags=["ignore"],
            aggressive_optimization=True,
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000
        )

    def test_optimizer_v2_with_cmake_flag_fix(self):
        """
        Check compatibility of optimizer v2 with CMakeFixMultipleSourceInstancesWithDifferentFlags
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_with_cmake_flag_fix")

        self.parse_and_generate("windows", flag_optimizer_ver="2")

    def test_optimizer_v2_remove_redundant_link_flags(self):
        """
        Remove link flags from targets that don't need them (object libraries)
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_remove_redundant_link_flags")

        self.parse_and_generate(
            "linux", flag_optimizer_ver="2", log_type="make"
        )

    def test_optimizer_v2_remove_redundant_compiler_flags(self):
        """
        Remove compiler flags from targets that don't need them (all input objects are pre-built)
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_remove_redundant_compiler_flags")

        self.parse_and_generate(
            "linux", flag_optimizer_ver="2", log_type="make"
        )

    def test_optimizer_v2_global_compiler_flags_and_include_dirs_msvc(self):
        if not (self.has_msvc and self.has_nasm and self.has_yasm):
            self.skipTest("MSVC or NASM or YASM not found in PATH")

        self.set_test_data_subdir(
            "optimizer_v2_global_compiler_flags_and_include_dirs_msvc"
        )

        self.parse_and_generate("windows", flag_optimizer_ver="2")

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_global_compiler_flags_and_include_dirs_gcc(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir(
            "optimizer_v2_global_compiler_flags_and_include_dirs_gcc"
        )

        self.parse_and_generate("linux", flag_optimizer_ver="2")

        self.parse_and_generate(
            "linux",
            flag_optimizer_ver="2",
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_global_link_flags_gcc(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_global_link_flags_gcc")

        self.parse_and_generate("linux", flag_optimizer_ver="2")

        self.parse_and_generate(
            "linux",
            flag_optimizer_ver="2",
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_global_link_flags_msvc(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_global_link_flags_msvc")

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            keep_flags=[".+"],
            add_presets=False,
            log_type="make",
        )

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            keep_flags=[".+"],
            add_presets=False,
            log_type="make",
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_c_compiler_flags_and_include_dirs(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_c_compiler_flags_and_include_dirs")

        self.parse_and_generate("linux", flag_optimizer_ver="2")

        self.parse_and_generate(
            "linux",
            flag_optimizer_ver="2",
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_cxx_compiler_flags_and_include_dirs(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_cxx_compiler_flags_and_include_dirs")

        self.parse_and_generate("linux", flag_optimizer_ver="2")

        self.parse_and_generate(
            "linux",
            flag_optimizer_ver="2",
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_gasm_compiler_flags_and_include_dirs(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_gasm_compiler_flags_and_include_dirs")

        self.parse_and_generate("linux", flag_optimizer_ver="2")

        self.parse_and_generate(
            "linux",
            flag_optimizer_ver="2",
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_masm_compiler_flags_and_include_dirs(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_masm_compiler_flags_and_include_dirs")

        self.parse_and_generate("windows", flag_optimizer_ver="2")

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_nasm_compiler_flags_and_include_dirs_1(self):
        if not (self.has_msvc and self.has_nasm):
            self.skipTest("MSVC or NASM not found in PATH")

        self.set_test_data_subdir("optimizer_v2_nasm_compiler_flags_and_include_dirs_1")

        self.parse_and_generate("windows", flag_optimizer_ver="2")

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_nasm_compiler_flags_and_include_dirs_2(self):
        if not (self.has_msvc and self.has_nasm):
            self.skipTest("MSVC or NASM not found in PATH")

        self.set_test_data_subdir("optimizer_v2_nasm_compiler_flags_and_include_dirs_2")

        self.parse_and_generate("windows", flag_optimizer_ver="2")

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_rc_compiler_flags_and_include_dirs(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_rc_compiler_flags_and_include_dirs")

        self.parse_and_generate("windows", flag_optimizer_ver="2", keep_flags=[".+"])
        
        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            keep_flags=[".+"],
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_yasm_compiler_flags_and_include_dirs_1(self):
        if not (self.has_msvc and self.has_yasm):
            self.skipTest("MSVC or YASM not found in PATH")

        self.set_test_data_subdir("optimizer_v2_yasm_compiler_flags_and_include_dirs_1")

        self.parse_and_generate("windows", flag_optimizer_ver="2")

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_yasm_compiler_flags_and_include_dirs_2(self):
        if not (self.has_msvc and self.has_yasm):
            self.skipTest("MSVC or YASM not found in PATH")

        self.set_test_data_subdir("optimizer_v2_yasm_compiler_flags_and_include_dirs_2")

        self.parse_and_generate(
            "windows", flag_optimizer_ver="2", log_type="make"
        )

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            log_type="make",
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_static_link_flags(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_static_link_flags")

        self.parse_and_generate(
            "windows",
            add_presets=False,
            log_type="make",
            flag_optimizer_ver="2",
            keep_flags=[".+"],
        )

        self.parse_and_generate(
            "windows",
            add_presets=False,
            log_type="make",
            flag_optimizer_ver="2",
            keep_flags=[".+"],
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_shared_link_flags(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_shared_link_flags")

        self.parse_and_generate("linux", flag_optimizer_ver="2")

    def test_optimizer_v2_exe_link_flags(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_exe_link_flags")

        self.parse_and_generate("linux", flag_optimizer_ver="2")

        self.parse_and_generate(
            "linux",
            flag_optimizer_ver="2",
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_variables_for_compiler_flags_1(self):
        """
        variable optimizer + target_language_compile_options
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_variables_for_compiler_flags_1")

        self.parse_and_generate(
            "linux", flag_optimizer_ver="2", aggressive_optimization=True
        )

        self.parse_and_generate(
            "linux",
            flag_optimizer_ver="2",
            aggressive_optimization=True,
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_variables_for_compiler_flags_2(self):
        """
        variable optimizer + global flags
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_variables_for_compiler_flags_2")

        self.parse_and_generate(
            "linux", flag_optimizer_ver="2", aggressive_optimization=True
        )

        self.parse_and_generate(
            "linux",
            flag_optimizer_ver="2",
            aggressive_optimization=True,
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_variables_for_compiler_flags_3(self):
        """
        Variable optimizer is currently "greedy" and may produce
        suboptimal results. Significant memory+time may be required
        to check all possible optimization paths.
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_variables_for_compiler_flags_3")

        self.parse_and_generate(
            "linux", flag_optimizer_ver="2", aggressive_optimization=True
        )

    def test_optimizer_v2_variables_for_compiler_flags_4(self):
        """
        Check that global / target optimizers do not interfere
        with variable optimizer
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_variables_for_compiler_flags_4")

        self.parse_and_generate(
            "linux", flag_optimizer_ver="2", aggressive_optimization=True
        )

    def test_optimizer_v2_variables_for_compiler_flags_5(self):
        """
        Check that variable optimizer works with NASM, MASM,
        YASM, RC
        """

        if not (self.has_msvc and self.has_yasm and self.has_nasm):
            self.skipTest("MSVC or YASM or NASM not found in PATH")

        self.set_test_data_subdir("optimizer_v2_variables_for_compiler_flags_5")

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            keep_flags=[".+"],
            aggressive_optimization=True,
            add_presets=False,
            log_type="make",
        )

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            keep_flags=[".+"],
            aggressive_optimization=True,
            add_presets=False,
            log_type="make",
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_variables_for_include_dirs_gcc(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_variables_for_include_dirs_gcc")

        self.parse_and_generate(
            "linux", flag_optimizer_ver="2", aggressive_optimization=True
        )

    def test_optimizer_v2_variables_for_include_dirs_msvc(self):
        if not (self.has_msvc and self.has_yasm and self.has_nasm):
            self.skipTest("MSVC or YASM or NASM not found in PATH")

        self.set_test_data_subdir("optimizer_v2_variables_for_include_dirs_msvc")

        self.parse_and_generate(
            "windows", flag_optimizer_ver="2", aggressive_optimization=True
        )

    def test_optimizer_v2_variables_for_link_flags(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_variables_for_link_flags")

        self.parse_and_generate(
            "linux",
            flag_optimizer_ver="2",
            keep_flags=[".+"],
            aggressive_optimization=True,
        )

    def test_optimizer_v2_variables_for_link_libs_gcc(self):
        self.skipTest("GCC parser doesn't support arbitrary system libraries yet")

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_variables_for_link_libs_gcc")

        self.parse_and_generate(
            "linux", flag_optimizer_ver="2", aggressive_optimization=True
        )

    def test_optimizer_v2_variables_for_link_libs_msvc(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_variables_for_link_libs_msvc")

        self.parse_and_generate(
            "windows", flag_optimizer_ver="2", aggressive_optimization=True
        )

    def test_optimizer_v2_hard_mode_msvc(self):
        """
        Check that optimizer v2 can correctly process complex
        MSVC build log.
        """

        if not (self.has_msvc and self.has_yasm and self.has_nasm):
            self.skipTest("MSVC or YASM or NASM not found in PATH")

        self.set_test_data_subdir("optimizer_v2_hard_mode_msvc")

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            keep_flags=[".+"],
            add_presets=False,
            log_type="make",
        )

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            keep_flags=[".+"],
            add_presets=False,
            log_type="make",
            cmakelists_name="CMakeLists2.txt",
            class_optimization_threshold=1000,
        )

    def test_optimizer_v2_hard_mode_msvc_aggressive_optimization(self):
        """
        Check that optimizer v2 can correctly process complex
        MSVC build log.
        + aggressive optimization enabled
        """

        if not (self.has_msvc and self.has_yasm and self.has_nasm):
            self.skipTest("MSVC or YASM or NASM not found in PATH")

        self.set_test_data_subdir("optimizer_v2_hard_mode_msvc")

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            keep_flags=[".+"],
            aggressive_optimization=True,
            cmakelists_name="CMakeLists_aggressive_optimization.txt",
            add_presets=False,
            log_type="make",
        )

        self.parse_and_generate(
            "windows",
            flag_optimizer_ver="2",
            keep_flags=[".+"],
            aggressive_optimization=True,
            cmakelists_name="CMakeLists_aggressive_optimization2.txt",
            add_presets=False,
            log_type="make",
            class_optimization_threshold=1000,
        )

    def test_file_target_gsub(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("file_target_gsub")

        build_dir = os.path.join(self.test_method_dir, "build")
        targets = [
            os.path.join(build_dir, "utf-16-be.txt"),
            os.path.join(build_dir, "utf-8.txt"),
            os.path.join(build_dir, "utf-8-sig.txt"),
            "libtest.so",
        ]
        file_target_gsubs = [
            ("*.txt", "TEST", "_"),
            ("*.c", r'#include "\.\./', '#include "'),
        ]
        self.parse_and_generate(
            "linux",
            log_type="make",
            targets=targets,
            file_target_gsubs=file_target_gsubs,
            max_relpath_level=0,
        )

        generator_out_dir = os.path.join(self.test_method_out_dir, "out")
        for filename, encoding in [
            ("foo.c", None),
            ("utf-8.txt", None),
            ("utf-8-sig.txt", "utf-8-sig"),
            ("utf-16-be.txt", "utf-16-be"),
        ]:
            target_file = os.path.join(generator_out_dir, "prebuilt", filename)
            expected_file = os.path.join(self.test_method_dir, "files", filename)
            self.assertFilesEqual(expected_file, target_file, encoding=encoding)

    def test_file_target_change_encoding_and_gsub(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("file_target_change_encoding_and_gsub")

        build_dir = os.path.join(self.test_method_dir, "build")
        targets = [
            os.path.join(build_dir, "ui_unscaled_resources.rc"),
            os.path.join(build_dir, "libtest.so"),
        ]
        file_target_change_encodings = [
            ("*/ui_unscaled_resources.rc", "utf-16-le", "utf-8")
        ]
        file_target_gsubs = [
            (
                "*/ui_unscaled_resources.rc",
                r'"[^"]+test_e2e\\\\electron\\\\source',
                '"@ELECTRON_SOURCE_DIR_NATIVE@',
            )
        ]
        self.parse_and_generate(
            "linux",
            log_type="make",
            targets=targets,
            file_target_change_encodings=file_target_change_encodings,
            file_target_gsubs=file_target_gsubs,
        )

        generator_out_dir = os.path.join(self.test_method_out_dir, "out")
        target_file = os.path.join(
            generator_out_dir, "prebuilt/ui_unscaled_resources.rc"
        )
        expected_file = os.path.join(
            self.test_method_dir, "files", "ui_unscaled_resources.rc"
        )
        self.assertFilesEqual(expected_file, target_file)

    def test_file_target_change_encoding(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("file_target_change_encoding")

        build_dir = os.path.join(self.test_method_dir, "build")
        targets = [
            os.path.join(build_dir, "utf-16-be.txt"),
            os.path.join(build_dir, "utf-8-sig.txt"),
            "libtest.so",
        ]
        file_target_change_encodings = [
            ("*/utf-8-sig.txt", "utf-8-sig", "utf-8"),
            ("*/utf-16-be.txt", "utf-16-be", "utf-8"),
        ]
        self.parse_and_generate(
            "linux",
            log_type="make",
            targets=targets,
            file_target_change_encodings=file_target_change_encodings,
        )

        generator_out_dir = os.path.join(self.test_method_out_dir, "out")
        for filename in ["utf-8-sig.txt", "utf-16-be.txt"]:
            target_file = os.path.join(generator_out_dir, "prebuilt", filename)
            expected_file = os.path.join(self.test_method_dir, "files", filename)
            self.assertFilesEqual(expected_file, target_file)

    def test_implicit_gcc_output(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("implicit_gcc_output")

        self.parse_and_generate("linux")

    def test_gcc_create_and_link_library_object(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("gcc_create_and_link_library_object")

        self.parse_and_generate("linux")

    def test_gcc_link_shared_object_file_by_path(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("gcc_link_shared_object_file_by_path")

        self.parse_and_generate("linux")

    def _test_optimization_in_case_of_flag_order_significance(self, test_dir, **kwargs):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir(test_dir)
        self.parse_and_generate("linux", log_type="make", **kwargs)

    def test_optimization_in_case_of_flag_order_significance_1_optimizer_v2(self):
        self.skipTest("Flag order is wrong, task #3815995")
        self._test_optimization_in_case_of_flag_order_significance(
            "optimization_in_case_of_flag_order_significance_1",
            cmakelists_name="CMakeLists_v2.txt",
            flag_optimizer_ver="2",
        )

    def test_optimization_in_case_of_flag_order_significance_2_optimizer_v2(self):
        self.skipTest("Flag order is wrong, task #3815995")
        self._test_optimization_in_case_of_flag_order_significance(
            "optimization_in_case_of_flag_order_significance_2",
            cmakelists_name="CMakeLists_v2.txt",
            flag_optimizer_ver="2",
        )

    def test_optimization_in_case_of_flag_order_significance_3_optimizer_v2(self):
        self.skipTest("Flag order is wrong, task #3815995")
        self._test_optimization_in_case_of_flag_order_significance(
            "optimization_in_case_of_flag_order_significance_3",
            cmakelists_name="CMakeLists_v2.txt",
            keep_flags=[".+"],  # -U
            flag_optimizer_ver="2",
        )

    def test_optimization_in_case_of_flag_order_significance_4_optimizer_v2(self):
        self.skipTest("Flag order is wrong, task #3815995")
        self._test_optimization_in_case_of_flag_order_significance(
            "optimization_in_case_of_flag_order_significance_4",
            cmakelists_name="CMakeLists_v2.txt",
            keep_flags=[".+"],  # -U
            flag_optimizer_ver="2",
        )

    def test_windows_get_file_version_info(self):
        """
        Check that GetFileVersionInfo wrapper works correctly

        Note: CMake target property 'VERSION' doesn't do aything
        when building for MSVC.
        """

        if not self.on_windows():
            self.skipTest("Only Windows is supported")

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("windows_get_file_version_info")

        self.parse_and_generate("windows", keep_module_version=True)

    def test_mac_library_version_from_filename(self):
        """
        Parse shared library filename and set 'VERSION' target property
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("mac_library_version_from_filename")

        self.parse_and_generate("darwin", keep_module_version=True)

    def test_linux_library_version_from_filename(self):
        """
        Parse shared library filename and set 'VERSION' target property
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("linux_library_version_from_filename")

        self.parse_and_generate("linux", keep_module_version=True)

    def _try_set_short_path(self, cwd, long, short):
        from build_migrator.common.win32 import GetShortPathName

        path_long = os.path.join(cwd, long)
        path_short_expected = os.path.join(cwd, short)
        path_short_current = GetShortPathName(path_long)
        if path_short_current != path_short_expected:
            args = ["fsutil", "file", "setshortname", path_long, short]
            try:
                output = subprocess.check_output(args, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                message = (
                    "Unable to set short name, try running command with admin privileges. "
                    + "Command: %r, returncode=%r, output: %r"
                    % (args, e.returncode, e.output.strip())
                )
                self.skipTest(message)

    def test_windows_get_long_path_name(self):
        """
        Check that GetLongPathName wrapper works correctly
        Build log contains short paths (e.g. C:\\PROGR~1\\etc)
        """

        if not self.on_windows():
            self.skipTest("Only Windows is supported")

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("windows_get_long_path_name")

        # Set short paths, if needed
        self._try_set_short_path(
            os.path.join(self.test_method_dir, "build"), "Output Directory", "OUTPUT~1"
        )
        self._try_set_short_path(
            os.path.join(self.test_method_dir, "source"),
            "Source File.cpp",
            "SOURCE~1.CPP",
        )

        self.parse_and_generate("windows", preserve_output_path=True)

    def test_windows_make_log(self):
        """
        Check that flags like -DTEST=\"test\" or "-DTEST=\"test\" " from Makefile logs parse correctly
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("windows_make_log")

        self.parse_and_generate(
            "windows",
            presets=["windows", "autotools", "clang_gcc"],
            tokenizer_ruleset="posix",
        )

    def test_generate_for_files_matching_glob_1(self):
        """
        Check that --targets arguments support path globs
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("generate_for_files_matching_glob_1")

        build_dir = os.path.join(self.test_method_dir, "build")
        globs = ["lib/*.dll", os.path.join(build_dir, "bin/*.exe"), "./README.*"]
        self.parse_and_generate(
            "windows", presets=["windows", "clang_gcc", "autotools"], targets=globs
        )

    def test_generate_for_files_matching_glob_2(self):
        """
        If --targets argument matches a file literally, it won't be evaluated as a glob.
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("generate_for_files_matching_glob_2")

        build_dir = os.path.join(self.test_method_dir, "build")
        globs = [
            "lib/[0-9].dll",
            os.path.join(build_dir, "bin/[0-9].exe"),
            "README.[0-9]",
        ]
        self.parse_and_generate(
            "windows", presets=["windows", "clang_gcc", "autotools"], targets=globs
        )

    def test_generate_for_selected_file_with_empty_build_dir(self):
        """
        Check that --targets supports paths to files that only exist
        in the build logs, not on the filesystem.
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("generate_for_selected_file_with_empty_build_dir")

        build_dir = os.path.join(self.test_method_dir, "build")
        targets = ["app.exe", os.path.join(build_dir, "shared.dll"), "static.lib"]
        self.parse_and_generate(
            "windows", presets=["windows", "clang_gcc", "autotools"], targets=targets
        )

    def test_dir_mismatch_in_make_log(self):
        """
        Check that mismatched "Entering"/"Leaving" messages do not break the parser.
        ICU (via cygwin) shows such behavior on Windows. If parser starts to treat
        mismatched "Leaving" message as error, or will pop the directory stack,
        we won't be able to parse ICU logs correctly.
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("dir_mismatch_in_make_log")

        self.parse_and_generate(
            "windows", presets=["windows", "autotools"], tokenizer_ruleset="posix"
        )

    def test_tab_in_flag(self):
        """
        Check that flags like -DA="1\t2" can be processed correctly
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("tab_in_flag")

        self.parse_and_generate("linux", log_type="make")

    def _test_command_substitution(self, **kwargs):
        """
        Check that command substition works correctly
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("command_substitution")

        self.parse_and_generate("linux", log_type="make", **kwargs)

    def test_command_substitution_enabled(self, **kwargs):
        self._test_command_substitution(
            cmakelists_name="CMakeLists_enabled.txt", command_substitution=True
        )

    def test_command_substitution_disabled(self, **kwargs):
        self._test_command_substitution(
            cmakelists_name="CMakeLists_disabled.txt", command_substitution=False
        )

    def test_object_files_with_same_name(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("object_files_with_same_name")

        self.parse_and_generate("linux")

    def test_msvc_skip_toolchain_warnings(self):
        """
        Generate CMakeLists.txt for all toolchain parts with possible warnings in log for MSVC
        """

        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("msvc_skip_toolchain_warnings")

        self.parse_and_generate("windows")

    def test_object_target_optimization_v2_msvc1(self, **kwargs):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("object_target_optimization_msvc1")

        self.parse_and_generate(
            "windows", cmakelists_name="CMakeLists_v2.txt", flag_optimizer_ver="2"
        )

    def test_object_target_optimization_v2_msvc2(self, **kwargs):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("object_target_optimization_msvc2")

        self.parse_and_generate(
            "windows", cmakelists_name="CMakeLists_v2.txt", flag_optimizer_ver="2"
        )

    def test_object_target_optimization_v2_gcc1(self, **kwargs):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("object_target_optimization_gcc1")

        self.parse_and_generate(
            "linux", cmakelists_name="CMakeLists_v2.txt", flag_optimizer_ver="2"
        )

    def test_object_target_optimization_v2_gcc2(self, **kwargs):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("object_target_optimization_gcc2")

        self.parse_and_generate(
            "linux", cmakelists_name="CMakeLists_v2.txt", flag_optimizer_ver="2"
        )

    def test_glob_with_multiple_build_dirs(self):
        """
        Check that --target <glob> supports multiple build dirs
        """

        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("glob_with_multiple_build_dirs")

        self.parse_and_generate("linux", targets=["main1", "main2", "data/*.dat"])

    def test_optimizer_v2_ignore_system_link_libs_msvc(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("optimizer_v2_ignore_system_link_libs_msvc")

        self.parse_and_generate("windows", flag_optimizer_ver="2")

    def test_clang_multiarch(self):
        on_linux = not self.on_windows() and not self.on_darwin()
        if on_linux:
            self.skipTest("Clang on Linux (Ubuntu) doesn't support -arch argument")

        if not self.has_clang:
            self.skipTest("Clang not found in PATH")

        if self.clang_version < (8, 0, 0):
            self.skipTest("Clang version must be at least 8.0.0")

        self.set_test_data_subdir("clang_multiarch")

        self.parse_and_generate("darwin")

    def test_gcc_collect_files_for_arch(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("gcc_collect_files_for_arch")

        self.parse_and_generate("linux")

    def test_gcc_exclude_libs(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("gcc_exclude_libs")

        self.parse_and_generate("linux", keep_flags=[".+"])

    def test_msbuild_without_mp(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("msbuild_without_mp")

        self.parse_and_generate(
            "windows",
            log_type="msbuild",
            path_aliases=[
                [
                    r"C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\CL.exe",
                    "cl.exe",
                ],
                [
                    r"C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\bin\rc.exe",
                    "rc.exe",
                ],
                [
                    r"C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\Lib.exe",
                    "lib.exe",
                ],
            ],
        )

    def test_multiple_msbuild_logs(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("multiple_msbuild_logs")

        self.parse_and_generate(
            "windows",
            log_type="msbuild",
            path_aliases=[
                [
                    r"C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\CL.exe",
                    "cl.exe",
                ],
                [
                    r"C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\bin\rc.exe",
                    "rc.exe",
                ],
                [
                    r"C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\Lib.exe",
                    "lib.exe",
                ],
            ],
            flag_optimizer_ver="2",
            keep_flags=["."],
            delete_flags=[r"^/Fd"],
        )

    def test_redirection(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("redirection")

        self.parse_and_generate("linux")

    def test_wl_z_flag(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("wl_z_flag")

        self.parse_and_generate("linux", keep_flags=["."])

    def test_filter_wl_z_flag(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("wl_z_flag")

        self.parse_and_generate(
            "linux",
            cmakelists_name="CMakeLists_filtered.txt",
            keep_flags=["."],
            delete_flags=["relro"],
        )

    def test_rpath_flag_variations(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("rpath_flag_variations")

        self.parse_and_generate("linux", keep_flags=["."], flag_optimizer_ver="2")

    def test_filter_rpath_flag_variations(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("rpath_flag_variations")

        self.parse_and_generate(
            "linux",
            cmakelists_name="CMakeLists_filtered.txt",
            flag_optimizer_ver="2",
            keep_flags=["."],
            delete_flags=["-rpath"],
        )

    def test_use_object_file_in_cmd(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("use_object_file_in_cmd")

        self.parse_and_generate(
            "linux",
            extra_targets=[
                get_command_target(
                    "a1_o",
                    "copy_a_o",
                    ["@build_dir@/a.o", "@build_dir@/a1.o"],
                    "@build_dir@/a1.o",
                    dependencies=["@build_dir@/a.o"],
                ),
                get_command_target(
                    "b1_o",
                    "copy_a_o",
                    ["@build_dir@/b.o", "@build_dir@/b1.o"],
                    "@build_dir@/b1.o",
                    dependencies=["@build_dir@/b.o"],
                ),
            ],
        )

    def test_use_object_file_in_cmd_implicit(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("use_object_file_in_cmd")

        self.parse_and_generate(
            "linux",
            cmakelists_name="CMakeLists_implicit.txt",
            extra_targets=[
                get_command_target(
                    "a1_o",
                    "use_a_o_implicitly",
                    ["@build_dir@/a1.o"],
                    "@build_dir@/a1.o",
                    dependencies=["@build_dir@/a.o"],
                ),
                get_command_target(
                    "b1_o",
                    "use_a_o_implicitly",
                    ["@build_dir@/b1.o"],
                    "@build_dir@/b1.o",
                    dependencies=["@build_dir@/b.o"],
                ),
            ],
        )

    def test_cmd_depends_on_source(self):
        self.set_test_data_subdir("cmd_depends_on_source")

        self.parse_and_generate(
            "linux",
            extra_targets=[
                get_command_target(
                    "b.c",
                    "copy_source",
                    ["@source_dir@/a.c", "@build_dir@/b.c"],
                    "@build_dir@/b.c",
                    dependencies=["@source_dir@/a.c"],
                )
            ],
        )

    def test_ignore_flags_windows(self):
        """
        Ignore compiler/linker flags that may introduce unwanted dependencies
        --delete-flags is applied after dependency resolution, so it's not
        applicable here
        Windows toolchain
        """
        if not (self.has_msvc and self.has_nasm and self.has_yasm):
            self.skipTest("MSVC or NASM or YASM not found in PATH")

        self.set_test_data_subdir("ignore_flags_windows")

        self.parse_and_generate(
            "windows",
            ignore_compile_flags=["-DIGNORE", "[/-]Iignore"],
            ignore_link_flags=["/machine:6510"],
            keep_flags=["."],
        )

    def test_ignore_flags_linux(self):
        """
        Ignore compiler/linker flags that may introduce unwanted dependencies
        --delete-flags is applied after dependency resolution, so it's not
        applicable here
        Linux toolchain
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("ignore_flags_linux")

        self.parse_and_generate(
            "linux",
            ignore_compile_flags=["-DIGNORE", "-Iignore"],
            ignore_link_flags=["-m256"],
            keep_flags=["."],
        )

    def test_msbuild_sqlite(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("msbuild_sqlite")

        self.parse_and_generate("windows", log_type="msbuild")

    def test_msbuild_libjson(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("msbuild_libjson")

        self.parse_and_generate(
            "windows",
            log_type="msbuild",
            ignore_compile_flags=[".+Program Files"],
            keep_flags=["[-/]M", "[-/]D_MBCS", "[-/]DJSON_UNICODE", "[-/]Zc:"],
            flag_optimizer_ver="2",
            preserve_output_path=True,
        )

    def test_multiple_object_targets_with_same_path(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("multiple_object_targets_with_same_path")

        self.parse_and_generate("linux", log_type="make", flag_optimizer_ver="2")

    def test_gcc_artifacts_in_subdir(self):
        """
        Make sure that directory targets don't end up in generated CMakeLists.txt if we don't need them
        """
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("gcc_artifacts_in_subdir")

        self.parse_and_generate(
            "linux", log_type="make", targets=["out/*.a", "out/*.so"]
        )

    def test_msvc_artifacts_in_subdir(self):
        """
        Make sure that directory targets don't end up in generated CMakeLists.txt if we don't need them
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("msvc_artifacts_in_subdir")

        self.parse_and_generate(
            "windows",
            presets=["windows", "autotools"],
            targets=["out/*.dll", "out/*.lib"],
        )

    def test_path_alias_with_target_filter(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("path_alias_with_target_filter")

        include_a = os.path.normpath(
            os.path.join(self.test_method_dir, "include/a")
        ).replace("\\", "/")
        include_b = os.path.normpath(
            os.path.join(self.test_method_dir, "include/b")
        ).replace("\\", "/")
        include_c = os.path.normpath(
            os.path.join(self.test_method_dir, "include/c")
        ).replace("\\", "/")
        include_d = os.path.normpath(
            os.path.join(self.test_method_dir, "include/d")
        ).replace("\\", "/")
        lib_a = os.path.normpath(
            os.path.join(self.test_method_dir, "lib/liba.a")
        ).replace("\\", "/")
        lib_b = os.path.normpath(
            os.path.join(self.test_method_dir, "lib/libb.a")
        ).replace("\\", "/")
        lib_c = os.path.normpath(
            os.path.join(self.test_method_dir, "lib/libc.a")
        ).replace("\\", "/")
        lib_d = os.path.normpath(
            os.path.join(self.test_method_dir, "lib/libd.a")
        ).replace("\\", "/")
        self.parse_and_generate(
            "linux",
            path_aliases=[
                [include_a, "@EXTERNAL_INCLUDE_A@"],
                [include_b, "@EXTERNAL_INCLUDE_B@"],
                [include_c, "@EXTERNAL_INCLUDE_C@"],
                [include_d, "@EXTERNAL_INCLUDE_D@"],
                [lib_a, "@EXTERNAL_LIB_A@"],
                [lib_b, "@EXTERNAL_LIB_B@"],
                [lib_c, "@EXTERNAL_LIB_C@"],
                [lib_d, "@EXTERNAL_LIB_D@"],
            ],
            default_var_values=[
                ["EXTERNAL_INCLUDE_A", "@build_dir@/include/a"],
                ["EXTERNAL_INCLUDE_B", "@build_dir@/include/b"],
                ["EXTERNAL_INCLUDE_C", "@build_dir@/include/c"],
                ["EXTERNAL_INCLUDE_D", "@build_dir@/include/d"],
                ["EXTERNAL_LIB_A", "external.a.static"],
                ["EXTERNAL_LIB_B", "external.b.static"],
                ["EXTERNAL_LIB_C", "external.c.static"],
                ["EXTERNAL_LIB_D", "external.d.static"],
            ],
            flag_optimizer_ver="2",
            targets=["test1", "test2", "test3"],
        )
        
    def test_path_alias_rpath_gcc(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("path_alias_rpath_gcc")

        self.parse_and_generate(
            "linux",
            path_aliases=[
                ["/some/path", "@RPATH_PATH_ROOT@"],
            ]
        )

    def test_path_alias_def_msvc(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("path_alias_def_msvc")
        
        path = os.path.normpath(os.path.join(self.test_method_dir, "external")).replace(
            "\\", "/"
        )

        self.parse_and_generate(
            "windows",
            path_aliases=[
                [path, "@DEF_FILE_ROOT@"],
            ],
            default_var_values=[
                ["DEF_FILE_ROOT", "some_path_to_external_dir"]
            ]
        )

    def test_variable_dependency_1(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("variable_dependency_1")

        zlib_include_dir = os.path.normpath(
            os.path.join(self.test_method_dir, "source/zlib/include")
        ).replace("\\", "/")
        self.parse_and_generate(
            "linux",
            path_aliases=[[zlib_include_dir, "@ZLIB_INCLUDE_DIR@"]],
            default_var_values=[["ZLIB_INCLUDE_DIR", "@source_dir@/zlib/include"]],
            flag_optimizer_ver="2",
            aggressive_optimization=True,
            targets=["t1", "t2", "t3", "t4", "t5"],
        )

    @unittest.skip("Bug: C flags are lost")
    def test_variable_dependency_2(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("variable_dependency_2")

        self.parse_and_generate(
            "linux",
            flag_optimizer_ver="2",
            aggressive_optimization=True,
            targets=["t1", "t2", "t3", "t4", "t5", "t6"],
        )

    def test_variable_dependency_3(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("variable_dependency_3")

        self.parse_and_generate(
            "linux",
            flag_optimizer_ver="2",
            aggressive_optimization=True,
            targets=["t1", "t2", "t3", "t4", "t5", "t6", "t7"],
        )

    def test_msvc_mc(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("msvc_mc")

        self.parse_and_generate(
            "windows",
            presets=["windows", "autotools"],
            targets=["main"],
            flag_optimizer_ver="2",
        )

    def test_generate_for_object_library(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("generate_for_object_library")

        self.parse_and_generate(
            "windows", presets=["windows", "autotools"], targets=["out/a.obj"]
        )

    def test_filter_include_dirs_keep_flags(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("filter_include_dirs")

        self.parse_and_generate(
            "linux",
            log_type="make",
            cmakelists_name="CMakeLists1.txt",
            flag_optimizer_ver="2",
            keep_flags=["^-I.+a/b/c/"],
        )

    def test_filter_include_dirs_delete_flags(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("filter_include_dirs")

        self.parse_and_generate(
            "linux",
            log_type="make",
            cmakelists_name="CMakeLists2.txt",
            flag_optimizer_ver="2",
            delete_flags=["/usr/"],
        )

    def test_filter_include_dirs_replace_flags(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("filter_include_dirs")

        self.parse_and_generate(
            "linux",
            log_type="make",
            cmakelists_name="CMakeLists3.txt",
            flag_optimizer_ver="2",
            replace_flags=[["include", "dir"]],
        )

    def test_gcc_windows(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("gcc_windows")

        self.parse_and_generate(
            "windows",
            presets=["windows", "autotools", "clang_gcc"],
            cmakelists_name="CMakeLists.txt",
            flag_optimizer_ver="2",
        )

    def test_msvc_cl_link_flags(self):
        """
        cl.exe: link directly, pass linker options via /link flag
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("msvc_cl_link_flags")

        self.parse_and_generate(
            "windows", presets=["windows", "autotools"], flag_optimizer_ver="2",
        )

    def test_object_lib_depends_on_custom_command(self):
        """
        source/common.cpp depends on generated/manifest.h,
        which is generated by mc.exe
        This dependency should be reflected in generated CMakeLists.txt
        """
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("object_lib_depends_on_custom_command")

        self.parse_and_generate(
            "windows",
            presets=["windows", "autotools"],
            cmakelists_name="CMakeLists.txt",
            flag_optimizer_ver="2",
            targets=["a", "b"],
        )

    def test_sqlite(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("sqlite")

        self.parse_and_generate(
            "linux",
            log_type="make",
            flag_optimizer_ver="2",
            targets=["sqlite3", "sqlite3.static", "sqlite3.0.8.6"],
            replace_line=[
                [r"^libtool: \w+: ", ""],
                [r"(^| )[^ ]+/compile", ""],
                [r"(^| )/bin/bash", ""],
                [r"(^| )[^ ]+/depcomp", ""],
                [r"(^| )\./libtool", ""],
                [r"--tag=CC", ""],
                [r"--mode=compile", ""],
                [
                    r"/opt/aurora/tooling/opt/cross/bin/armv7hl-meego-linux-gnueabi-gcc",
                    "gcc",
                ],
            ],
            command_substitution=True,
        )

    def test_install_name_with_symlink(self):
        """
        -install_name argument points to a file created via symlink.
        """
        if not self.has_clang:
            self.skipTest("Clang not found in PATH")

        self.set_test_data_subdir("install_name_with_symlink")

        self.parse_and_generate(
            "darwin",
            presets=["darwin", "autotools"],
            parsers=["cmake"],
            flag_optimizer_ver="2",
            keep_flags=["."],
        )

    def test_prebuilt_and_source_files_have_same_relpath_invalid_config(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("prebuilt_and_source_files_have_same_relpath")

        self.assertRaisesRegexp(
            ValueError,
            "prebuilt_subdir cannot be the same as source_subdir",
            self.parse_and_generate,
            "linux",
            presets=["linux", "autotools"],
            source_subdir=".",
            prebuilt_subdir=".",
        )

    def test_prebuilt_and_source_files_have_same_relpath_with_default_config(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("prebuilt_and_source_files_have_same_relpath")

        self.parse_and_generate(
            "linux",
            presets=["linux", "autotools"],
            source_subdir="source",
            prebuilt_subdir="prebuilt",
        )

        prebuilt_dir = os.path.join(self.test_method_out_dir, "out/prebuilt")
        source_dir = os.path.join(self.test_method_out_dir, "out/source")

        path = os.path.join(prebuilt_dir, "a.c")
        self.assertTrue(os.path.exists(path), path)
        with open(path) as f:
            self.assertEqual(f.read(), "// build")

        path = os.path.join(source_dir, "a.c")
        self.assertTrue(os.path.exists(path), path)
        with open(path) as f:
            self.assertEqual(f.read(), "// source")

    def test_dont_capture_source(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("prebuilt_and_source_files_have_same_relpath")

        self.parse_and_generate(
            "linux",
            presets=["linux", "autotools"],
            source_subdir="source",
            prebuilt_subdir="prebuilt",
            dont_capture_sources=True,
        )

        prebuilt_dir = os.path.join(self.test_method_out_dir, "out/prebuilt")
        source_dir = os.path.join(self.test_method_out_dir, "out/source")

        path = os.path.join(prebuilt_dir, "a.c")
        self.assertTrue(os.path.exists(path), path)
        with open(path) as f:
            self.assertEqual(f.read(), "// build")

        path = os.path.join(source_dir, "a.c")
        self.assertFalse(os.path.exists(path), path)

    def test_zlib_darwin(self):
        if not self.has_clang:
            self.skipTest("Clang not found in PATH")

        replace_line = None
        ignore_flags = None
        if not self.on_darwin():
            if not self.has_gcc:
                self.skipTest("GCC not found in PATH")
            replace_line = [(" clang ", " gcc ")]
            ignore_flags = [r"-mmacosx-version-min=", r"-arch ", r"-isysroot "]
        else:
            ignore_flags = [r"-isysroot "]

        self.set_test_data_subdir("zlib/darwin")

        self.parse_and_generate(
            "darwin",
            add_presets=False,
            presets=["darwin", "ninja"],
            replace_line=replace_line,
            project="zlib",
            project_version="1.2.11",
            prebuilt_subdir="darwin",
            build_condition='CMAKE_SYSTEM_NAME STREQUAL "Darwin"',
            targets=["z.static", "z"],
            source_dir=os.path.join(self.test_method_dir, "../source"),
            ignore_compile_flags=ignore_flags,
            ignore_link_flags=ignore_flags,
            keep_flags=["^-D"],
            source_subdir="source",
        )

    def test_zlib_linux(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("zlib/linux")

        self.parse_and_generate(
            "linux",
            add_presets=False,
            presets=["linux", "ninja"],
            project="zlib",
            project_version="1.2.11",
            prebuilt_subdir="linux",
            build_condition='CMAKE_SYSTEM_NAME STREQUAL "Linux"',
            targets=["z.static", "z"],
            source_dir=os.path.join(self.test_method_dir, "../source"),
            keep_flags=["^-D", "^-Wl,--version-script", "^-Wl,-soname,libz.so"],
            delete_flags=["^-DNDEBUG$"],
            source_subdir="source",
        )

    def test_zlib_windows(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("zlib/windows")

        self.parse_and_generate(
            "windows",
            add_presets=False,
            presets=["windows", "ninja"],
            project="zlib",
            project_version="1.2.11",
            prebuilt_subdir="windows",
            build_condition='CMAKE_SYSTEM_NAME STREQUAL "Windows"',
            targets=["zlib1", "zlib.static", "zlib1mt", "zlibmt.static"],
            source_dir=os.path.join(self.test_method_dir, "../source"),
            keep_flags=["^-D"],
            delete_flags=["^-D_", "^-DNDEBUG", "^-DNTDDI_VERSION", "^-DWIN32"],
            replace_line=[
                (r"print-response-file-cl.bat", "cl.exe"),
                (r"C:.*cmake.exe.*link\.exe", "link.exe"),
                ("C:.*cmcldeps.exe.*zlib1.rc.*C:.*rc.exe", "rc.exe"),
                (r"^cl : ", ""),
                (r"^LINK : ", ""),
            ],
            ignore_compile_flags=[r"^/FS$"],  # vs10 doesn't support this flag
            source_subdir="source",
        )

    def test_openssl_darwin(self):
        if not self.has_clang:
            self.skipTest("Clang not found in PATH")

        replace_line = None
        ignore_flags = None
        if not self.on_darwin():
            if not self.has_gcc:
                self.skipTest("GCC not found in PATH")
            replace_line = [
                ("clang ", " gcc "),
                (r"clang\+\+ ", " g++ "),
            ]
            ignore_flags = [
                r"-mmacosx-version-min=",
                r"-arch ",
                r"-isysroot",
            ]
        else:
            ignore_flags = [r"-isysroot "]

        self.set_test_data_subdir("openssl/darwin")

        self.parse_and_generate(
            "darwin",
            add_presets=False,
            presets=["darwin", "autotools"],
            replace_line=replace_line,
            project="openssl",
            project_version="1.1.1",
            prebuilt_subdir="darwin",
            build_condition='CMAKE_SYSTEM_NAME STREQUAL "Darwin"',
            targets=["openssl"],
            source_dir=os.path.join(self.test_method_dir, "../source"),
            ignore_compile_flags=ignore_flags,
            ignore_link_flags=ignore_flags,
            keep_flags=[
                "^-D",
                "^-fPIC",
                "^-current_version",
                "^-compatibility_version",
            ],
            delete_flags=["^-D_", "^-DNDEBUG"],
            replace_flags=[
                (r"^(-DENGINESDIR)=.+$", r'\g<1>="."'),
                (r"^(-DOPENSSLDIR)=.+$", r'\g<1>="/usr/local/ssl"'),
            ],
            source_subdir="source",
        )

        root = os.path.join(self.test_method_out_dir, "out/source")
        for curdir, _, files in os.walk(root):
            for f in files:
                expected = os.path.join(
                    self.test_method_dir, "../source", os.path.relpath(curdir, root), f
                )
                result = os.path.join(curdir, f)
                self.assertFilesEqualBinary(expected, result)

        opensslconf_h_checked = True
        root = os.path.join(self.test_method_out_dir, "out/prebuilt")
        for curdir, _, files in os.walk(root):
            for f in files:
                if f == "opensslconf.h":
                    opensslconf_h_checked = True
                expected = os.path.join(
                    self.test_method_dir, "build", os.path.relpath(curdir, root), f
                )
                result = os.path.join(curdir, f)
                self.assertFilesEqualBinary(expected, result)

        self.assertTrue(opensslconf_h_checked)

    def test_openssl_linux(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("openssl/linux")

        self.parse_and_generate(
            "linux",
            add_presets=False,
            presets=["linux", "autotools"],
            project="openssl",
            project_version="1.1.1",
            prebuilt_subdir="linux",
            build_condition='CMAKE_SYSTEM_NAME STREQUAL "Linux"',
            targets=["openssl"],
            source_dir=os.path.join(self.test_method_dir, "../source"),
            ignore_compile_flags=["^-m64$", "^-fstack-protector-strong"],
            ignore_link_flags=["^-m64$", "^-fstack-protector-strong"],
            keep_flags=[
                "^-D",
                "^-Wa,--noexecstack",
                "^-fno-exceptions",
                "^-fno-rtti",
                "^-Wl,-z",
                "^-static-",
                "^-fPIC$",
                "^-pthread$",
                "^-Wl,--version-script=",
            ],
            delete_flags=["^-D_", "^-DNDEBUG"],
            replace_flags=[
                (r"^(-DENGINESDIR)=.+$", r'\g<1>="."'),
                (r"^(-DOPENSSLDIR)=.+$", r'\g<1>="/usr/local/ssl"'),
            ],
            source_subdir="source",
        )

        root = os.path.join(self.test_method_out_dir, "out/source")
        for curdir, _, files in os.walk(root):
            for f in files:
                expected = os.path.join(
                    self.test_method_dir, "../source", os.path.relpath(curdir, root), f
                )
                result = os.path.join(curdir, f)
                self.assertFilesEqualBinary(expected, result)

        opensslconf_h_checked = True
        root = os.path.join(self.test_method_out_dir, "out/prebuilt")
        for curdir, _, files in os.walk(root):
            for f in files:
                if f == "opensslconf.h":
                    opensslconf_h_checked = True
                expected = os.path.join(
                    self.test_method_dir, "build", os.path.relpath(curdir, root), f
                )
                result = os.path.join(curdir, f)
                self.assertFilesEqualBinary(expected, result)

        self.assertTrue(opensslconf_h_checked)

    def test_openssl_windows(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("openssl/windows")

        self.parse_and_generate(
            "windows",
            add_presets=False,
            presets=["windows", "autotools"],
            project="openssl",
            project_version="1.1.1",
            prebuilt_subdir="windows",
            build_condition='CMAKE_SYSTEM_NAME STREQUAL "Windows"',
            targets=["openssl"],
            source_dir=os.path.join(self.test_method_dir, "../source"),
            keep_flags=[
                "^-D",
                "-fwin32",
                "-Gw",
                "-Zc:threadSafeInit-",
                "-arch:",
                "/GL",
                "/bigobj",
            ],
            delete_flags=["^-D_", "^-DNDEBUG$", "^-DUNICODE$"],
            replace_flags=[
                (r"^(-DENGINESDIR)=.+$", r'\g<1>="."'),
                (
                    r"^(-DOPENSSLDIR)=.+$",
                    r'\g<1>="C:\\Program Files\\Common Files\\SSL"',
                ),
            ],
            source_subdir="source",
        )

        root = os.path.join(self.test_method_out_dir, "out/source")
        for curdir, _, files in os.walk(root):
            for f in files:
                expected = os.path.join(
                    self.test_method_dir, "../source", os.path.relpath(curdir, root), f
                )
                result = os.path.join(curdir, f)
                self.assertFilesEqualBinary(expected, result)

        opensslconf_h_checked = True
        root = os.path.join(self.test_method_out_dir, "out/prebuilt")
        for curdir, _, files in os.walk(root):
            for f in files:
                if f == "opensslconf.h":
                    opensslconf_h_checked = True
                expected = os.path.join(
                    self.test_method_dir, "build", os.path.relpath(curdir, root), f
                )
                result = os.path.join(curdir, f)
                self.assertFilesEqualBinary(expected, result)

        self.assertTrue(opensslconf_h_checked)

    def test_electron(self):
        if not (
            self.has_msvc and self.has_clang_cl and self.has_nasm and self.has_yasm
        ):
            self.skipTest("MSVC or clang-cl or NASM or YASM not found in PATH")

        self.set_test_data_subdir("electron")

        source_dir = os.path.join(self.test_method_out_dir, "source")
        build_dir = os.path.join(source_dir, "out/Release-x86")

        # make a copy of source directory, because we're going to modify files
        shutil.copytree(os.path.join(self.test_method_dir, "source"), source_dir)

        # ui_unscaled_resources.rc should contain **full** paths to includes
        source_dir_native = source_dir.replace("\\", r"\\").replace("/", r"\\")
        self.replace_file_content(
            os.path.join(build_dir, "gen/ui/resources/ui_unscaled_resources.rc"),
            "@source_dir@",
            source_dir_native,
            "utf-16-le",
        )

        header = os.path.join(self.test_method_dir, "user_code/header.cmake")
        footer = os.path.join(self.test_method_dir, "user_code/footer.cmake")
        self.parse_and_generate(
            "windows",
            presets=["windows", "ninja"],
            source_dir=source_dir,
            build_dirs=[build_dir],
            user_code_headers=[header],
            user_code_footers=[footer],
            working_dir=source_dir,
            build_condition='CMAKE_SYSTEM_NAME STREQUAL "Windows"',
            delete_flags=[
                "^-DNTDDI_VERSION=",
                "^-D_WIN32_WINNT=",
                "^-DNDEBUG",
                "[-/]MT",
                "[-/]MD",
            ],
            flag_optimizer_ver=2,
            aggressive_optimization=True,
            file_target_change_encodings=[
                ("*/ui_unscaled_resources.rc", "utf-16-le", "utf-8")
            ],
            file_target_gsubs=[
                ("*.c", '#include "../../', '#include "'),
                ("*.cc", '#include "../../', '#include "'),
                (
                    "*/ui_unscaled_resources.rc",
                    r'"[^"]+.test_parse_and_generate\\\\electron\\\\source',
                    '"@ELECTRON_SOURCE_DIR_NATIVE@',
                ),
            ],
            keep_flags=[
                "^-m",
                r"^-Wno-c\+\+11-narrowing$",
                "^-Wno-nonportable-include-path",
                "^-Wno-nonportable-include-path",
                "^-Wno-microsoft-include",
                "^-Wno-unused-const-variable",
                "^-Wno-deprecated-declarations",
                "^-Wno-unused-variable",
                "^-Wno-unused-function",
                "^-Wno-deprecated-declarations",
                "^-Wno-ignored-pragma-optimize",
                "^-Wno-inconsistent-missing-override",
                "^-Wno-missing-braces",
                "/OPT",
                "/INCREMENTAL",
                "/FIXED",
                "/largeaddressaware",
                "/fastfail",
                "/llvmlibthin",
                "/NXCOMPAT",
                "/DYNAMICBASE",
                "/SUBSYSTEM",
                "^-fmsc-version",
                "^[/-]Oi$",
                "^[-/]DELAYLOAD:",
                "^[-/]MANIFESTUAC",
                "^-fcomplete-member-pointers",
                "^[-/]bigobj",
                "^-D",
                "(?i)^[-/]arch:",
                "(?i)^/safeseh$",
                "^[-/]GL",
                "^[-/]GR",
                "^[-/]Gw",
                "^[-/]Zc:",
                "^-P",
                r"^-W\+error",
                "^-fwin32",
            ],
            ignore_compile_flags=[r"(?i)(.*c:[/\\]program files.*|^/X$|^/Brepro$)"],
            ignore_link_flags=[r"(?i).*c:[/\\]program files.*"],
            preserve_output_path=True,
            project="electron",
            project_version="5.0.5",
            replace_line=[
                ("-Xclang -add-plugin -Xclang blink-gc-plugin ", ""),
                ("-Xclang -add-plugin -Xclang find-bad-constructs ", ""),
                ("C:/Python27/python.exe ../../build/gn_run_binary.py ", ""),
                (
                    "C:/Python27/python.exe ../../build/toolchain/win/tool_wrapper.py asm-wrapper environment.x86 C:/Python27/python.exe ../../build/toolchain/win/ml.py ",
                    "",
                ),
                (
                    "C:/Python27/python.exe ../../build/toolchain/win/tool_wrapper.py rc-wrapper environment.x86 ",
                    "",
                ),
                ("C:/Python27/python.exe ../../third_party/yasm/run_yasm.py ./", ""),
                ("ninja -t msvc -e environment.x86 -- ", ""),
            ],
            targets=[
                "locales",
                "resources",
                "swiftshader/libEGL.dll",
                "swiftshader/libGLESv2.dll",
                "chrome_100_percent.pak",
                "chrome_200_percent.pak",
                "d3dcompiler_47.dll",
                "electron.dll",
                "ffmpeg.dll",
                "icudtl.dat",
                "libEGL.dll",
                "libGLESv2.dll",
                "natives_blob.bin",
                "resources.pak",
                "snapshot_blob.bin",
                "v8_context_snapshot.bin",
            ],
            source_subdir="source",
        )

        out_dir = os.path.join(self.test_method_out_dir, "out", "prebuilt")
        path = os.path.join(out_dir, "icudtl.dat")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(out_dir, "d3dcompiler_47.dll")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(out_dir, "locales", "en-gb.pak")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(out_dir, "locales", "zh-tw.pak.info")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(out_dir, "resources", "default_app.asar")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(out_dir, "resources/inspector/.htaccess")
        self.assertTrue(os.path.exists(path), path)
        path = os.path.join(
            out_dir, "resources/inspector/accessibility/ariaproperties.js"
        )
        self.assertTrue(os.path.exists(path), path)

        # Check modified file content (--file_target_gsub, --convert_encoding)
        definitions = [
            ("gen/base/base_jumbo_7.cc", "base_jumbo_7.cc"),
            ("gen/base/base_jumbo_c.c", "base_jumbo_c.c"),
            ("gen/ui/resources/ui_unscaled_resources.rc", "ui_unscaled_resources.rc"),
        ]
        for result, expected in definitions:
            result_file = os.path.join(out_dir, result)
            expected_file = os.path.join(self.test_method_dir, "files", expected)
            self.assertFilesEqual(expected_file, result_file)

    def test_icu_darwin(self):
        if not self.has_clang:
            self.skipTest("Clang not found in PATH")

        self.set_test_data_subdir("icu/darwin")

        replace_line = []
        ignore_flags = []
        if not self.on_darwin():
            if not self.has_gcc:
                self.skipTest("GCC not found in PATH")
            replace_line = [
                ("clang ", " gcc "),
                (r"clang\+\+ ", " g++ "),
            ]
            ignore_flags = [r"-mmacosx-version-min=", r"-arch "]

        self.parse_and_generate(
            "darwin",
            add_presets=False,
            presets=["darwin", "autotools", "icu"],
            project="icu",
            project_version="58.2",
            source_dir=os.path.join(self.test_method_dir, "../source"),
            flag_optimizer_ver=2,
            aggressive_optimization=True,
            keep_module_version=True,
            target_order=["."],
            replace_line=replace_line
            + [
                # remove messages from pkgdata
                (r"^pkgdata:.+$", ""),
            ],
            # Keep all flags by default
            keep_flags=[".+"],
            delete_flags=[
                r"^[-/]DDEFAULT_ICU_PLUGINS",
                r"^[-/]DU_ICU_DATA_DEFAULT_DIR=",
                r"^[-/]D_",
                r"^[-/]DU_RELEASE",
                r"^[-/]DU_BUILD=",
                r"^[-/]DU_CC=",
                r"^[-/]DU_CXX=",
                r"^[-/]DU_HOST=",
                r"^[-/]DNDEBUG",
                r"^[-/]O",
                r"^[-/]W$",
                r"^[-/]W(?!l,).+",
                "^-arch",
                "^-fPIC",
                "^-fstack",
                "^-pedantic",
                "^--?std",
                "^-Wl,-search_paths_first",
                "^-mptr64",
                "^-march=",
                "^-isysroot ",
                "^-mmacosx-version",
                "^-arch ",
                "^--target=",
            ],
            # There are targets with same filename in different directories (data, stubdata)
            preserve_output_path=True,
            # Rename targets to match other platforms
            # TODO: do the same thing, but without this
            rename_patterns=[
                (r"^sicu(.+)\.static", r"icu\g<1>.static"),
                (r"icu([^\.]+)58$", r"icu\g<1>.58.2"),
                (r"icuin", r"icui18n"),
                (r"icudt", r"icudata"),
            ],
            user_code_headers=[
                os.path.join(self.test_method_dir, "../user_code/header.cmake")
            ],
            path_aliases=[("data/icupkg.inc", "@ICU_BUILD_OPTIONS_FILE@")],
            # Ignore include dirs in Agard build/source root
            ignore_compile_flags=ignore_flags
            + [
                r"^-I(?:/home/builder|/Users/buildadmin)/a/b/[a-z]_[A-Za-z0-9]+_/b/include",
                r"^-I(?:/home/builder|/Users/buildadmin)/a/b/[a-z]_[A-Za-z0-9]+/s/include",
                # Ignore Mac-specific flags
                r"^-isysroot ",
                r"^-mmacosx-version",
                r"^-arch ",
                # Ignore other flags that may break some compilers
                r"^--target=",
                r"^-mptr64",
                r"^-march=",
            ],
            targets=["lib/*.dylib", "stubdata/*.dylib"],
            build_condition='CMAKE_SYSTEM_NAME STREQUAL "Darwin" AND CMAKE_SYSTEM_PROCESSOR STREQUAL "i686"',
            platform="darwin",
            prebuilt_subdir="darwin",
            source_subdir="source",
        )

    def test_icu_windows(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.set_test_data_subdir("icu/windows")

        self.parse_and_generate(
            "windows",
            add_presets=False,
            presets=["windows", "autotools", "icu"],
            project="icu",
            project_version="58.2",
            source_dir=os.path.join(self.test_method_dir, "../source"),
            flag_optimizer_ver=2,
            aggressive_optimization=True,
            keep_module_version=True,
            target_order=["."],
            # Keep all flags by default
            keep_flags=[".+"],
            delete_flags=[
                r"^[-/]DDEFAULT_ICU_PLUGINS",
                r"^[-/]DU_ICU_DATA_DEFAULT_DIR=",
                r"^[-/]D_",
                r"^[-/]DU_RELEASE",
                r"^[-/]DU_BUILD=",
                r"^[-/]DU_CC=",
                r"^[-/]DU_CXX=",
                r"^[-/]DU_HOST=",
                r"^[-/]DNDEBUG",
                r"^[-/]O",
                r"^[-/]W(?!l,).+",
                "[-/]DNTDDI_VERSION=",
                "[-/]DWIN32",
                "[-/]arch:",
                "[-/]MD",
                "[-/]nologo",
                "[-/]machine:",
                "[-/]STACK:",
                "[-/]DEBUG",
                "[-/]INCREMENTAL",
                "[-/]OPT:",
                "[-/]LTCG",
                "[-/]EH",
                "[-/]base:",
            ],
            # There are targets with same filename in different directories (data, stubdata)
            preserve_output_path=True,
            # Rename targets to match other platforms
            force_target_name=[("@build_dir@/lib/icudt58.dll", "icudt58")],
            rename_patterns=[
                (r"^sicu(.+)\.static", r"icu\g<1>.static"),
                (r"icu([^\.]+)58$", r"icu\g<1>.58.2"),
                (r"icuin", r"icui18n"),
                (r"icudt", r"icudata"),
            ],
            user_code_headers=[
                os.path.join(self.test_method_dir, "../user_code/header.cmake")
            ],
            path_aliases=[("data/icupkg.inc", "@ICU_BUILD_OPTIONS_FILE@")],
            ignore_compile_flags=[
                # Ignore invalid include dirs: -I@build_dir@/common/-a-b-d_00000000_-b-include
                r"^-I.+-include$",
            ],
            targets=["lib/*.lib", "lib/*.dll"],
            build_condition='CMAKE_SYSTEM_NAME STREQUAL "Windows" AND CMAKE_SYSTEM_PROCESSOR STREQUAL "x86_64"',
            platform="windows",
            prebuilt_subdir="windows",
            replace_line=[
                # Replace invalid escape sequences (\p) with path separator + char (/p)
                (r"(?=\\)\\([a-zA-Z0-9])", r"/\g<1>"),
                # Don't parse warnings from linker / compiler
                (r"LINK : ", ""),
                (r"cl : ", ""),
                # Remove text before cl.exe/link.exe in lines like
                # "sal.h(2876): note: see previous definition of '__on_failure'cl.exe -D..."
                (r'(?i)^(.*[^\n"])cl.exe ', "cl.exe "),
                (r'(?i)^(.*[^\n"])link.exe ', "link.exe "),
            ],
            # Set command tokenizer mode to posix
            tokenizer_ruleset="posix",
            source_subdir="source",
        )

    def test_icu_linux(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.set_test_data_subdir("icu/linux")

        kwargs = {
            "add_prests": False,
            "presets": ["linux", "autotools", "icu"],
            "project": "icu",
            "project_version": "58.2",
            "source_dir": os.path.join(self.test_method_dir, "../source"),
            "flag_optimizer_ver": 2,
            "aggressive_optimization": True,
            "keep_module_version": True,
            "target_order": ["."],
            "replace_line": [
                # remove messages from pkgdata
                (r"^pkgdata:.+$", ""),
            ],
            # Keep all flags by default
            "keep_flags": [".+"],
            "delete_flags": [
                r"^[-/]DDEFAULT_ICU_PLUGINS",
                r"^[-/]DU_ICU_DATA_DEFAULT_DIR=",
                r"^[-/]D_",
                r"^[-/]DU_RELEASE",
                r"^[-/]DU_BUILD=",
                r"^[-/]DU_CC=",
                r"^[-/]DU_CXX=",
                r"^[-/]DU_HOST=",
                r"^[-/]DNDEBUG",
                r"^[-/]O",
                r"^[-/]W$",
                r"^[-/]W(?!l,).+",
                "^-arch",
                "^-fPIC",
                "^-fstack",
                "^-pedantic",
                "^--?std",
                "^-Wl,-search_paths_first",
                "^-mptr64",
                "^-march=",
                "^-isysroot ",
                "^-mmacosx-version",
                "^-arch ",
                "^--target=",
            ],
            # There are targets with same filename in different directories (data, stubdata)
            "preserve_output_path": True,
            # Rename targets to match other platforms
            # TODO: do the same thing, but without this
            "rename_patterns": [
                (r"^sicu(.+)\.static", r"icu\g<1>.static"),
                (r"icu([^\.]+)58$", r"icu\g<1>.58.2"),
                (r"icuin", r"icui18n"),
                (r"icudt", r"icudata"),
            ],
            "user_code_headers": [
                os.path.join(self.test_method_dir, "../user_code/header.cmake")
            ],
            "path_aliases": [("data/icupkg.inc", "@ICU_BUILD_OPTIONS_FILE@")],
            # Ignore include dirs in Agard build/source root
            "ignore_compile_flags": [
                r"^-I(?:/home/builder|/Users/buildadmin)/a/b/[a-z]_[A-Za-z0-9]+_/b/include",
                r"^-I(?:/home/builder|/Users/buildadmin)/a/b/[a-z]_[A-Za-z0-9]+/s/include",
                # Ignore other flags that may break some compilers
                r"^--target=",
                r"^-mptr64",
                r"^-march=",
            ],
            "build_condition": 'CMAKE_SYSTEM_NAME STREQUAL "Linux" AND CMAKE_SYSTEM_PROCESSOR STREQUAL "x86_64"',
            "platform": "linux",
            "prebuilt_subdir": "linux",
            "source_subdir": "source",
        }

        # Generate single CMakeLists.txt from multiple build logs

        self.parse_and_generate(
            "linux",
            commands=["parse"],
            targets=["lib/*.a"],
            save=os.path.join(self.test_method_out_dir, "icu.pickle"),
            **kwargs
        )

        self.parse_and_generate(
            "linux",
            load=os.path.join(self.test_method_out_dir, "icu.pickle"),
            targets=["lib/*.a", "data/out/*.dat"],
            build_dirs=[os.path.join(self.test_method_dir, "build_data_archive")],
            logs=[os.path.join(self.test_method_dir, "build_data_archive.log.in")],
            **kwargs
        )

    def test_optimizer_v2_with_def_files(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.parse_and_generate(
            "windows",
            presets=["windows", "autotools"],
            flag_optimizer_ver="2",
            aggressive_optimization=True,
        )

    def test_def_file_generated_during_build(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.parse_and_generate(
            "windows",
            presets=["windows", "autotools"],
            flag_optimizer_ver="2",
            prebuilt_subdir="prebuilt",
        )

        target_file = os.path.join(
            self.test_method_out_dir, "out/external/C_/temp/1.def"
        )
        expected_file = os.path.join(self.test_method_dir, "files", "1.def")
        self.assertFilesEqual(expected_file, target_file)

        target_file = os.path.join(
            self.test_method_out_dir, "out/external/X_/a/b/c/2.tmp"
        )
        expected_file = os.path.join(self.test_method_dir, "files", "2.tmp")
        self.assertFilesEqual(expected_file, target_file)

    def test_objcopy(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.parse_and_generate(
            "linux", presets=["linux", "autotools"], flag_optimizer_ver="2"
        )

    def test_objcopy_post_build(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.parse_and_generate(
            "linux", presets=["linux", "autotools"], flag_optimizer_ver="2"
        )

    def test_objcopy_for_object_library(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.parse_and_generate(
            "linux", presets=["linux", "autotools"], flag_optimizer_ver="2"
        )

    def test_objcopy_for_object_library_post_build(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.parse_and_generate(
            "linux", presets=["linux", "autotools"], flag_optimizer_ver="2"
        )

    def test_unknown_gcc_flags(self):
        if not self.has_gcc:
            self.skipTest("GCC not found in PATH")

        self.parse_and_generate(
            "linux", flag_optimizer_ver="2", log_type="make"
        )

    def test_unknown_msvc_flags(self):
        if not self.has_msvc:
            self.skipTest("MSVC not found in PATH")

        self.parse_and_generate(
            "windows", flag_optimizer_ver="2", log_type="make"
        )

    def test_clang_install_name(self):
        if not self.has_clang:
            self.skipTest("Clang not found in PATH")

        self.parse_and_generate("darwin")
