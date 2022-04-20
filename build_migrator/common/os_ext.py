""""
This module should allow to parse build logs from one platform on another.
None of the functions access filesystem, with the exception of 'resolve_lib',
but even there it's optional.
"""

import logging
import os
import re
import platform


_logger = logging.getLogger(__name__)


def resolve_lib(lib, lib_dirs, cwd=os.curdir):
    return Platform.resolve_lib(lib, lib_dirs, cwd=cwd)


def is_shared_lib(path):
    return Platform.is_shared_lib(path)


def is_static_lib(path):
    return Platform.is_static_lib(path)


def parse_shared_lib(path):
    return Platform.parse_shared_lib(path)


def parse_static_lib(path):
    return Platform.parse_static_lib(path)


def parse_executable(path):
    return Platform.parse_executable(path)


def path_join(*paths):
    return Platform.path_join(*paths)


def is_absolute(path):
    return Platform.is_absolute(path)


def get_host_system_name():
    name = platform.system().lower()
    if name not in ("windows", "darwin"):
        name = "linux"
    return name


def get_program_path_re(name, *alts):
    r"""
        Get a regex that will match all possible executable paths with the provided name (names):
            * <name> or <name>.exe
            * <toolchain>-<name>
            * ...\<name>
            * .../<name>
            * etc
        Usage:
            * get_program_path_re('cl')
            * get_program_path_re('ar', 'gnu-ar') - alternative names supported
    """

    return Platform.get_program_path_re(name, *alts)


def normalize_path(path):
    return Platform.normalize_path(path)


