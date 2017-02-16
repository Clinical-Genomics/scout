# -*- coding: utf-8 -*-
import logging

import operator

logger = logging.getLogger(__name__)


class HpoHandler(object):

    def load_hpo_term(self, hpo_obj):
        """Add a hpo object

        Arguments:
            hpo_obj(dict)

        """
        self.mongoengine_adapter.load_hpo_term(
            hpo_obj = hpo_obj
        )

    def hpo_term(self, hpo_id):
        """Fetch a hpo term"""
        return self.mongoengine_adapter.hpo_term(
            hpo_id = hpo_id
        )

    def hpo_terms(self, query=None):
        """Return all HPO terms"""
        return self.mongoengine_adapter.hpo_terms(
            query = query
        )

    def disease_terms(self, hgnc_id=None):
        """Return all disease terms that overlaps a gene

            If no gene, return all disease terms
        """
        return self.mongoengine_adapter.disease_terms(
            hgnc_id = hgnc_id
        )

    def load_disease_term(self, disease_obj):
        """Load a disease term into the database"""
        self.mongoengine_adapter.load_disease_term(
            disease_obj = disease_obj
        )

    def generate_hpo_gene_list(self, *hpo_terms):
        """Generate a sorted list with namedtuples of hpogenes

            Each namedtuple of the list looks like (hgnc_id, count)

            Args:
                hpo_terms(iterable(str))

            Returns:
                hpo_genes(list(HpoGene))
        """
        return self.mongoengine_adapter.generate_hpo_gene_list(
            hpo_terms = hpo_terms
        )
