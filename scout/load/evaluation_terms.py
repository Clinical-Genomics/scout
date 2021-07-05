import json
import logging

from scout.constants.variant_tags import EVALUATION_TERM_CATEGORIES
from scout.resources import default_evaluations_file_path

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


def load_default_evaluation_terms(adapter):
    """Load default variant evaluation terms stored in json resource file

    Args:
        adapter(MongoAdapter)
    """
    with open(default_evaluations_file_path) as json_file:
        load_evaluation_terms_from_file(adapter, json_file)


def load_evaluation_terms_from_file(adapter, json_file):
    """Load into database custom variant evaluation terms read from a json file

    Args:
        adapter(MongoAdapter)
        json_file(File): a json file containing evaluation terms definitions
    """
    entries = json.load(json_file)
    if not entries:
        LOG.error("Could not find any custom track entry in provided file. Aborting")
        return

    # Remove all evaluation terms from database first
    adapter.drop_evaluation_terms(EVALUATION_TERM_CATEGORIES)

    for entry in entries:
        tracks = entry.get("track")
        category = entry.get("category")
        terms = entry.get("terms")

        # Load a single evaluation terms into database
        for term in terms:
            term_key = term.get("key")
            adapter.load_evaluation_term(category, tracks, term_key, term)

    _print_loaded(adapter)
