# -*- coding: utf-8 -*-
import mimetypes
import os
import re

from flask import Response, abort, request, send_file

BYTE_RANGE_RE = re.compile(r"bytes=(\d+)-(\d+)?$")


def parse_byte_range(byte_range):
    """Returns the two numbers in 'bytes=123-456' or throws ValueError.
    The last number or both numbers may be None.
    """
    if byte_range.strip() == "":
        return None, None

    m = BYTE_RANGE_RE.match(byte_range)
    if not m:
        raise ValueError("Invalid byte range %s" % byte_range)

    first, last = [x and int(x) for x in m.groups()]
    if last and last < first:
        raise ValueError("Invalid byte range %s" % byte_range)
    return first, last


def send_file_partial(path):
    range_header = request.headers.get("Range", None)
    if not range_header:
        return send_file(path)

    try:
        byte_range = parse_byte_range(request.headers["Range"])
    except ValueError as error:
        return abort(400, "Invalid byte range")
    first, last = byte_range

    try:
        data = None
        with open(path, "rb") as file_handle:
            fs = os.fstat(file_handle.fileno())
            file_len = fs[6]
            if first >= file_len:
                return abort(416, "Requested Range Not Satisfiable")

            if last is None or last >= file_len:
                last = file_len - 1
            response_length = last - first + 1

            file_handle.seek(first)
            data = file_handle.read(response_length)
    except IOError:
        return abort(404, "File not found")

    resp = Response(data, 206, mimetype=mimetypes.guess_type(path)[0], direct_passthrough=True)

    resp.headers.add("Content-type", "application/octet-stream")
    resp.headers.add("Accept-Ranges", "bytes")
    resp.headers.add("Content-Range", "bytes %s-%s/%s" % (first, last, file_len))
    resp.headers.add("Content-Length", str(response_length))
    return resp
