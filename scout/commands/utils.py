from codecs import open
import gzip


def get_file_handle(file_path):
    """Return a opened file"""
    
    if file_path.endswith('.gz'):
        file_handle = gzip.open(file_path, 'r')
    else:
        file_handle = open(file_path, 'r')
    
    return file_handle
    