def remove_nonetype(dictionary):
    """If value = None in key/value pair, the pair is removed.
        Python >3
    Args:
        dictionary: dict

    Returns:
        dict
    """

    return {k: v for k, v in dictionary.items() if v is not None}
