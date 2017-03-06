import logging

from datetime import datetime

from scout.parse.hpo import parse_hpo_phenotypes
from scout.parse.omim import get_mim_phenotypes
from scout.build.hpo import build_hpo_term
from scout.build.disease import build_disease_term

from pprint import pprint as pp

logger = logging.getLogger(__name__)


def load_hpo(adapter, hpo_lines, disease_lines):
    """Load the hpo terms and hpo diseases into database
    
    Args:
        adapter(MongoAdapter)
        hpo_lines(iterable(str))
        disease_lines(iterable(str))
    """
    genes = adapter.hgncsymbol_to_gene()
    
    load_hpo_terms(adapter, hpo_lines, genes)
    
    load_disease_terms(adapter, disease_lines, genes)

def load_hpo_terms(adapter, hpo_lines, genes):
    """Load the hpo terms into the database
    
    Parse the hpo lines, build the objects and add them to the database
    
    Args:
        adapter(MongoAdapter)
        hpo_lines(iterable(str))
    """
    hpo_terms = parse_hpo_phenotypes(hpo_lines)

    start_time = datetime.now()

    logger.info("Loading the hpo terms...")
    for nr_terms, hpo_id in enumerate(hpo_terms):
        hpo_info = hpo_terms[hpo_id]
        hpo_obj = build_hpo_term(hpo_info, genes)
        
        adapter.load_hpo_term(hpo_obj)
    
    logger.info("Loading done. Nr of terms loaded {0}".format(nr_terms))
    logger.info("Time to load terms: {0}".format(datetime.now() - start_time))


def load_disease_terms(adapter, genemap_lines, genes):
    """Load the hpo phenotype terms into the database

    Args:
        adapter(MongoAdapter)
        genemap_lines(iterable(str))
    """

    disease_terms = get_mim_phenotypes(genemap_lines=genemap_lines)

    start_time = datetime.now()

    logger.info("Loading the hpo disease...")
    for nr_diseases, disease_id in enumerate(disease_terms):
        disease_info = disease_terms[disease_id]
        disease_obj = build_disease_term(disease_info, genes)

        adapter.load_disease_term(disease_obj)
    
    logger.info("Loading done. Nr of diseases loaded {0}".format(nr_diseases))
    logger.info("Time to load diseases: {0}".format(datetime.now() - start_time))
    