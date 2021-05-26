import logging

from scout.constants import (
    CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
    DISMISS_VARIANT_OPTIONS,
    MANUAL_RANK_OPTIONS,
)

LOG = logging.getLogger(__name__)


def _load_default_term(adapter, category, terms):
    """Interact with the database adapter that loads a default evaluation term in the database

    Args:
        adapter(MongoAdapter)
        category(str): "dismissal_term" or "manual_rank"
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
        adapter.load_default_evaluation_term(category, key, term)


def _load_default_dismiss_terms(adapter):
    """Load default DISMISS_VARIANT_OPTIONS and CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS into database

    Args:
        adapter(MongoAdapter)
    """
    for terms in [DISMISS_VARIANT_OPTIONS, CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS]:
        _load_default_term(adapter, "dismissal_term", terms)


def _load_defaul_manual_rank_terms(adapter):
    """Load default MANUAL_RANK_OPTIONS into database

    Args:
        adapter(MongoAdapter)
    """
    _load_default_term(adapter, "manual_rank", MANUAL_RANK_OPTIONS)


def load_default_evaluation_terms(adapter):
    """Load default evaluation terms into database on database setup

    Args:
        adapter(MongoAdapter)
    """
    # Load default dismiss variant terms
    _load_default_dismiss_terms(adapter)
    # Load default manual rank terms
    _load_defaul_manual_rank_terms(adapter)