class Windows:
    # Allowed values:
    # * False = win32 is not supported
    # * None = module not loaded yet
    # * actual'win32' module
    win32_module = None
    executable_ext = ".exe"
    shared_lib_ext = ".dll"
    static_lib_ext = ".lib"
    import_lib_ext = ".lib"
    shared_lib_re = re.compile(r"^(?P<name>[^\\/\s]+)\.dll$", re.IGNORECASE)
    static_lib_re = re.compile(r"^(?P<name>[^\\/\s]+)\.lib$", re.IGNORECASE)
    executable_re = re.compile(r"^(?P<name>[^\\/\s]+)\.exe$", re.IGNORECASE)
    absolute_path_re = re.compile(r"^(?:\\\\|[a-z]:)", re.IGNORECASE)

    @classmethod
    def is_shared_lib(cls, path):
        return path.lower().endswith(cls.shared_lib_ext)

    @classmethod
    def is_static_lib(cls, path):
        return path.lower().endswith(cls.static_lib_ext)

    @classmethod
    # version information will be available if 'pypiwin32' library is installed
    def parse_shared_lib(cls, path):
        filename = os.path.basename(path.replace("\\", "/"))
        m = cls.shared_lib_re.match(filename)
        if not m:
            return None
        return {
            "module_name": m.group("name"),
            "target_name": cls._remove_lib_prefix(m.group("name")).lower(),
            "soname": m.group("name") + cls.import_lib_ext,
            "version": cls.GetFileVersionInfo(path) if os.path.exists(path) else None,
        }

    @classmethod
    def parse_static_lib(cls, path):
        filename = os.path.basename(path.replace("\\", "/"))
        m = cls.static_lib_re.match(filename)
        if not m:
            return None
        return {
            "module_name": m.group("name"),
            "target_name": cls._remove_lib_prefix(m.group("name")).lower() + ".static",
            "soname": m.group("name") + cls.static_lib_ext,
            "version": None,
        }

    @classmethod
    def parse_import_lib(cls, path):
        filename = os.path.basename(path.replace("\\", "/"))
        m = cls.static_lib_re.match(filename)
        if not m:
            return None
        return {
            "module_name": m.group("name"),
            "target_name": cls._remove_lib_prefix(m.group("name")).lower(),
            "soname": m.group("name") + cls.import_lib_ext,
            "version": None,
        }

    @classmethod
    # version information will be available if 'pypiwin32' library is installed
    def parse_executable(cls, path):
        filename = os.path.basename(path.replace("\\", "/"))
        m = cls.executable_re.match(filename)
        if not m:
            return None
        return {
            "module_name": m.group("name"),
            "target_name": m.group("name").lower(),
            "soname": None,
            "version": cls.GetFileVersionInfo(path) if os.path.exists(path) else None,
        }

    @classmethod
    def resolve_lib(
        cls, lib, lib_dirs, cwd=os.curdir, import_lib=False, check_file=os.path.isfile
    ):
        if lib.endswith(cls.import_lib_ext) and import_lib:
            filenames = cls.get_library_filenames(
                lib, shared=True, static=False, implib=True
            )
        else:
            filenames = []

        filenames.append(lib)
        dirs = [cwd]
        dirs.extend(lib_dirs)
        for filename in filenames:
            for dir in dirs:
                path = cls.path_join(dir, filename)

                if not cls.is_absolute(path):
                    path = cls.path_join(cwd, path)

                if check_file(cls.normalize_path(path)):
                    return path

        return None

    @classmethod
    def get_obj_file_locations(cls, obj, obj_dirs, cwd=os.curdir):
        for dir in [cwd] + obj_dirs:
            path = cls.path_join(dir, obj)
            if not cls.is_absolute(path):
                path = cls.path_join(cwd, path)
            yield path

    @classmethod
    def get_program_path_re(cls, name, *alts):
        parts = [
            r"(?:^|.+-|.+\\|.+/){}(?:\.exe|\.bat)?$".format(re.escape(n))
            for n in (name,) + alts
        ]
        full_re = None
        if len(parts) > 1:
            full_re = "|".join(parts)
            full_re = r"(?:{})".format(full_re)
        else:
            full_re = parts[0]

        return re.compile(full_re, re.IGNORECASE)

    # TODO: move to common?
    @classmethod
    def _get_path_case_from_filesystem(cls, path):
        if not os.path.exists(path):
            return None

        # TODO: check filesystem case sensitivity
        if os.name != "nt":
            return path

        orig_path = path
        path_split = path.split("\\")
        if not (len(path_split[0]) == 2 and path_split[0][1] == ":"):
            raise ValueError("Path must be absolute: {}".format(path))
        test_path = path_split[0].upper() + "\\"
        for i in range(1, len(path_split)):
            part = path_split[i]
            if os.path.isdir(test_path):
                for name in os.listdir(test_path):
                    if name.lower() == part.lower():
                        part = name
                        break
                test_path = cls.path_join(test_path, part)
            else:
                return orig_path
        return test_path

    @classmethod
    def normalize_path(cls, path):
        win32 = cls._get_win32_module()
        if win32 is not None:
            long_path = win32.GetLongPathName(path)
            if long_path is None:
                # File does not exist, try resolving its directory
                dirname, filename = os.path.split(path)
                if dirname:
                    long_path = win32.GetLongPathName(dirname)
                    if long_path is not None:
                        long_path = cls.path_join(long_path, filename)
            if long_path is not None:
                path = long_path
        path = os.path.normpath(path.replace("\\", "/"))
        actual_path = cls._get_path_case_from_filesystem(path)
        if actual_path:
            path = actual_path
        return path.replace("\\", "/")

    @classmethod
    def _remove_lib_prefix(cls, name):
        if name.lower().startswith("lib") and len(name) > 3:
            return name[3:]
        return name

    @classmethod
    def get_library_filenames(
        cls, namespec, static=True, shared=True, implib=True, revision=None
    ):
        result = []
        basename = os.path.splitext(namespec)[0]
        if shared:
            result.append(basename + cls.shared_lib_ext)
        if static or implib:
            result.append(basename + cls.static_lib_ext)
        return result

    @classmethod
    def GetFileVersionInfo(cls, path):
        win32 = cls._get_win32_module()
        if win32 is not None:
            version = win32.GetFileVersionInfo(path)
            if version and version.find(", ") != -1:
                # reformat "major, minor" to "minor.major"
                version_parts = version.split(", ")
                # remove trailing zeros
                while version_parts[-1] == '0':
                    version_parts = version_parts[:-2]
                version = ".".join(version_parts)
            return version
        else:
            return None

    @classmethod
    def _get_win32_module(cls):
        if cls.win32_module:
            return cls.win32_module
        if cls.win32_module is False:
            return None

        try:
            from . import win32

            cls.win32_module = win32
        except Exception as e:
            _logger.error(
                "%s\n%s"
                % (e, "GetLongPathName and GetFileVersionInfo will not be available")
            )
            cls.win32_module = False

        return cls._get_win32_module()

    @classmethod
    def path_join(cls, *paths):
        if len(paths) <= 1:
            return paths[0]

        if cls.is_absolute(paths[1]):
            return cls.path_join(paths[1], *paths[2:])

        if not get_host_system_name() == "windows" and not cls.is_absolute(paths[0]):
            # Workaround that allows generating for Windows on Unix
            # Treat paths starting with '/' as absolute, but only once per path_join() call
            if Unix.is_absolute(paths[1]):
                return cls.path_join(paths[1], *paths[2:])

        first = paths[0].rstrip("/\\")
        second = paths[1].lstrip("/\\")
        return cls.path_join("\\".join([first, second]), *paths[2:])

    @classmethod
    def is_absolute(cls, path):
        return bool(cls.absolute_path_re.match(path))


