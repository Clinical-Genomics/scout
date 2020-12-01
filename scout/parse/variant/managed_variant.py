import logging

LOG = logging.getLogger(__name__)

from scout.parse.panel import get_delimiter


def parse_managed_variant_id(
    chromosome, position, reference, alternative, category, sub_category, build="37"
):
    """Construct Managed Variant id for searching.

    Args:
        chromosome,
        position,
        reference,
        alternative,
        category,
        sub_category,
        build,

    Returns:
        managed_variant_id
    """

    return "_".join(
        [
            str(part)
            for part in (
                chromosome,
                position,
                reference,
                alternative,
                category,
                sub_category,
                build,
            )
        ]
    )


def parse_managed_variant_lines(csv_lines):
    """Parse managed variant csv lines into managed variant info dicts.

    Shares implementation structure with panel csv parsing. Could be generalised.

    Args:
        csv_lines(iterable(str))

    Returns:
        list(managed_variant_info(dict)):   A list of variant info dicts,
            possibly with the following header keys:
                chromosome,
                position,
                end,
                reference,
                alternative,
                build,
                maintainer,
                institute,
                category,
                sub_category,
                description,
    """

    managed_variant_info_dicts = []

    delimiter = "\t"

    for i, line in enumerate(csv_lines):
        line = line.rstrip()

        if line.startswith("##") or len(line) < 1:
            continue

        if line.startswith("#"):
            delimiter = get_delimiter(line)
            header = [word.lower() for word in line[1:].split(delimiter)]
            continue

        if i == 0:
            delimiter = get_delimiter(line)
            header = [word.lower() for word in line[0:].split(delimiter)]
            continue

        managed_variant_info = dict(zip(header, line.split(delimiter)))

        # There are cases when excel exports empty lines
        if not any(managed_variant_info.values()):
            continue

        managed_variant_info_dicts.append(managed_variant_info)

    return managed_variant_info_dicts
