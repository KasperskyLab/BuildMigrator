import codecs
import io
import sys


encoding_to_bom = {
    "utf-8-sig": codecs.BOM_UTF8,
    "utf-16-le": codecs.BOM_UTF16_LE,
    "utf-32-le": codecs.BOM_UTF32_LE,
    "utf-16-be": codecs.BOM_UTF16_BE,
    "utf-32-be": codecs.BOM_UTF32_BE,
}


def detect_encoding_by_bom(path=None, data=None, default="utf-8"):
    if path:
        with open(path, "rb") as f:
            raw = f.read(4)
    else:
        raw = data[0:4]

    for enc, bom in encoding_to_bom.items():
        if raw.startswith(bom):
            return enc, bom
    return default, None


def read_lines(path, encoding=None, newline=None):
    if newline is None:
        newline = "\n"

    if encoding is None:
        encoding, bom = detect_encoding_by_bom(path=path, default=encoding)
    else:
        bom = encoding_to_bom.get(encoding)

    if bom:
        bom = bom.decode(encoding)

    with io.open(path, encoding=encoding, newline=newline, errors="replace") as f:
        for line in _read_lines_from_stream(f, bom):
            yield line


def read_lines_from_binary(data, encoding=None, newline=None):
    if newline is None:
        newline = "\n"

    if encoding is None:
        encoding, bom = detect_encoding_by_bom(data=data, default=encoding)
    else:
        bom = encoding_to_bom.get(encoding)

    if bom:
        bom = bom.decode(encoding)

    with io.TextIOWrapper(
        io.BytesIO(data), encoding=encoding, newline=newline, errors="replace"
    ) as f:
        for line in _read_lines_from_stream(f, bom):
            yield line


def convert_lines_to_binary(lines, encoding="utf-8", newline=None):
    if newline is None:
        newline = "\n"

    with io.BytesIO() as bf:
        bom = encoding_to_bom.get(encoding)
        if bom is not None:
            bf.write(bom)
        with io.TextIOWrapper(
            bf, encoding=encoding, newline=newline, errors="replace"
        ) as tf:
            _write_lines_to_stream(tf, lines)
            tf.flush()
            return bf.getvalue()


def _read_lines_from_stream(stream, bom=None):
    for line in stream:
        if bom and line.startswith(bom):
            line = line[len(bom):]
            bom = None
        if sys.version_info <= (3, 0):
            line = line.encode("utf-8")
        yield line


def _write_lines_to_stream(stream, lines):
    for line in lines:
        if sys.version_info <= (3, 0):
            line = line.decode("utf-8")
        stream.write(line)
