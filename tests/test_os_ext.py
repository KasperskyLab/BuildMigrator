import os
import sys

__module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, __module_dir)
import base  # noqa: E402
import build_migrator.common.os_ext as os_ext  # noqa: E402


class TestOsExtensions(base.TestBase):
    def test_windows_resolve_lib(self):
        lib1 = os_ext.Windows.path_join(
            self.test_group_dir[:-12],
            "test_parse_and_generate/resolve_library_windows/build/shared/libfoo.lib",
        )
        cwd1 = os_ext.Windows.path_join(
            self.test_group_dir[:-12],
            "test_parse_and_generate/resolve_library_windows/build",
        )
        lb_dirs = []
        full_path1 = os_ext.Windows.resolve_lib(lib1, lb_dirs, cwd1)
        assert full_path1, lib1

        if self.on_windows():
            # TODO: os_ext.Windows does should provide case-insensitive path matching on Unix
            lib = os_ext.Windows.path_join(self.test_group_dir, "DIR/a.LIB")
            cwd = os_ext.Windows.path_join(self.test_group_dir, "dir")
            full_path = os_ext.Windows.resolve_lib("a.lib", [], cwd)
            assert full_path, lib

    def test_windows(self):
        self.assertTrue(os_ext.Windows.is_shared_lib("test.dll"))
        self.assertFalse(os_ext.Windows.is_shared_lib("test.lib"))

        self.assertFalse(os_ext.Windows.is_static_lib("test.dll"))
        self.assertTrue(os_ext.Windows.is_static_lib("test.lib"))

        self.assertIsNone(os_ext.Windows.parse_shared_lib("static.lib"))

        descr = os_ext.Windows.parse_shared_lib(
            os_ext.Windows.path_join(self.test_group_dir, "win.shared_lib.dll")
        )
        expected_descr = {
            "module_name": "win.shared_lib",
            "target_name": "win.shared_lib",
            "soname": "win.shared_lib.lib",
            "version": "1.3.0.0" if os.name == "nt" else None,
        }
        self.assertEqual(expected_descr, descr)

        descr = os_ext.Windows.parse_shared_lib("path\\libtest.dll")
        expected_descr = {
            "module_name": "libtest",
            "target_name": "test",
            "soname": "libtest.lib",
            "version": None,
        }
        self.assertEqual(expected_descr, descr)

        self.assertIsNone(os_ext.Windows.parse_executable("static.lib"))

        descr = os_ext.Windows.parse_executable(
            os_ext.Windows.path_join(self.test_group_dir, "win.executable.exe")
        )
        expected_descr = {
            "module_name": "win.executable",
            "target_name": "win.executable",
            "soname": None,
            "version": "1.3.0.0" if os.name == "nt" else None,
        }
        self.assertEqual(expected_descr, descr)

        descr = os_ext.Windows.parse_executable("test.exe")
        expected_descr = {
            "module_name": "test",
            "target_name": "test",
            "soname": None,
            "version": None,
        }
        self.assertEqual(expected_descr, descr)

        self.assertIsNone(os_ext.Windows.parse_static_lib("app.exe"))

        descr = os_ext.Windows.parse_static_lib("path\\libtest.lib")
        expected_descr = {
            "module_name": "libtest",
            "target_name": "test.static",
            "soname": "libtest.lib",
            "version": None,
        }
        self.assertEqual(expected_descr, descr)

        descr = os_ext.Windows.parse_static_lib("path\\test.lib")
        expected_descr = {
            "module_name": "test",
            "target_name": "test.static",
            "soname": "test.lib",
            "version": None,
        }
        self.assertEqual(expected_descr, descr)

        res = os_ext.Windows.resolve_lib(
            "win.shared_lib.lib", [self.test_group_dir], import_lib=True
        )
        expected_res = os_ext.Windows.path_join(
            self.test_group_dir, "win.shared_lib.dll"
        )
        self.assertEqual(expected_res, res)

        res = os_ext.Windows.resolve_lib(
            "win.shared_lib.lib", [self.test_group_dir], import_lib=False
        )
        expected_res = os_ext.Windows.path_join(
            self.test_group_dir, "win.shared_lib.lib"
        )
        self.assertEqual(expected_res, res)

        path = os_ext.Windows.path_join(self.test_group_dir, "win.shared_lib.lib")
        res = os_ext.Windows.resolve_lib(path, [])
        expected_res = os_ext.Windows.path_join(
            self.test_group_dir, "win.shared_lib.lib"
        )
        self.assertEqual(expected_res, res)

        path = os_ext.Windows.path_join(self.test_group_dir, "win.shared_lib.lib")
        res = os_ext.Windows.resolve_lib(path, [], import_lib=True)
        expected_res = os_ext.Windows.path_join(
            self.test_group_dir, "win.shared_lib.dll"
        )
        self.assertEqual(expected_res, res)

        res = os_ext.Windows.resolve_lib("libtest.lib", [self.test_group_dir])
        expected_res = os_ext.Windows.path_join(self.test_group_dir, "libtest.lib")
        self.assertEqual(expected_res, res)

        re = os_ext.Windows.get_program_path_re("cl", "icc")
        self.assertRegex("CL.EXE", re)
        self.assertRegex("cl.exe", re)
        self.assertRegex("cl", re)
        self.assertRegex("path to file\\cl", re)
        self.assertRegex("path to file/cl", re)
        self.assertRegex("toolchain-cl", re)
        self.assertRegex("ICC.EXE", re)
        self.assertRegex("icc.exe", re)
        self.assertRegex("icc", re)
        self.assertRegex("path to file\\icc", re)
        self.assertRegex("path to file/icc", re)
        self.assertRegex("toolchain-icc", re)
        self.assertNotRegex("noticc", re)
        self.assertNotRegex("NOTCL.exe", re)

        self.assertEqual(
            "C:/nul/B.txt", os_ext.Windows.normalize_path("C:\\nul\\B.txt")
        )
        self.assertEqual(
            "C:/nul/b.TXT", os_ext.Windows.normalize_path("C:\\nul\\../nul\\b.TXT")
        )
        self.assertEqual(
            "C:/nul", os_ext.Windows.normalize_path("C:\\nul\\../nul\\././")
        )
        if os.path.exists("C:/Windows"):
            self.assertEqual("C:/Windows", os_ext.Windows.normalize_path("c:\\Windows"))
            self.assertEqual("C:/Windows", os_ext.Windows.normalize_path("C:/windows"))
        self.assertEqual("nul/b/c", os_ext.Windows.normalize_path("./nul/b/c/."))
        self.assertEqual("nul/b", os_ext.Windows.normalize_path("nul//b"))
        self.assertEqual("nul/b", os_ext.Windows.normalize_path("nul\\\\b"))

        self.assertTrue(os_ext.Windows.is_absolute("C:\\temp"))
        self.assertTrue(os_ext.Windows.is_absolute("C://temp"))
        self.assertTrue(os_ext.Windows.is_absolute("\\\\smb_share"))
        self.assertFalse(os_ext.Windows.is_absolute("temp"))
        self.assertFalse(os_ext.Windows.is_absolute("\\temp"))

        if not self.on_windows():
            # generate for windows on unix
            self.assertEqual(
                "/usr\\temp", os_ext.Windows.path_join(".", "/usr", "temp")
            )
            self.assertEqual(
                "C:\\", os_ext.Windows.path_join(".", "/usr", "temp", "C:\\")
            )
        self.assertEqual("C:\\temp", os_ext.Windows.path_join("C:", "temp"))
        self.assertEqual("C:\\temp\\", os_ext.Windows.path_join("C:\\", "\\temp\\"))
        self.assertEqual(
            "\\\\smb_share\\temp", os_ext.Windows.path_join("\\\\smb_share", "temp")
        )
        self.assertEqual(
            "\\\\smb_share\\temp",
            os_ext.Windows.path_join("C:", "\\\\smb_share", "temp"),
        )
        self.assertEqual(
            "C:\\not_smb_share\\temp",
            os_ext.Windows.path_join("C:", "//not_smb_share", "temp"),
        )
        self.assertEqual(
            "\\\\smb_share\\temp",
            os_ext.Windows.path_join("C:", "\\\\smb_share", "temp"),
        )
        self.assertEqual("C:\\a\\b", os_ext.Windows.path_join("C:", "a", "b"))
        self.assertEqual("a\\b\\c\\d", os_ext.Windows.path_join("a", "b", "c", "d"))

    def test_unix(self):
        self.assertTrue(os_ext.Unix.is_shared_lib("libtest.so"))
        self.assertTrue(os_ext.Unix.is_shared_lib("libtest.so.1.2.3"))
        self.assertTrue(os_ext.Unix.is_shared_lib("libtest.1.2.3.so"))
        self.assertFalse(os_ext.Unix.is_shared_lib("libtest.a"))

        self.assertTrue(os_ext.Unix.is_static_lib("libtest.a"))
        self.assertTrue(os_ext.Unix.is_static_lib("libtest.1.2.3.a"))
        self.assertFalse(os_ext.Unix.is_static_lib("libtest.so"))
        self.assertFalse(os_ext.Unix.is_static_lib("libtest.a.1.2.3"))

        self.assertIsNone(os_ext.Unix.parse_shared_lib("libtest.a"))
        self.assertIsNone(os_ext.Unix.parse_shared_lib("test.so"))
        self.assertIsNone(os_ext.Unix.parse_shared_lib("test.so.1.2.3"))

        descr = os_ext.Unix.parse_shared_lib("path/libtest.so.1.3.0")
        expected_descr = {
            "module_name": "test",
            "target_name": "test",
            "soname": "test",
            "version": "1.3.0",
        }
        self.assertEqual(expected_descr, descr)

        descr = os_ext.Unix.parse_shared_lib("path/libtest.1.3.0.so")
        expected_descr = {
            "module_name": "test.1.3.0",
            "target_name": "test.1.3.0",
            "soname": "test.1.3.0",
            "version": None,
        }
        self.assertEqual(expected_descr, descr)

        self.assertIsNone(os_ext.Unix.parse_static_lib("test"))
        self.assertIsNone(os_ext.Unix.parse_static_lib("test.a"))

        descr = os_ext.Unix.parse_static_lib("path/libtest.a")
        expected_descr = {
            "module_name": "test",
            "target_name": "test.static",
            "soname": "test",
            "version": None,
        }
        self.assertEqual(expected_descr, descr)

        self.assertIsNotNone(os_ext.Unix.parse_executable("libtest.a"))

        descr = os_ext.Unix.parse_executable("files/test_os_ext/linux.executable")
        expected_descr = {
            "module_name": "linux.executable",
            "target_name": "linux.executable",
            "soname": None,
            "version": None,
        }
        self.assertEqual(expected_descr, descr)

        descr = os_ext.Unix.parse_executable("linux.executable.3.2")
        expected_descr = {
            "module_name": "linux.executable",
            "target_name": "linux.executable",
            "soname": None,
            "version": "3.2",
        }
        self.assertEqual(expected_descr, descr)

        res = os_ext.Unix.resolve_lib("test", [self.test_group_dir])
        expected_res = os_ext.Unix.path_join(self.test_group_dir, "libtest.so")
        self.assertEqual(expected_res, res)

        res = os_ext.Unix.resolve_lib("teststatic", [self.test_group_dir])
        expected_res = os_ext.Unix.path_join(self.test_group_dir, "libteststatic.a")
        self.assertEqual(expected_res, res)

        res = os_ext.Unix.resolve_lib("testver", [self.test_group_dir])
        self.assertIsNone(res)

        re = os_ext.Unix.get_program_path_re("gcc", "clang")
        self.assertRegex("gcc", re)
        self.assertRegex("path/gcc", re)
        self.assertRegex("toolchain-gcc", re)
        self.assertRegex("clang", re)
        self.assertRegex("path/clang", re)
        self.assertRegex("toolchain-clang", re)
        self.assertNotRegex("notgcc", re)
        self.assertNotRegex("notclang", re)

        self.assertEqual("/a/b", os_ext.Unix.normalize_path("/a/b/./."))
        self.assertEqual("/a/b", os_ext.Unix.normalize_path("/a/b/"))
        self.assertEqual("/a/b", os_ext.Unix.normalize_path("/a//b"))
        self.assertEqual("b", os_ext.Unix.normalize_path("./a/../b"))

        self.assertTrue(os_ext.Unix.is_absolute("/temp"))
        self.assertFalse(os_ext.Unix.is_absolute("temp"))

        if self.on_windows():
            # generate for unix on windows
            self.assertEqual("F:/temp", os_ext.Unix.path_join(".", "F:", "temp"))
            self.assertEqual("/usr", os_ext.Unix.path_join(".", "F:", "temp", "/usr"))
        self.assertEqual("/temp", os_ext.Unix.path_join("/", "temp"))
        self.assertEqual("/usr/temp/", os_ext.Unix.path_join("/usr", "temp/"))
        self.assertEqual("\\usr/\\temp", os_ext.Unix.path_join("\\usr", "\\temp"))
        self.assertEqual("/b/temp", os_ext.Unix.path_join("/a", "/b", "temp"))
        self.assertEqual("/a/b", os_ext.Unix.path_join("/", "a", "b"))
        self.assertEqual("a/b/c/d", os_ext.Unix.path_join("a", "b", "c", "d"))

    def test_darwin(self):
        self.assertTrue(os_ext.Darwin.is_shared_lib("libtest.dylib"))
        self.assertTrue(os_ext.Darwin.is_shared_lib("libtest.1.2.3.dylib"))
        self.assertFalse(os_ext.Darwin.is_shared_lib("libtest.dylib.1.2.3"))
        self.assertFalse(os_ext.Darwin.is_shared_lib("libtest.so"))
        self.assertFalse(os_ext.Darwin.is_shared_lib("libtest.a"))

        descr = os_ext.Darwin.parse_shared_lib("path/libtest.1.3.0.dylib")
        expected_descr = {
            "module_name": "test",
            "target_name": "test",
            "soname": "test",
            "version": "1.3.0",
        }
        self.assertEqual(expected_descr, descr)

        res = os_ext.Darwin.resolve_lib("test", [self.test_group_dir])
        expected_res = os_ext.Darwin.path_join(self.test_group_dir, "libtest.dylib")
        self.assertEqual(expected_res, res)

        res = os_ext.Darwin.resolve_lib("teststatic", [self.test_group_dir])
        expected_res = os_ext.Darwin.path_join(self.test_group_dir, "libteststatic.a")
        self.assertEqual(expected_res, res)

        res = os_ext.Darwin.resolve_lib("testver", [self.test_group_dir])
        self.assertIsNone(res)
