"""Code for parsing conservation"""

import logging
import numbers
from typing import List

from scout.constants import CONSERVATION

LOG = logging.getLogger(__name__)


def parse_conservations(variant: dict, parsed_transcripts: List[dict] = None) -> dict:
    """Parse the conservation predictors

    Args:
        variant(dict): A variant dictionary
        parsed_transcripts(list): if provided, use transcript annotations

    Returns:
        conservations(dict): A dictionary with the conservations
    """
    parsed_transcripts = parsed_transcripts or []
    conservations = {}

    conservation_keys = {
        "gerp": "dbNSFP_GERP___RS",
        "phast": "dbNSFP_phastCons100way_vertebrate",
        "phylop": "dbNSFP_phyloP100way_vertebrate",
    }

    # First check if information is in INFO
    for key, value in conservation_keys.items():
        result = None
        if value and variant.INFO.get(value):
            result = parse_conservation_info(variant, value, key)
        elif len(parsed_transcripts) > 0:
            result = parse_conservation_csq(parsed_transcripts[0], key)

        conservations[key] = result

    return conservations


def parse_conservation_info(variant: dict, info_key: str, field_key: str) -> List[str]:
    """Get the conservation prediction from the INFO field

    Args:
        variant(dict): A variant dictionary
        info_key(str): 'dbNSFP_GERP___RS', 'dbNSFP_phastCons100way_vertebrate' or
            'phyloP100way_vertebrate'
        field_key(str): 'gerp', 'phast' or 'phylop'

    Returns:
        conservations(list): List of conservation terms
    """
    raw_score = variant.INFO.get(info_key)
    conservations = []

    if raw_score:
        if isinstance(raw_score, numbers.Number):
            raw_score = (raw_score,)

        for score in raw_score:
            if score >= CONSERVATION[field_key]["conserved_min"]:
                conservations.append(f"Conserved ({round(score,2)})")
            else:
                conservations.append(f"NotConserved ({round(score,2)})")

    return conservations


def parse_conservation_csq(transcript: dict, field_key: str) -> List[str]:
    """Get the conservation prediction from a transcript

    Args:
        transcript(dict): One parsed transcripts
        field_key(str): 'gerp', 'phast' or 'phylop'

    Returns:
        conservations(list): List of censervation terms
    """
    conservations = []

    try:
        scores = transcript.get(field_key)
        if not scores:
            return conservations

        for score in scores.split("&"):
            # fields may consist of multiple numeric values
            score = float(score)
            if score >= CONSERVATION[field_key]["conserved_min"]:
                conservations.append(f"Conserved ({round(score,2)})")
            else:
                conservations.append(f"NotConserved ({round(score,2)})")
    except ValueError:
        LOG.warning("Error while parsing %s value:%s ", field_key, transcript.get(field_key))

    return conservations
