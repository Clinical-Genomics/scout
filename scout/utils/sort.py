from scout.constants import FILE_TYPE_MAP


def get_load_priority(category: str = None, variant_type: str = None, file_type: str = None) -> int:
    """
    Returns most urgent, highest load priority (numerically the lowest prio number) for the given variables
    from a FILE_TYPE_MAP dict of dicts. Helper useful in a sort function.
    """
    ordered_file_type_map = sorted(FILE_TYPE_MAP.items(), key=lambda ftm: ftm[1]["load_priority"])

    for ftm in ordered_file_type_map:
        if file_type and file_type != ftm[0]:
            continue

        if category and category != ftm[1]["category"]:
            continue

        if variant_type and variant_type != ftm[1]["variant_type"]:
            continue

        return ftm[1]["load_priority"]
