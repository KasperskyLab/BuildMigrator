import copy
import difflib
import io
import logging
import os
import platform
import pprint
import re
import shutil
import sys
import subprocess
import tarfile
import unittest

__build_migrator_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, __build_migrator_dir)
from build_migrator import BuildMigrator, ModuleLoader, SettingsLoader  # noqa: E402
from build_migrator.modules import ModuleGroups  # noqa: E402
from build_migrator.common.algorithm import get_subdict  # noqa: E402
from build_migrator.common.encoding_detection import (
    read_lines,
    encoding_to_bom,
)  # noqa: E402
from build_migrator.common.os_ext import get_platform  # noqa: E402


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestBase(unittest.TestCase):
    @staticmethod
    def on_windows():
        return platform.system() == "Windows"

    @staticmethod
    def on_darwin():
        return platform.system() == "Darwin"

    @classmethod
    def which(cls, cmd, mode=os.F_OK | os.X_OK):
        # From https://github.com/cookiecutter/whichcraft by Daniel Roy Greenfeld
        # TODO: Once we stop supporting Python 2, remove this and use shutil.which

        path = os.environ.get("PATH", os.defpath)
        path = path.split(os.pathsep)

        if cls.on_windows():
            # The current directory takes precedence on Windows.
            if os.curdir not in path:
                path.insert(0, os.curdir)

            # PATHEXT is necessary to check on Windows.
            pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
            # See if the given file matches any of the expected path
            # extensions. This will allow us to short circuit when given
            # "python.exe". If it does match, only test that one, otherwise we
            # have to try others.
            if any(cmd.lower().endswith(ext.lower()) for ext in pathext):
                files = [cmd]
            else:
                files = [cmd + ext for ext in pathext]
        else:
            # On other platforms you don't have things like PATHEXT to tell you
            # what file suffixes are executable, so just pass on cmd as-is.
            files = [cmd]

        seen = set()
        for dir_ in path:
            normdir = os.path.normcase(dir_)
            if normdir not in seen:
                seen.add(normdir)
                for fname in files:
                    fpath = os.path.join(dir_, fname)
                    if (
                        os.path.exists(fpath)
                        and os.access(fpath, mode)
                        and not os.path.isdir(fpath)
                    ):
                        return fpath

        return None

    @classmethod
    def has_program(cls, name):
        return cls.which(name) is not None

    @classmethod
    def setUpClass(cls, clean_directory=True):
        cls.clean_directory = clean_directory

        cls.test_root_dir = os.path.abspath(os.path.dirname(__file__))
        if cls.on_windows():
            # Capitalize disk letter (useful when parsing non-Windows build logs on Windows)
            cls.test_root_dir = cls.test_root_dir[0].upper() + cls.test_root_dir[1:]

        test_group_name = cls.__module__.split(".")[-1]
        cls.test_group_dir = os.path.join(cls.test_root_dir, "files", test_group_name)
        cls.test_group_out_dir = os.path.join(os.getcwd(), ".files", test_group_name)
        cls.makedirs(cls.test_group_out_dir)

        cls.build_migrator_bin_dir = os.path.join(cls.test_root_dir, "../bin")

        cls.build_migrator_path = os.path.join(
            cls.build_migrator_bin_dir, "build_migrator"
        )
        if cls.on_windows():
            cls.build_migrator_path += ".bat"

        cls.has_gcc = cls.has_program("gcc") and cls.has_program("g++")
        cls.has_clang = cls.has_program("clang") and cls.has_program("clang++")
        if cls.has_clang:
            _clang_version_output = subprocess.check_output(["clang", "--version"])
            _m = re.search(
                r"\bversion\s+(\d+\.\d+\.\d+)",
                str(_clang_version_output),
                re.IGNORECASE,
            )
            assert _m, _clang_version_output
            cls.clang_version = tuple(map(int, _m.group(1).split(".")))
        cls.has_msvc = cls.has_program("cl") and cls.has_program("rc")
        if cls.has_msvc:
            _msvc_cl_out = subprocess.check_output(["cl.exe"], stderr=subprocess.STDOUT)
            _m = re.search(
                r"compiler version (?:\d+\.)+\d+ for ([a-z0-9-]+)\b",
                str(_msvc_cl_out),
                re.IGNORECASE,
            )
            assert _m, _msvc_cl_out
            cls.msvc_arch = _m.group(1)
        else:
            cls.msvc_arch = None
        cls.has_clang_cl = cls.has_program("clang-cl") and cls.has_program("lld-link")
        cls.has_nasm = cls.has_program("nasm")
        cls.has_yasm = cls.has_program("yasm")
        cls.has_cmake = cls.has_program("cmake")
        if cls.has_cmake:
            _cmake_version_output = subprocess.check_output(["cmake", "--version"])
            _m = re.search(
                r"\bversion\s+(\d+\.\d+\.\d+)",
                str(_cmake_version_output),
                re.IGNORECASE,
            )
            assert _m, _cmake_version_output
            cls.cmake_version = tuple(map(int, _m.group(1).split(".")))
        cls.has_ninja = cls.has_program("ninja")
        cls.default_presets = {
            "windows": ["windows", "msbuild"],
            "linux": ["linux", "autotools"],
            "darwin": ["darwin", "autotools"],
        }
        cls._log_idx = 1

    def setUp(self):
        assertRegex = getattr(self, "assertRegex", None)
        if not callable(assertRegex):
            self.assertRegex = self.assertRegexpMatches
            self.assertNotRegex = self.assertNotRegexpMatches

        subdir = self._testMethodName[len("test_"):]
        self.test_method_dir = os.path.join(self.test_group_dir, subdir)
        self.test_method_out_dir = os.path.join(self.test_group_out_dir, subdir)
        self.makedirs(self.test_method_out_dir)

    def set_test_data_subdir(self, subdir):
        self.test_method_dir = os.path.join(self.test_group_dir, subdir)

    def get_test_data(self, relpath):
        return os.path.join(self.test_method_dir, relpath)

    def assertFilesEqual(self, first, second, msg=None, encoding=None):
        if encoding is None:
            encoding = "utf-8"
        lines_first = None
        with io.open(first, "rt", newline=None, encoding=encoding) as f:
            lines_first = f.readlines()

        lines_second = None
        with io.open(second, "rt", newline=None, encoding=encoding) as f:
            lines_second = f.readlines()

        if lines_first != lines_second:
            message = "".join(difflib.ndiff(lines_first, lines_second))
            if msg:
                message += " : " + msg
            self.fail(
                "Files are different:\nA: {}\nB: {}\n".format(first, second) + message
            )

    def assertFilesEqualBinary(self, first, second):
        content_first = None
        with open(first, "rb") as f:
            content_first = f.read()

        content_second = None
        with open(second, "rb") as f:
            content_second = f.read()

        if content_first != content_second:
            self.fail("Files are different: {}, {}".format(first, second))

    @classmethod
    def makedirs(cls, path):
        if not os.path.exists(path):
            os.makedirs(path)
        elif cls.clean_directory:
            for f in os.listdir(path):
                f_path = os.path.join(path, f)
                if os.path.isfile(f_path):
                    os.unlink(f_path)
                elif os.path.isdir(f_path):
                    shutil.rmtree(f_path, ignore_errors=True)

    @classmethod
    def replace_file_content(cls, path, substring, replacement, encoding="utf-8"):
        # TODO: reuse write_lines from encoding_detection
        bom = encoding_to_bom.get(encoding)
        content = "".join(read_lines(path))
        content = content.replace(substring, replacement)
        with io.open(path, "wb") as f:
            if bom:
                f.write(bom)
            f.write(content.encode(encoding))

    def _format_template(self, path, platform, test_data_dir):
        if not path.endswith(".in"):
            return path
        with open(path, "rt") as f_template:
            filename = os.path.split(path)[1]
            # remove .in extension
            filename = filename[:-2]
            out_path = os.path.join(self.test_method_out_dir, filename)
            with open(out_path, "wt") as f:
                for line in f_template:
                    f.write(
                        line.replace(
                            "@cwd@", platform.normalize_path(test_data_dir),
                        )
                    )
            return out_path

    def parse_and_generate(
        self,
        test_platform,
        presets=None,
        path_aliases=None,
        log_type=None,
        cmakelists_name="CMakeLists.txt",
        max_relpath_level=1,
        extra_targets=None,
        build_dirs=None,
        source_dir=None,
        commands=None,
        load=None,
        save=None,
        logs=None,
        source_subdir=None,
        flag_optimizer_ver=None,
        test_data_dir=None,
        **kwargs
    ):
        if test_data_dir is None:
            test_data_dir = self.test_method_dir
        if path_aliases is None:
            path_aliases = []
        if source_subdir is None:
            source_subdir = "."
        if flag_optimizer_ver is None:
            flag_optimizer_ver = "1"

        platform = get_platform(test_platform)
        if presets is None:
            presets = copy.copy(self.default_presets.get(test_platform))

        if source_dir is None:
            source_dir = os.path.join(test_data_dir, "source")

        if build_dirs is None:
            build_dir = os.path.join(test_data_dir, "build")
            multiple_build_dirs = [
                os.path.join(test_data_dir, "build1"),
                os.path.join(test_data_dir, "build2"),
            ]

            if os.path.exists(multiple_build_dirs[0]):
                build_dirs = multiple_build_dirs
            else:
                build_dirs = [build_dir]

        generator_out_dir = os.path.join(self.test_method_out_dir, "out")
        self.makedirs(generator_out_dir)

        expected_cmake_template = os.path.join(
            test_data_dir, cmakelists_name + ".in"
        )
        if os.path.exists(expected_cmake_template):
            expected_cmake = self._format_template(
                expected_cmake_template, platform, test_data_dir=test_data_dir
            )
        else:
            expected_cmake = os.path.join(test_data_dir, cmakelists_name)

        if logs is None:
            build_log_template = os.path.join(test_data_dir, "build.log.in")
            multiple_build_logs_first = os.path.join(test_data_dir, "build1.log")
            multiple_build_logs_first_template = os.path.join(
                test_data_dir, "build1.log.in"
            )
            if os.path.exists(build_log_template):
                logs = [build_log_template]
            elif os.path.exists(multiple_build_logs_first):
                logs = [multiple_build_logs_first]
                idx = 2
                while True:
                    path = os.path.join(test_data_dir, "build%d.log" % idx)
                    idx += 1
                    if os.path.exists(path):
                        logs.append(path)
                    else:
                        break
            elif os.path.exists(multiple_build_logs_first_template):
                logs = []
                idx = 1
                while True:
                    template = os.path.join(
                        test_data_dir, "build%d.log.in" % idx
                    )
                    if not os.path.exists(template):
                        break
                    idx += 1
                    logs.append(template)
            else:
                logs = [os.path.join(test_data_dir, "build.log")]

        logs = [self._format_template(path, platform, test_data_dir=test_data_dir) for path in logs]

        if log_type:
            log_type += ":"
        else:
            log_type = ""
        kwargs.update(
            {
                "platform": test_platform,
                "path_aliases": path_aliases,
                "max_relpath_level": max_relpath_level,
                "logs": [log_type + log for log in logs],
                "build_dirs": build_dirs,
                "source_dir": source_dir,
                "out_dir": generator_out_dir,
                "save": None,
                "load": None,
                "source_subdir": source_subdir,
                "flag_optimizer_ver": flag_optimizer_ver,
            }
        )

        modules = None
        settings = {}
        if presets is not None:
            loader = SettingsLoader()
            settings = loader.load(presets)
            settings = loader.merge(settings, kwargs)
        else:
            settings = kwargs
        if settings is not None:
            modules = ModuleLoader(settings.get("module_dirs")).load(
                **get_subdict(
                    settings,
                    ModuleGroups.BUILDERS,
                    ModuleGroups.PARSERS,
                    ModuleGroups.OPTIMIZERS,
                    ModuleGroups.GENERATORS,
                )
            )

        migrator = BuildMigrator(modules)

        targets = []
        if load:
            targets = migrator.load_build_object_model(load)

        if extra_targets:
            targets.extend(extra_targets)

        if commands is None or "parse" in commands:
            targets = migrator.parse(targets, **settings)

        if "targets" in settings:
            del settings["targets"]
        if commands is None or "optimize" in commands:
            targets = migrator.optimize(targets, **settings)

        if save:
            migrator.save_build_object_model(save, targets)

        if commands is None or "generate" in commands:
            migrator.generate(targets, **settings)
            result_cmake = os.path.join(generator_out_dir, "CMakeLists.txt")
            self.assertTrue(os.path.exists(result_cmake))
            self.assertFilesEqual(expected_cmake, result_cmake)

    def parse_and_generate_bazel(
        self,
        test_platform,
        presets=None,
        path_aliases=None,
        log_type=None,
        extra_targets=None,
        build_dirs=None,
        source_dir=None,
        commands=None,
        load=None,
        save=None,
        logs=None,
        test_data_dir=None,
        **kwargs
    ):
        if test_data_dir is None:
            test_data_dir = self.test_method_dir
        if path_aliases is None:
            path_aliases = []

        platform = get_platform(test_platform)
        if presets is None:
            presets = copy.copy(self.default_presets.get(test_platform))

        if source_dir is None:
            source_dir = os.path.join(test_data_dir, "source")

        if build_dirs is None:
            build_dir = os.path.join(test_data_dir, "build")
            multiple_build_dirs = [
                os.path.join(test_data_dir, "build1"),
                os.path.join(test_data_dir, "build2"),
            ]

            if os.path.exists(multiple_build_dirs[0]):
                build_dirs = multiple_build_dirs
            else:
                build_dirs = [build_dir]

        generator_out_dir = os.path.join(self.test_method_out_dir, "bazel")
        self.makedirs(generator_out_dir)

        expected_bazel = os.path.join(test_data_dir, "BUILD.bazel")

        if logs is None:
            build_log_template = os.path.join(test_data_dir, "build.log.in")
            multiple_build_logs_first = os.path.join(test_data_dir, "build1.log")
            multiple_build_logs_first_template = os.path.join(
                test_data_dir, "build1.log.in"
            )
            if os.path.exists(build_log_template):
                logs = [build_log_template]
            elif os.path.exists(multiple_build_logs_first):
                logs = [multiple_build_logs_first]
                idx = 2
                while True:
                    path = os.path.join(test_data_dir, "build%d.log" % idx)
                    idx += 1
                    if os.path.exists(path):
                        logs.append(path)
                    else:
                        break
            elif os.path.exists(multiple_build_logs_first_template):
                logs = []
                idx = 1
                while True:
                    template = os.path.join(
                        test_data_dir, "build%d.log.in" % idx
                    )
                    if not os.path.exists(template):
                        break
                    idx += 1
                    logs.append(template)
            else:
                logs = [os.path.join(test_data_dir, "build.log")]

        logs = [self._format_template(path, platform, test_data_dir=test_data_dir) for path in logs]

        if log_type:
            log_type += ":"
        else:
            log_type = ""
        kwargs.update(
            {
                "platform": test_platform,
                "path_aliases": path_aliases,
                "logs": [log_type + log for log in logs],
                "build_dirs": build_dirs,
                "source_dir": source_dir,
                "out_dir": generator_out_dir,
                "save": None,
                "load": None,
            }
        )

        settings = {}
        if presets is not None:
            loader = SettingsLoader()
            settings = loader.load(presets)
            settings = loader.merge(settings, kwargs)
        else:
            settings = kwargs
        settings["generators"] = ["bazel"]
        modules = None
        if settings is not None:
            modules = ModuleLoader(settings.get("module_dirs")).load(
                **get_subdict(
                    settings,
                    ModuleGroups.BUILDERS,
                    ModuleGroups.PARSERS,
                    ModuleGroups.OPTIMIZERS,
                    ModuleGroups.GENERATORS,
                )
            )

        migrator = BuildMigrator(modules)

        targets = []
        if load:
            targets = migrator.load_build_object_model(load)

        if extra_targets:
            targets.extend(extra_targets)

        if commands is None or "parse" in commands:
            targets = migrator.parse(targets, **settings)

        if "targets" in settings:
            del settings["targets"]
        if commands is None or "optimize" in commands:
            targets = migrator.optimize(targets, **settings)

        if save:
            migrator.save_build_object_model(save, targets)

        if commands is None or "generate" in commands:
            settings["generators"] = "bazel"
            migrator.generate(targets, **settings)
            result_bazel = os.path.join(generator_out_dir, "BUILD.bazel")
            self.assertTrue(os.path.exists(result_bazel))
            expected_bazel = os.path.join(test_data_dir, "BUILD.bazel")
            self.assertFilesEqual(expected_bazel, result_bazel)

    def call(self, args, **kwargs):
        log_path = os.path.join(
            self.test_method_out_dir, "call_" + str(self._log_idx) + ".log"
        )
        exception = None
        with open(log_path, "w") as fout:
            logger.info(
                'Command: "%s", kwargs: %s', " ".join(args), pprint.pformat(kwargs)
            )
            try:
                subprocess.check_call(
                    args, stdout=fout, stderr=subprocess.STDOUT, **kwargs
                )
            except Exception as _e:
                exception = _e
        if exception:
            with open(log_path, "r") as fin:
                content = fin.read()
                if content:
                    logger.error(content)
            raise exception
        self._log_idx += 1

    def call_example_script(self, args, cwd=None):
        env = os.environ.copy()
        env["PATH"] = self.build_migrator_bin_dir + os.pathsep + env["PATH"]
        self.call(args, cwd=cwd, env=env)

    def build_with_cmake_and_ninja(
        self, source_dir, build_dir, release=True, extra_path=None
    ):
        cmake_path = os.getenv("CMAKE_PATH") or "cmake"
        self.makedirs(build_dir)
        args = ["-DCMAKE_VERBOSE_MAKEFILE=ON"]
        if self.on_windows():
            args.extend(["-DCMAKE_C_COMPILER=cl.exe", "-DCMAKE_CXX_COMPILER=cl.exe"])
        if release:
            args.append("-DCMAKE_BUILD_TYPE=Release")
        else:
            args.append("-DCMAKE_BUILD_TYPE=Debug")
        env = None
        if extra_path:
            env = os.environ.copy()
            env["PATH"] = extra_path + os.pathsep + env["PATH"]
        self.call([cmake_path] + args + ["-GNinja", source_dir], cwd=build_dir, env=env)
        self.call([cmake_path, "--build", "."], cwd=build_dir, env=env)

    def extract_archive(self, path, output):
        if path.lower().endswith(".tar.gz"):
            tar = tarfile.open(path, "r:gz")
            tar.extractall(output)
            tar.close()
        else:
            raise ValueError("Unsupported format")
