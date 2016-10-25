import logging

from scout.utils.md5 import generate_md5_key

logger = logging.getLogger(__name__)

def parse_compounds(variant, case, variant_type):
    """Get a list with mongoengine compounds for this variant.

        Arguments:
            variant(dict): A Variant dictionary
            case(Case)
            variant_type(str): 'research' or 'clinical'

        Returns:
            compounds(list(dict)): A list of compounds
    """
    # We need the case to construct the correct id
    case_id = case['case_id']
    case_name = case['display_name']
    compounds = []

    for compound in variant['compound_variants'].get(case_name, []):
        compound_obj = {}

        compound_name = compound['variant_id']
        # The compound id have to match the document id
        compound_obj['variant'] = generate_md5_key(compound_name.split('_') +
                                   [variant_type] +
                                   case_id.split('_'))
        try:
            compound_score = float(compound['compound_score'])
        except TypeError:
            compound_score = 0.0

        compound_obj['score'] = compound_score
        compound_obj['display_name'] = compound_name

        compounds.append(compound_obj)

    return compounds

