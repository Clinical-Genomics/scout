import logging

from datetime import datetime

from scout.parse.hpo import (parse_hpo_phenotypes, parse_hpo_diseases)
from scout.parse.omim import get_mim_phenotypes
from scout.build.hpo import build_hpo_term
from scout.build.disease import build_disease_term

from pprint import pprint as pp

logger = logging.getLogger(__name__)


def load_hpo(adapter, hpo_lines, disease_lines, hpo_disease_lines):
    """Load the hpo terms and hpo diseases into database
    
    Args:
        adapter(MongoAdapter)
        hpo_lines(iterable(str))
        disease_lines(iterable(str))
    """
    alias_genes = adapter.genes_by_alias()
    
    load_hpo_terms(adapter, hpo_lines, alias_genes)
    
    load_disease_terms(adapter, disease_lines, alias_genes, hpo_disease_lines)

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


def load_disease_terms(adapter, genemap_lines, genes, hpo_disease_lines):
    """Load the omim phenotypes into the database
    
    Parse the phenotypes from genemap2.txt and find the associated hpo terms
    from ALL_SOURCES_ALL_FREQUENCIES_diseases_to_genes_to_phenotypes.txt.

    Args:
        adapter(MongoAdapter)
        genemap_lines(iterable(str))
        genes(dict): Dictionary with all genes found in database
        hpo_disease_lines(iterable(str))

    """

    disease_terms = get_mim_phenotypes(genemap_lines=genemap_lines)
    hpo_diseases = parse_hpo_diseases(hpo_disease_lines)

    start_time = datetime.now()

    logger.info("Loading the hpo disease...")
    for nr_diseases, disease_number in enumerate(disease_terms):
        disease_info = disease_terms[disease_number]
        disease_id = "OMIM:{0}".format(disease_number)
        
        if disease_id in hpo_diseases:
            hpo_terms = hpo_diseases[disease_id]['hpo_terms']
            if hpo_terms:
                disease_info['hpo_terms'] = hpo_terms
        disease_obj = build_disease_term(disease_info, genes)

        adapter.load_disease_term(disease_obj)
    
    logger.info("Loading done. Nr of diseases loaded {0}".format(nr_diseases))
    logger.info("Time to load diseases: {0}".format(datetime.now() - start_time))
    