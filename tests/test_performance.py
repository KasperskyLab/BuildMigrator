import cProfile
import logging
import os
import sys
import unittest

__module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, __module_dir)
import base  # noqa: E402


class TestPerformance(base.TestBase):
    @unittest.skip("This test is disabled by default")
    def test_performance(self):
        test_data_dir = os.path.join(self.test_method_out_dir, "in")
        build_dir = os.path.join(test_data_dir, "build")
        source_dir = os.path.join(test_data_dir, "source")
        build_log = os.path.join(test_data_dir, "build.log")
        cmakelists = os.path.join(test_data_dir, "CMakeLists.txt")
        os.mkdir(test_data_dir)
        os.mkdir(build_dir)
        os.mkdir(source_dir)

        logging.info("Generating build.log")
        with open(build_log, "w") as f:
            for idx in range(1, 10000):
                f.write(
                    "{test_data_dir}\cl.bat /c /I../source /Fo{idx}.obj ..\\source\\{idx}.cpp\n".format(
                        test_data_dir=test_data_dir, idx=idx,
                    )
                )
                cpp_path = os.path.join(source_dir, "{}.cpp".format(idx))
                with open(cpp_path, "w"):
                    pass

        logging.info("Generating cl.exe stand-in")
        cl_stub_path = os.path.join(test_data_dir, "cl.bat")
        with open(cl_stub_path, "w") as f:
            f.write("@echo off\n")
            for idx in range(1, 20):
                hpp_path = os.path.join(source_dir, "{}.hpp".format(idx))
                with open(hpp_path, "w"):
                    pass
                f.write("echo Note: including file: {}\n".format(hpp_path))

        with open(cmakelists, "w") as f:
            f.write("Intentionally left empty")

        logging.info("Starting the test")
        profiler = cProfile.Profile()
        profiler.enable()
        try:
            self.parse_and_generate(
                "windows", test_data_dir=test_data_dir,
            )
        except:
            pass
        finally:
            profiler.disable()
            profiler.print_stats(sort="cumtime")
