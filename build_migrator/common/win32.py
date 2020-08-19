import array
from ctypes import (
    create_string_buffer,
    create_unicode_buffer,
    windll,
    wintypes,
    POINTER,
    string_at,
    wstring_at,
)
import sys


if not hasattr(wintypes, "LPDWORD"):  # Python 2
    wintypes.LPDWORD = POINTER(wintypes.DWORD)

if sys.version_info[0] >= 3:
    unicode = str

__GetFileVersionInfoSizeW = windll.version.GetFileVersionInfoSizeW
# TODO: not sure it's requried
__GetFileVersionInfoSizeW.argtypes = [wintypes.LPCWSTR, wintypes.LPDWORD]
__GetFileVersionInfoSizeW.restype = wintypes.HANDLE

__GetFileVersionInfoW = windll.version.GetFileVersionInfoW
__GetFileVersionInfoW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.LPVOID,
]
__GetFileVersionInfoW.restype = wintypes.BOOL

__VerQueryValueW = windll.version.VerQueryValueW
__VerQueryValueW.argtypes = [
    wintypes.LPCVOID,
    wintypes.LPCWSTR,
    POINTER(wintypes.LPVOID),
    POINTER(wintypes.UINT),
]
__VerQueryValueW.restype = wintypes.BOOL

__VerQueryValueA = windll.version.VerQueryValueA
__VerQueryValueA.argtypes = [
    wintypes.LPCVOID,
    wintypes.LPCSTR,
    POINTER(wintypes.LPVOID),
    POINTER(wintypes.UINT),
]
__VerQueryValueA.restype = wintypes.BOOL

__GetFileVersionInfoA = windll.version.GetFileVersionInfoA
__GetFileVersionInfoSizeA = windll.version.GetFileVersionInfoSizeA


def GetFileVersionInfo(path):
    if isinstance(path, unicode):
        GetFileVersionInfoSize = __GetFileVersionInfoSizeW
        _GetFileVersionInfo = __GetFileVersionInfoW
        VerQueryValue = __VerQueryValueW
        VerQueryValueSubBlock1 = unicode(r"\VarFileInfo\Translation")
        VerQueryValueSubBlock2 = unicode(r"\StringFileInfo\%04x%04x\FileVersion")
        _string_at = wstring_at
    else:
        GetFileVersionInfoSize = __GetFileVersionInfoSizeA
        _GetFileVersionInfo = __GetFileVersionInfoA
        VerQueryValue = __VerQueryValueA
        VerQueryValueSubBlock1 = br"\VarFileInfo\Translation"
        VerQueryValueSubBlock2 = br"\StringFileInfo\%04x%04x\FileVersion"
        _string_at = string_at

    size = GetFileVersionInfoSize(path, None)
    if not size:
        return None

    data = create_string_buffer(size)
    success = _GetFileVersionInfo(path, 0, size, data)
    assert success

    buffer = wintypes.LPVOID()
    length = wintypes.UINT()
    success = VerQueryValue(data, VerQueryValueSubBlock1, buffer, length)
    if not success:
        return None

    codepage = tuple(array.array("H", string_at(buffer.value, length.value)))

    success = VerQueryValue(data, VerQueryValueSubBlock2 % codepage, buffer, length)
    if not success:
        return None

    return _string_at(buffer.value, length.value - 1)


def GetLongPathName(path):
    if isinstance(path, unicode):
        _GetLongPathName = windll.kernel32.GetLongPathNameW
        create_buffer = create_unicode_buffer
    else:
        _GetLongPathName = windll.kernel32.GetLongPathNameA
        create_buffer = create_string_buffer

    res = _GetLongPathName(path, None, 0)
    if res == 0:
        return None
    buf = create_buffer(res)
    res = _GetLongPathName(path, buf, res)
    if res == 0:
        return None
    else:
        return type(path)(buf[:res])


def GetShortPathName(path):
    if isinstance(path, unicode):
        _GetShortPathName = windll.kernel32.GetShortPathNameW
        create_buffer = create_unicode_buffer
    else:
        _GetShortPathName = windll.kernel32.GetShortPathNameA
        create_buffer = create_string_buffer

    res = _GetShortPathName(path, None, 0)
    if res == 0:
        return None
    buf = create_buffer(res)
    res = _GetShortPathName(path, buf, res)
    if res == 0:
        return None
    else:
        return type(path)(buf[:res])
