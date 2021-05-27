import logging

from scout.constants import (
    CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
    CANCER_TIER_OPTIONS,
    DISMISS_VARIANT_OPTIONS,
    MANUAL_RANK_OPTIONS,
    MOSAICISM_OPTIONS,
)

LOG = logging.getLogger(__name__)


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
        adapter.load_default_evaluation_term(
            category=category, tracks=tracks, term_key=key, term_value=term
        )


def load_default_evaluation_terms(adapter):
    """Load default evaluation terms into database on database setup

    Args:
        adapter(MongoAdapter)
    """
    # Load default dismiss variant terms (rare and cancer tracks)
    _load_default_terms(adapter, "dismissal_term", ["rare", "cancer"], DISMISS_VARIANT_OPTIONS)
    # Load default dismiss variant terms (cancer track)
    _load_default_terms(
        adapter,
        "dismissal_term",
        ["cancer"],
        CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
    )
    LOG.debug(
        f'{len(adapter.dismiss_variant_options(["rare","cancer"]).keys())} variant dismissal terms loaded into database.'
    )

    # Load manual rank terms (rare and cancer tracks)
    _load_default_terms(adapter, "manual_rank", ["rare", "cancer"], MANUAL_RANK_OPTIONS)
    LOG.debug(
        f'{len(adapter.manual_rank_options(["rare","cancer"]).keys())} manual rank terms loaded into database.'
    )

    # Load cancer tier terms (cancer track)
    _load_default_terms(adapter, "cancer_tier", ["cancer"], CANCER_TIER_OPTIONS)
    LOG.debug(f"{len(adapter.cancer_tier_terms().keys())} cancer tier terms loaded into database.")

    # Load mosaicism options terms (rare track)
    _load_default_terms(adapter, "mosaicism_options", ["rare"], MOSAICISM_OPTIONS)
    LOG.debug(
        f"{len(adapter.mosaicism_options().keys())} mosaicism options terms loaded into database."
    )
