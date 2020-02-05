from scout.utils.md5 import generate_md5_key


def parse_ids(chrom, pos, ref, alt, case_id, variant_type):
    """Construct the necessary ids for a variant

    Args:
        chrom(str): Variant chromosome
        pos(int): Variant position
        ref(str): Variant reference
        alt(str): Variant alternative
        case_id(str): Unique case id
        variant_type(str): 'clinical' or 'research'

    Returns:
        ids(dict): Dictionary with the relevant ids
    """
    ids = {}
    pos = str(pos)

    ids["simple_id"] = parse_simple_id(chrom, pos, ref, alt)
    ids["variant_id"] = parse_variant_id(chrom, pos, ref, alt, variant_type)
    ids["display_name"] = parse_display_name(chrom, pos, ref, alt, variant_type)
    ids["document_id"] = parse_document_id(chrom, pos, ref, alt, variant_type, case_id)

    return ids


def parse_simple_id(chrom, pos, ref, alt):
    """Parse the simple id for a variant

    Simple id is used as a human readable reference for a position, it is
    in no way unique.

    Args:
        chrom(str)
        pos(str)
        ref(str)
        alt(str)

    Returns:
        simple_id(str): The simple human readable variant id
    """
    return "_".join([chrom, pos, ref, alt])


def parse_variant_id(chrom, pos, ref, alt, variant_type):
    """Parse the variant id for a variant

    variant_id is used to identify variants within a certain type of
    analysis. It is not human readable since it is a md5 key.

    Args:
        chrom(str)
        pos(str)
        ref(str)
        alt(str)
        variant_type(str): 'clinical' or 'research'

    Returns:
        variant_id(str): The variant id converted to md5 string
    """
    return generate_md5_key([chrom, pos, ref, alt, variant_type])


def parse_display_name(chrom, pos, ref, alt, variant_type):
    """Parse the variant id for a variant

    This is used to display the variant in scout.

    Args:
        chrom(str)
        pos(str)
        ref(str)
        alt(str)
        variant_type(str): 'clinical' or 'research'

    Returns:
        variant_id(str): The variant id in human readable format
    """
    return "_".join([chrom, pos, ref, alt, variant_type])


def parse_document_id(chrom, pos, ref, alt, variant_type, case_id):
    """Parse the unique document id for a variant.

    This will always be unique in the database.

    Args:
        chrom(str)
        pos(str)
        ref(str)
        alt(str)
        variant_type(str): 'clinical' or 'research'
        case_id(str): unqiue family id

    Returns:
        document_id(str): The unique document id in an md5 string
    """
    return generate_md5_key([chrom, pos, ref, alt, variant_type, case_id])
