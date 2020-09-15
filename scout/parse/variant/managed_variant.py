import logging

LOG = logging.getLogger(__name__)


def parse_managed_variant_id(
    chromosome, position, reference, alternative, category, sub_category, build="37"
):
    """Check if a variant is on the managed_variant list and should be loaded

    All variants on the list will be loaded regardless of the kind of relevance.

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