class Unix:
    shared_lib_ext = ".so"
    static_lib_ext = ".a"
    shared_lib_re = re.compile(
        r"^lib(?P<name>[^\\/\s]+)\.so(?P<version>(?:\.\d+){0,4})$"
    )
    static_lib_re = re.compile(r"^lib(?P<name>[^\\/\s]+)\.a$")
    executable_re = re.compile(r"^(?P<name>[^\\/\s]+?)(?P<version>(?:\.\d+){0,4})$")

    @classmethod
    def is_shared_lib(cls, path):
        return cls.shared_lib_re.match(os.path.basename(path))

    @classmethod
    def is_static_lib(cls, path):
        return path.endswith(cls.static_lib_ext)

    @staticmethod
    def __format_version__(version):
        if version:
            version = version[1:]  # skip the first '.'
        if version == "":
            version = None
        return version

    @classmethod
    def parse_shared_lib(cls, path):
        filename = os.path.basename(path)
        m = cls.shared_lib_re.match(filename)
        if not m:
            return None
        return {
            "module_name": m.group("name"),
            "target_name": m.group("name"),
            "soname": m.group("name"),
            "version": cls.__format_version__(m.group("version")),
        }

    @classmethod
    def parse_static_lib(cls, path):
        filename = os.path.basename(path)
        m = cls.static_lib_re.match(filename)
        if not m:
            return None
        return {
            "module_name": m.group("name"),
            "target_name": m.group("name") + ".static",
            "soname": m.group("name"),
            "version": None,
        }

    @classmethod
    def parse_executable(cls, path):
        filename = os.path.basename(path)
        m = cls.executable_re.match(filename)
        if not m:
            return None
        return {
            "module_name": m.group("name"),
            "target_name": m.group("name"),
            "soname": None,
            "version": cls.__format_version__(m.group("version")),
        }

    @classmethod
    def resolve_lib(
        cls, lib, lib_dirs, cwd=os.curdir, static_only=None, check_file=os.path.isfile
    ):
        for dir in lib_dirs:
            dir = cls.path_join(cwd, dir)
            if static_only:
                filenames = cls.get_library_filenames(lib, shared=False, static=True)
            else:
                filenames = cls.get_library_filenames(lib, shared=True, static=True)
            for expected_filename in filenames:
                for filename in sorted(os.listdir(dir)):
                    path = cls.path_join(dir, filename)
                    if filename == expected_filename and check_file(path):
                        return path

        return None

    @classmethod
    def get_program_path_re(cls, name, *alts):
        parts = [
            r"(?:^|.+-|.+/){}(?:\.sh)?$".format(re.escape(n)) for n in (name,) + alts
        ]
        full_re = None
        if len(parts) > 1:
            full_re = "|".join(parts)
            full_re = r"(?:{})".format(full_re)
        else:
            full_re = parts[0]

        return re.compile(full_re)

    @classmethod
    def normalize_path(cls, path):
        return os.path.normpath(path).replace("\\", "/")

    @classmethod
    def get_library_filenames(cls, namespec, shared=True, static=True, revision=None):
        result = []
        if shared:
            result.append(cls.get_shared_library_filename(namespec, revision=revision))
        if static:
            result.append(cls.get_static_library_filename(namespec))
        return result

    @classmethod
    def get_shared_library_filename(cls, namespec, revision=None):
        filename = "lib" + namespec + cls.shared_lib_ext
        if revision:
            filename += "." + revision
        return filename

    @classmethod
    def get_static_library_filename(cls, namespec):
        return "lib" + namespec + cls.static_lib_ext

    @classmethod
    def path_join(cls, *paths):
        if len(paths) <= 1:
            return paths[0]

        if cls.is_absolute(paths[1]):
            return cls.path_join(paths[1], *paths[2:])

        if get_host_system_name() == "windows" and not cls.is_absolute(paths[0]):
            # Workaround that allows generating for Unix on Windows
            # Treat paths starting with '<letter>:' as absolute, but only once per path_join() call
            if Windows.is_absolute(paths[1]):
                return cls.path_join(paths[1], *paths[2:])

        first = paths[0].rstrip("/")
        second = paths[1]
        return cls.path_join("/".join([first, second]), *paths[2:])

    @staticmethod
    def is_absolute(path):
        return path.startswith("/")


class Darwin(Unix):
    shared_lib_ext = ".dylib"
    shared_lib_re = re.compile(
        r"^lib(?P<name>[^\\/\s]+?)(?P<version>(?:\.\d+){0,4})\.dylib$"
    )

    @classmethod
    def get_shared_library_filename(cls, namespec, revision=None):
        filename = "lib" + namespec
        if revision:
            filename += "." + revision
        filename += cls.shared_lib_ext
        return filename


def get_platform(name=None):
    if name is None:
        name = get_host_system_name()
    else:
        name = name.lower()
    if name.startswith("win"):
        return Windows
    elif name in ["darwin", "mac"]:
        return Darwin
    else:
        return Unix


Platform = get_platform()
