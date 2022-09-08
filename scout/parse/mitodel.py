from scout.utils.convert import convert_number, make_bool_pass_none


def parse_mitodel_file(lines):
    """Parse a mitodel TXT file.

    Args:
        lines(iterable(str))

    Returns:
        list(sma_info_per_individual(dict))
    """
    individuals = []
    header = []

    for i, line in enumerate(lines):
        line = line.rstrip()
        if i == 0:
            # Header line
            header = line.split("\t")
        else:
            ind_mitodel_info = dict(zip(header, line.split("\t")))

            individuals.append(ind_mitodel_info)

    return individuals
