import re

from scout.utils.convert import convert_number


def parse_mitodel_file(lines):
    """Parse a mitodel TXT file.

    Args:
        lines(iterable(str))

    Returns:
        list(mitodel_info_for_individual(dict))
    """

    for i, line in enumerate(lines):
        line = line.rstrip()

        HEADER = ["intermediate discordant", "normal", "ratio ppk"]
        contents = re.match(
            HEADER[0] + r"\s+(\d+)\s+" + HEADER[1] + r"\s+(\d+)\s+" + HEADER[2] + r"\s+([0-9.]+)",
            line,
        )

        HEADER_ABBREV = ["discordant", "normal", "ratioppk"]
        ind_mitodel_info = dict(zip(HEADER_ABBREV, contents.groups()))

        for field in HEADER_ABBREV:
            ind_mitodel_info[field] = convert_number(ind_mitodel_info[field])

    return ind_mitodel_info
