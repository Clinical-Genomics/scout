import logging

from datetime import datetime

from scout.parse.hpo import (parse_hpo_phenotypes, parse_hpo_diseases)
from scout.build import (build_hpo_term, build_disease_term)

from pprint import pprint as pp

logger = logging.getLogger(__name__)


def load_hpo(adapter, hpo_lines, disease_lines):
    """Load the hpo terms and hpo diseases into database
    
        Args:
            adapter(MongoAdapter)
            hpo_lines(iterable(str))
            disease_lines(iterable(str))
    """
    gene_objs = {}
    for gene in adapter.all_genes():
        gene_objs[gene.hgnc_symbol] = gene

    logger.info("All genes fetched")
    
    load_hpo_terms(adapter, hpo_lines, gene_objs)
    
    load_disease_terms(adapter, disease_lines, gene_objs)

def load_hpo_terms(adapter, hpo_lines, gene_objs):
    """Load the hpo terms into the database
    
        Args:
            adapter(MongoAdapter)
            hpo_lines(iterable(str))
    """
    hpo_terms = parse_hpo_phenotypes(hpo_lines)

    start_time = datetime.now()

    logger.info("Loading the hpo terms...")
    for nr_terms, hpo_id in enumerate(hpo_terms):
        hpo_info = hpo_terms[hpo_id]
        hpo_obj = build_hpo_term(hpo_info)
        
        hgnc_ids = []
        for hgnc_symbol in hpo_info['hgnc_symbols']:
            if hgnc_symbol in gene_objs:
                gene_obj = gene_objs[hgnc_symbol]
                hgnc_ids.append(gene_obj.hgnc_id)
        hpo_obj.genes = hgnc_ids
        adapter.load_hpo_term(hpo_obj)
    
    logger.info("Loading done. Nr of terms loaded {0}".format(nr_terms))
    logger.info("Time to load terms: {0}".format(datetime.now() - start_time))


def load_disease_terms(adapter, hpo_disease_lines, gene_objs):
    """Load the hpo phenotype terms into the database

        Args:
            adapter(MongoAdapter)
            hpo_lines(iterable(str))
    """

    mim_terms = parse_hpo_diseases(hpo_disease_lines)

    start_time = datetime.now()

    logger.info("Loading the hpo disease...")
    for nr_diseases, disease_id in enumerate(mim_terms):
        disease_info = mim_terms[disease_id]
        disease_obj = build_disease_term(disease_info)
        
        hgnc_ids = []
        for hgnc_symbol in disease_info['hgnc_symbols']:
            if hgnc_symbol in gene_objs:
                gene_obj = gene_objs[hgnc_symbol]
                hgnc_ids.append(gene_obj.hgnc_id)
        
        disease_obj.genes = hgnc_ids
        
        adapter.load_disease_term(disease_obj)
    
    logger.info("Loading done. Nr of diseases loaded {0}".format(nr_diseases))
    logger.info("Time to load diseases: {0}".format(datetime.now() - start_time))
    