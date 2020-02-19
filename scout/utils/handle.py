from codecs import open, getreader
import gzip


def get_file_handle(file_path):
    """Return a opened file"""

    if file_path.endswith(".gz"):
        file_handle = getreader("utf-8")(gzip.open(file_path, "r"), errors="replace")
    else:
        file_handle = open(file_path, "r", encoding="utf-8")

    return file_handle
