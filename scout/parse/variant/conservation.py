import logging

from scout.constants import CONSERVATION
import numbers

logger = logging.getLogger(__name__)

def parse_conservations(variant, vep_header=None):
    """Parse the conservation predictors

        Args:
            variant(dict): A variant dictionary
            vep_header(list): CSQ field might contain conservation annotations

        Returns:
            conservations(dict): A dictionary with the conservations
    """
    conservations = {}

    conservation_keys = {
        'info_keys' : {
            'gerp' : 'dbNSFP_GERP___RS',
            'phast' : 'dbNSFP_phastCons100way_vertebrate',
            'phylop' : 'dbNSFP_phyloP100way_vertebrate'
        },
        'csq_keys' : {
            'gerp' : 'GERP++_RS',
            'phast' : 'phastCons100way_vertebrate',
            'phylop' : 'phyloP100way_vertebrate'
        }
    }

    if any(elem in list(conservation_keys['csq_keys'].values()) for elem in vep_header):
        # if CSQ field contains any conservation key specified in conservation_keys['csq_keys']
        logger.info('-------------------------->{}'.format(variant.INFO.get('CSQ')))

    else: # parse conservation from the INFO field
        for key,value in conservation_keys['info_keys'].items():
            conservations[key] = parse_conservation_info(variant,value)

    return conservations


def parse_conservation_info(variant, info_key):
    """Get the conservation prediction from the INFO field

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


def parse_conservation_csq(variant, info_key):
    """Get the conservation prediction from the CSQ field

        Args:
            variant(dict): A variant dictionary
            info_key(str)

        Returns:
            conservations(list): List of censervation terms
    """
    vep_info = variant.INFO.get('CSQ')
