# -*- coding: utf-8 -*-
import logging

import operator

from pymongo.errors import (DuplicateKeyError, BulkWriteError)
from pymongo import (ASCENDING)

from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)


class HpoHandler(object):

    def load_hpo_term(self, hpo_obj):
        """Add a hpo object

        Arguments:
            hpo_obj(dict)

        """
        LOG.debug("Loading hpo term %s into database", hpo_obj['_id'])
        try:
            self.hpo_term_collection.insert_one(hpo_obj)
        except DuplicateKeyError as err:
            raise IntegrityError("Hpo term %s already exists in database".format(hpo_obj['_id']))
        LOG.debug("Hpo term saved")

    def load_hpo_bulk(self, hpo_bulk):
        """Add a hpo object

        Arguments:
            hpo_bulk(list(scout.models.HpoTerm))

        Returns:
            result: pymongo bulkwrite result

        """
        LOG.debug("Loading hpo bulk")

        try:
            result = self.hpo_term_collection.insert_many(hpo_bulk)
        except (DuplicateKeyError, BulkWriteError) as err:
            raise IntegrityError(err)
        return result

    def hpo_term(self, hpo_id):
        """Fetch a hpo term

        Args:
            hpo_id(str)

        Returns:
            hpo_obj(dict)
        """
        LOG.debug("Fetching hpo term %s", hpo_id)

        return self.hpo_term_collection.find_one({'_id': hpo_id})

    def hpo_terms(self, query=None, hpo_term=None, text=None, limit=None):
        """Return all HPO terms

        If a query is sent hpo_terms will try to match with regex on term or
        description.

        Args:
            query(str): Part of a hpoterm or description
            hpo_term(str): Search for a specific hpo term
            limit(int): the number of desired results

        Returns:
            result(pymongo.Cursor): A cursor with hpo terms
        """
        query_dict = {}
        search_term = None
        if query:
            query_dict = {'$or':
                [
                    {'hpo_id': {'$regex': query, '$options':'i'}},
                    {'description': {'$regex': query, '$options':'i'}},
                ]   
            }
            search_term = query
        elif text:
            new_string = ''
            for i,word in enumerate(text.split(' ')):
                if i == 0:
                    new_string += word
                else:
                    new_string += ' \"{0}\"'.format(word)
            LOG.info("Search HPO terms with %s", new_string)
            query_dict['$text'] = {'$search': new_string}
            search_term = text
        elif hpo_term:
            query_dict['hpo_id'] = hpo_term
            search_term = hpo_term

        limit = limit or int(10e10)
        res = self.hpo_term_collection.find(query_dict).limit(limit).sort('hpo_number',ASCENDING)
        

        LOG.info("Found {0} terms with search word {1}".format(res.count(), search_term))
        return res

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
            LOG.debug("Fetching all diseases for gene %s", hgnc_id)
            query['genes'] = hgnc_id
        else:
            LOG.info("Fetching all disease terms")

        return list(self.disease_term_collection.find(query))

    def load_disease_term(self, disease_obj):
        """Load a disease term into the database

        Args:
            disease_obj(dict)
        """
        LOG.debug("Loading disease term %s into database", disease_obj['_id'])
        try:
            self.disease_term_collection.insert_one(disease_obj)
        except DuplicateKeyError as err:
            raise IntegrityError("Disease term %s already exists in database".format(disease_obj['_id']))

        LOG.debug("Disease term saved")

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
                LOG.warning("Term %s could not be found", term)

        sorted_genes = sorted(genes.items(), key=operator.itemgetter(1), reverse=True)
        return sorted_genes
