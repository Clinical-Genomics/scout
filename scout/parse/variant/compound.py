import logging

from scout.utils.md5 import generate_md5_key

LOG = logging.getLogger(__name__)


def parse_compounds(compound_info, case_id, variant_type):
    """Get a list with compounds objects for this variant.

    Arguments:
        compound_info(str): A Variant dictionary
        case_id (str): unique family id
        variant_type(str): 'research' or 'clinical'

    Returns:
        compounds(list(dict)): A list of compounds
    """
    # We need the case to construct the correct id
    compounds = []
    if compound_info:
        for family_info in compound_info.split(","):
            splitted_entry = family_info.split(":")
            # This is the family id
            if splitted_entry[0] == case_id:
                for compound in splitted_entry[1].split("|"):
                    splitted_compound = compound.split(">")
                    compound_obj = {}
                    compound_name = splitted_compound[0]
                    compound_obj["variant"] = generate_md5_key(
                        compound_name.split("_") + [variant_type, case_id]
                    )

                    try:
                        compound_score = float(splitted_compound[1])
                    except (TypeError, IndexError):
                        compound_score = 0.0

                    compound_obj["score"] = compound_score
                    compound_obj["display_name"] = compound_name

                    compounds.append(compound_obj)

    return compounds
