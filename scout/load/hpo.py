import logging

from scout.parse import parse_hpo_phenotypes
from scout.build import build_hpo_term

logger = logging.getLogger(__name__)


def load_hpo_terms(adapter, hpo_lines):
    """Load the hpo terms into the database
    
        Args:
            adapter(MongoAdapter)
            hpo_lines(iterable(str))
    """
    from pprint import pprint as pp
    
    hpo_terms = parse_hpo_phenotypes(hpo_lines)
    
    logger.info("Loading the hpo terms...")
    for hgnc_id in hpo_terms:
        hpo_info = hpo_terms[hgnc_id]
        pp(hpo_info)
        hpo_obj = build_hpo_term(adapter, hpo_info)
        print(hpo_obj)
        #
        # adapter.load_hpo_term(hpo_obj)
    
    logger.info("Loading done.")


# def load_disease_terms(adapter, hpo_disease_lines):
#     """Load the hpo terms into the database
#
#         Args:
#             adapter(MongoAdapter)
#             hpo_lines(iterable(str))
#     """
#
#     hpo_terms = parse_hpo_phenotypes(hpo_lines)
#
#     for hgnc_id in hpo_terms:
#         hpo_info = hpo_terms[hgnc_id]
#
#         hpo_obj = build_hpo_term(adapter, hpo_info)
#
#         adapter.load_hpo_term(hpo_obj)