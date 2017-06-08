# -*- coding: utf-8 -*-
import logging

import operator

from pymongo.errors import DuplicateKeyError

from scout.exceptions import IntegrityError

log = logging.getLogger(__name__)


class HpoHandler(object):

    def load_hpo_term(self, hpo_obj):
        """Add a hpo object

        Arguments:
            hpo_obj(dict)

        """
        log.debug("Loading hpo term %s into database", hpo_obj['_id'])
        try:
            self.hpo_term_collection.insert_one(hpo_obj)
        except DuplicateKeyError as err:
            raise IntegrityError("Hpo term %s already exists in database".format(hpo_obj['_id']))
        log.debug("Hpo term saved")

    def hpo_term(self, hpo_id):
        """Fetch a hpo term

        Args:
            hpo_id(str)

        Returns:
            hpo_obj(dict)
        """
        log.debug("Fetching hpo term %s", hpo_id)

        return self.hpo_term_collection.find_one({'_id': hpo_id})

    def hpo_terms(self, query=None):
        """Return all HPO terms

        If a query is sent hpo_terms will try to match with regex on term or
        description.

        Args:
            query(str): Part of a hpoterm or description

        Returns:
            result(pymongo.Cursor): A cursor with hpo terms
        """
        if query:
            query_dict = {'$or':
                [
                    {'_id': {'$regex': query, '$options':'i'}},
                    {'description': {'$regex': query, '$options':'i'}},
                ]
            }
        else:
            query_dict = {}

        return self.hpo_term_collection.find(query_dict)

    def disease_term(self, disease_identifier):
        """Return a disease term

        Checks if the identifier is a disease number or a id

        Args:
            disease_identifier(str)

        Returns:
            disease_obj(dict)
        """
        query = {}
        try:
            disease_identifier = int(disease_identifier)
            query['disease_nr'] = disease_identifier
        except ValueError:
            query['_id'] = disease_identifier

        return self.disease_term_collection.find_one(query)

    def disease_terms(self, hgnc_id=None):
        """Return all disease terms that overlaps a gene

            If no gene, return all disease terms
        
        Args:
            hgnc_id(int)
        
        Returns:
            iterable(dict): A list with all disease terms that match
        """
        query = {}
        if hgnc_id:
            log.info("Fetching all diseases for gene %s", hgnc_id)
            query['genes'] = hgnc_id
        else:
            log.info("Fetching all disease terms")

        return list(self.disease_term_collection.find(query))

    def load_disease_term(self, disease_obj):
        """Load a disease term into the database

        Args:
            disease_obj(dict)
        """
        log.debug("Loading disease term %s into database", disease_obj['_id'])
        try:
            self.disease_term_collection.insert_one(disease_obj)
        except DuplicateKeyError as err:
            raise IntegrityError("Disease term %s already exists in database".format(disease_obj['_id']))

        log.debug("Disease term saved")

    def generate_hpo_gene_list(self, *hpo_terms):
        """Generate a sorted list with namedtuples of hpogenes

            Each namedtuple of the list looks like (hgnc_id, count)

            Args:
                hpo_terms(iterable(str))

            Returns:
                hpo_genes(list(HpoGene))
        """
        genes = {}
        for term in hpo_terms:
            hpo_obj = self.hpo_term(term)
            if hpo_obj:
                for hgnc_id in hpo_obj['genes']:
                    if hgnc_id in genes:
                        genes[hgnc_id] += 1
                    else:
                        genes[hgnc_id] = 1
            else:
                log.warning("Term %s could not be found", term)

        sorted_genes = sorted(genes.items(), key=operator.itemgetter(1), reverse=True)
        return sorted_genes
