import logging
import os
import shutil
import sys

__module_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, __module_dir)
import base  # noqa: E402


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestE2E(base.TestBase):
    @classmethod
    def setUpClass(cls):
        super(TestE2E, cls).setUpClass(clean_directory=True)
        cls.examples_dir = os.path.join(cls.test_root_dir, "..", "docs", "Examples")

    def test_openssl(self):
        if not self.has_program("perl"):
            self.skipTest("perl not found in PATH")

        if self.msvc_arch is not None and self.msvc_arch != "x64":
            self.skipTest("msvc_arch != x64")

        out_dir = os.path.join(self.test_method_out_dir, "out")
        self.makedirs(out_dir)

        logger.info("Extracting OpenSSL source")
        archive = self.get_test_data("openssl-1.1.1g.tar.gz")

        self.extract_archive(archive, self.test_method_out_dir)

        script_path = os.path.join(self.examples_dir, "openssl")
        if self.on_windows():
            script_path = os.path.join(script_path, "for_windows.bat")
        elif self.on_darwin():
            script_path = os.path.join(script_path, "for_darwin.sh")
        else:
            script_path = os.path.join(script_path, "for_linux.sh")

        src_dir = os.path.join(self.test_method_out_dir, "openssl-1.1.1g")
        self.call_example_script([script_path, src_dir], cwd=out_dir)

        if not (self.has_cmake and self.has_ninja):
            logger.warn("CMake or Ninja not found: skipping build")
            return

        with open(os.path.join(out_dir, "CMakeLists.txt"), "r") as f:
            content = f.read()
            logger.debug("Generated CMakeLists.txt:\n%s", content)

        # build with native toolchain
        build_dir = os.path.join(self.test_method_out_dir, "_cmake_build")
        self.build_with_cmake_and_ninja(source_dir=out_dir, build_dir=build_dir)

        test_env = None
        if not self.on_windows():
            test_env = os.environ.copy()
            if self.on_darwin():
                test_env["DYLD_LIBRARY_PATH"] = build_dir
            else:
                test_env["LD_LIBRARY_PATH"] = build_dir

        if self.on_windows():
            # TODO: investigate why apps/openssl exits with "DLL not found" error on build agents
            return

        # check build artifacts
        self.call([os.path.join(build_dir, "apps/openssl"), "ciphers"], env=test_env)
        self.call([os.path.join(build_dir, "test/asn1_decode_test")], env=test_env)
        self.call([os.path.join(build_dir, "test/x509_time_test")], env=test_env)

    def test_boost_with_icu(self):
        self.skipTest("For Github CI only")

        on_linux = not self.on_windows() and not self.on_darwin()
        if not on_linux:
            self.skipTest("Not on Linux")

        icu_out_dir = os.path.join(self.test_method_out_dir, "icu")
        icu_src_dir = os.path.join(self.test_method_out_dir, "icu_src")
        self.makedirs(icu_src_dir)
        self.makedirs(icu_out_dir)
        logger.info("Extracting ICU source")
        self.extract_archive(self.get_test_data("icu4c-67_1-src.tar.gz"), icu_src_dir)

        script_path = os.path.join(self.examples_dir, "icu", "for_linux.sh")
        icu_src_dir = os.path.join(icu_src_dir, "icu", "source")
        self.call_example_script([script_path, icu_src_dir], cwd=icu_out_dir)

        icu_build_dir = os.path.join(icu_out_dir, "_build")
        icu_include_dir = os.path.join(icu_build_dir, "include", "unicode")
        self.makedirs(icu_include_dir)
        _dir = os.path.join(icu_src_dir, "common/unicode")
        for path in os.listdir(_dir):
            shutil.copy(os.path.join(_dir, path), icu_include_dir)
        _dir = os.path.join(icu_src_dir, "i18n/unicode")
        for path in os.listdir(_dir):
            shutil.copy(os.path.join(_dir, path), icu_include_dir)
        _dir = os.path.join(icu_src_dir, "io/unicode")
        for path in os.listdir(_dir):
            shutil.copy(os.path.join(_dir, path), icu_include_dir)

        boost_out_dir = os.path.join(self.test_method_out_dir, "boost")
        boost_src_dir = os.path.join(self.test_method_out_dir, "boost_src")
        self.makedirs(boost_out_dir)
        self.makedirs(boost_src_dir)
        logger.info("Extracting Boost source")
        self.extract_archive(self.get_test_data("boost_1_73_0.tar.gz"), boost_src_dir)

        boost_src_dir = os.path.join(boost_src_dir, "boost_1_73_0")
        script_dir = os.path.join(self.examples_dir, "boost_with_icu")

        script_path = os.path.join(script_dir, "1_build_for_linux.sh")
        self.call_example_script(
            [script_path, boost_src_dir, icu_build_dir], cwd=boost_out_dir
        )

        script_path = os.path.join(script_dir, "2_parse_for_linux.sh")
        self.call_example_script(
            [script_path, boost_src_dir, icu_build_dir], cwd=boost_out_dir
        )

        script_path = os.path.join(script_dir, "3_generate_for_linux.sh")
        self.call_example_script([script_path, boost_src_dir], cwd=boost_out_dir)

        shutil.copy(self.get_test_data("CMakeLists.txt"), self.test_method_out_dir)

        if self.has_cmake and self.has_ninja:
            build_dir = os.path.join(self.test_method_out_dir, "_cmake_build")
            self.build_with_cmake_and_ninja(
                source_dir=self.test_method_out_dir,
                build_dir=build_dir,
                extra_path=os.getenv("ICU_DEVTOOLS_DIR"),
            )
        else:
            logger.warn("CMake or Ninja not found: skipping build")
