from scout.constants import CONSERVATION
import numbers

def parse_conservations(variant):
    """Parse the conservation predictors

        Args:
            variant(dict): A variant dictionary

        Returns:
            conservations(dict): A dictionary with the conservations
    """
    conservations = {}

    conservations['gerp'] = parse_conservation(
                                            variant,
                                            'dbNSFP_GERP___RS'
                                        )
    conservations['phast'] = parse_conservation(
                                            variant,
                                            'dbNSFP_phastCons100way_vertebrate'
                                        )
    conservations['phylop'] = parse_conservation(
                                            variant,
                                            'dbNSFP_phyloP100way_vertebrate'
                                        )
    return conservations

def parse_conservation(variant, info_key):
    """Get the conservation prediction

        Args:
            variant(dict): A variant dictionary
            info_key(str)

        Returns:
            conservations(list): List of censervation terms
    """
    raw_score = variant.INFO.get(info_key)
    conservations = []

    if raw_score:
        if isinstance(raw_score, numbers.Number):
            raw_score = (raw_score,)

        for score in raw_score:
            if score >= CONSERVATION[info_key]['conserved_min']:
                conservations.append('Conserved')
            else:
                conservations.append('NotConserved')

    return conservations
