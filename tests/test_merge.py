import os
import sys
import unittest

__module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, __module_dir)
import base  # noqa: E402
from merge_cmake.merge_cmake import merge_cmake  # noqa: E402


class TestMerge(base.TestBase):
    def test_merge_basic(self):
        """Check that merge_cmake function works
        """

        self.set_test_data_subdir("basic")

        generate_dir = os.path.join(self.test_method_out_dir, "out")
        self.makedirs(generate_dir)
        result_cmake = os.path.join(generate_dir, "CMakeLists.txt")
        expected_cmake = os.path.join(self.test_method_dir, "CMakeLists.txt")
        cmake1 = os.path.join(self.test_method_dir, "windows", "CMakeLists.txt")
        cmake2 = os.path.join(self.test_method_dir, "linux", "CMakeLists.txt")
        merge_cmake([cmake1, cmake2], result_cmake)
        self.assertFilesEqual(expected_cmake, result_cmake)

    def _test_merge_impl(self, directory, reverse=False):
        """Check that merge_cmake function works
        """

        self.set_test_data_subdir(directory)

        generate_dir = os.path.join(self.test_method_out_dir, "out")
        self.makedirs(generate_dir)
        result_cmake = os.path.join(generate_dir, "CMakeLists.txt")
        infiles = [
            os.path.join(self.test_method_dir, f)
            for f in os.listdir(self.test_method_dir)
            if f != "result.txt"
        ]
        infiles = sorted(infiles)
        if reverse:
            infiles = list(reversed(infiles))
        expected_cmake = os.path.join(self.test_method_dir, "result.txt")
        merge_cmake(infiles, result_cmake)
        self.assertFilesEqual(expected_cmake, result_cmake)

    def test_merge_complex_1(self):
        self._test_merge_impl("complex")

    def test_merge_complex_2(self):
        self._test_merge_impl("complex", True)

    def test_merge_grouping_1(self):
        self._test_merge_impl("grouping_1")

    def test_merge_grouping_1_reverse(self):
        self._test_merge_impl("grouping_1", True)

    def test_merge_grouping_2(self):
        self._test_merge_impl("grouping_2")

    def test_merge_grouping_2_reverse(self):
        self._test_merge_impl("grouping_2", True)

    def test_merge_empty_lines(self):
        self._test_merge_impl("empty_lines")

    def test_merge_empty_lines_reverse(self):
        self._test_merge_impl("empty_lines", True)

    @unittest.skip("Bug #4103439")
    def test_zlib(self):
        self._test_merge_impl("zlib", True)

    def test_openssl(self):
        self._test_merge_impl("openssl", True)

    def test_icu(self):
        self._test_merge_impl("icu", True)

    @unittest.skip("Bug #4103439")
    def test_conflicting_order_1(self):
        self._test_merge_impl("conflicting_order_1", True)

    @unittest.skip("Bug #4103439")
    def test_conflicting_order_2(self):
        self._test_merge_impl("conflicting_order_2", True)
