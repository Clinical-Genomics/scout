import json
import logging

from scout.constants import (
    CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
    CANCER_TIER_OPTIONS,
    DISMISS_VARIANT_OPTIONS,
    MANUAL_RANK_OPTIONS,
    MOSAICISM_OPTIONS,
)
from scout.constants.variant_tags import EVALUATION_TERM_CATEGORIES

LOG = logging.getLogger(__name__)


def _print_loaded(adapter):
    """Display the number of loaded terms by category

    Args:
        adapter(MongoAdapter)
    """
    LOG.debug(
        f'{len(adapter.dismiss_variant_options(["rare","cancer"]).keys())} variant dismissal terms loaded into database.'
    )
    LOG.debug(
        f'{len(adapter.manual_rank_options(["rare","cancer"]).keys())} manual rank terms loaded into database.'
    )
    LOG.debug(f"{len(adapter.cancer_tier_terms().keys())} cancer tier terms loaded into database.")
    LOG.debug(
        f"{len(adapter.mosaicism_options().keys())} mosaicism options terms loaded into database."
    )


def _load_default_terms(adapter, category, tracks, terms):
    """Interact with the database adapter to load evaluation terms in the database

    Args:
        adapter(MongoAdapter)
        category(str): "dismissal_term" or "manual_rank"
        tracks(list): a list of tracks to apply the terms to
        terms(list): example -->
            [
                8: {
                    "label": "KP",
                    "name": "Known pathogenic",
                    "description": "Known pathogenic, previously known pathogenic in ClinVar, HGMD, literature, etc",
                    "label_class": "danger",
                },
                ...
            ]
    """
    for key, term in terms.items():
        adapter.load_evaluation_term(
            category=category, tracks=tracks, term_key=key, term_value=term
        )


def load_default_evaluation_terms(adapter):
    """Load default evaluation terms into database on database setup

    Args:
        adapter(MongoAdapter)
    """
    # Remove all evaluation terms from database
    adapter.drop_evaluation_terms(EVALUATION_TERM_CATEGORIES)

    # Load default dismiss variant terms (rare and cancer tracks)
    _load_default_terms(adapter, "dismissal_term", ["rare", "cancer"], DISMISS_VARIANT_OPTIONS)
    # Load default dismiss variant terms (cancer track)
    _load_default_terms(
        adapter,
        "dismissal_term",
        ["cancer"],
        CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
    )

    # Load manual rank terms (rare and cancer tracks)
    _load_default_terms(adapter, "manual_rank", ["rare", "cancer"], MANUAL_RANK_OPTIONS)

    # Load cancer tier terms (cancer track)
    _load_default_terms(adapter, "cancer_tier", ["cancer"], CANCER_TIER_OPTIONS)

    # Load mosaicism options terms (rare track)
    _load_default_terms(adapter, "mosaicism_option", ["rare"], MOSAICISM_OPTIONS)

    _print_loaded(adapter)


def load_custom_evaluation_terms(adapter, json_file):
    """Load into database custom variant evaluation terms read from a json file

    Args:
        adapter(MongoAdapter)
        json_file(File): a json file containing evaluation terms definitions
    """
    entries = json.load(json_file)
    if not entries:
        LOG.error("Could not find any custom track entry in provided file. Aborting")
        return

    # Remove all evaluation terms from database
    adapter.drop_evaluation_terms(EVALUATION_TERM_CATEGORIES)

    for entry in entries:
        tracks = entry.get("track")
        category = entry.get("category")
        terms = entry.get("terms")

        # Load a single rvaluation term un database
        for term in terms:
            term_key = term.get("key")
            adapter.load_evaluation_term(category, tracks, term_key, term)

    _print_loaded(adapter)
