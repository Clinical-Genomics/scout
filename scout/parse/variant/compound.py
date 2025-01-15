import logging
from typing import List

from scout.utils.md5 import generate_md5_key

LOG = logging.getLogger(__name__)


def parse_compounds(compound_info: str, case_id: str, variant_type: str) -> List[dict]:
    """Get a list with compounds objects(dicts) for this variant.

    Scout IDs do not have "chr" prefixed chromosome names, hence we lstrip that from
    any compound names.

    We need the case id to construct the correct id, as well as the variant type (clinical or research).

    """

    compounds = []
    if compound_info:
        for family_info in compound_info.split(","):
            split_entry = family_info.split(":")
            # This is the family id
            if split_entry[0] == case_id:
                for compound in split_entry[1].split("|"):
                    split_compound = compound.split(">")
                    compound_name = split_compound[0].lstrip("chr")
                    compound_obj = {
                        "display_name": compound_name,
                        "variant": generate_md5_key(
                            compound_name.split("_") + [variant_type, case_id]
                        ),
                    }

                    try:
                        compound_score = float(split_compound[1])
                    except (TypeError, IndexError):
                        compound_score = 0.0
                    compound_obj["score"] = compound_score

                    compounds.append(compound_obj)

    return compounds
