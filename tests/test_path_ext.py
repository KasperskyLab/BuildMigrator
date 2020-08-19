import os
import sys

__module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, __module_dir)
import base  # noqa: E402
import build_migrator.common.path_ext as path_ext  # noqa: E402


class TestPathExtensions(base.TestBase):
    def test_closest_dir(self):
        self.assertEqual((".", "a"), path_ext.closest_dir("a", [".", "a"]))
        self.assertEqual(("a", "."), path_ext.closest_dir("a", ["a", "."]))
        self.assertEqual(("a", "."), path_ext.closest_dir("a", ["a", "a/b"]))
        self.assertEqual(("a/b/c", ".."), path_ext.closest_dir("a/b", ["a/b/c"]))
        self.assertEqual(("a/b", ".."), path_ext.closest_dir("a", ["a/b/c", "a/b"]))
        self.assertEqual(
            ("a/b", os.path.join("..", "b.txt")),
            path_ext.closest_dir("a/b.txt", ["a/b"]),
        )
        self.assertEqual(
            ("a/b/c", os.path.join("..", "..")), path_ext.closest_dir("a", ["a/b/c"])
        )
        self.assertIsNone(path_ext.closest_dir("a", ["a/b/c"], 1))

    def test_relpath_level(self):
        self.assertEqual(0, path_ext.relpath_level("a"))
        self.assertEqual(0, path_ext.relpath_level("/a"))
        self.assertEqual(0, path_ext.relpath_level("C:\\a"))
        self.assertEqual(0, path_ext.relpath_level("./a"))
        self.assertEqual(1, path_ext.relpath_level("../a"))
        self.assertEqual(0, path_ext.relpath_level(".\\a"))
        self.assertEqual(1, path_ext.relpath_level("..\\a"))
        self.assertEqual(0, path_ext.relpath_level("./../a"))
        self.assertEqual(2, path_ext.relpath_level("../../a"))
        self.assertEqual(0, path_ext.relpath_level("a/../.."))
