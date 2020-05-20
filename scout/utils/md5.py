# encoding: utf-8
import hashlib
from six import string_types


def generate_md5_key(list_of_arguments):
    """
    Generate an md5-key from a list of arguments.

    Args:
        list_of_arguments: A list of strings

    Returns:
        A md5-key object generated from the list of strings.
    """
    for arg in list_of_arguments:
        if not isinstance(arg, string_types):
            raise SyntaxError(
                "Error in generate_md5_key: " "Argument: {0} is a {1}".format(arg, type(arg))
            )

    hash_obj = hashlib.md5()
    hash_obj.update(" ".join(list_of_arguments).encode("utf-8"))
    return hash_obj.hexdigest()
