from scout.utils.convert import convert_number, make_bool_pass_none


def parse_mitodel_file(lines):
    """Parse a mitodel TXT file.

    Args:
        lines(iterable(str))

    Returns:
        list(sma_info_per_individual(dict))
    """
    individuals = []

    for i, line in enumerate(lines):
        line = line.rstrip()

        HEADER = ["intermediate discordant", "normal", "ratio ppk"]
        contents = re.match(
            HEADER[0] + r"\s+(\d+)\s+" + HEADER[1] + r"\s+(\d+)\s+" + HEADER[2] + r"\s+([0-9.]+)"
        )

        ind_mitodel_info = dict(zip(HEADER, contents.groups()))
        individuals.append(ind_mitodel_info)

    return individuals
