# -*- coding: utf-8 -*-
import logging
import operator

import pymongo
from anytree import Node, RenderTree, resolver, search
from anytree.exporter import DictExporter
from pymongo.errors import BulkWriteError, DuplicateKeyError

from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)


class HpoHandler(object):
    def load_hpo_term(self, hpo_obj):
        """Add a hpo object

        Arguments:
            hpo_obj(dict)

        """
        LOG.debug("Loading hpo term %s into database", hpo_obj["_id"])
        try:
            self.hpo_term_collection.insert_one(hpo_obj)
        except DuplicateKeyError as err:
            raise IntegrityError("Hpo term %s already exists in database".format(hpo_obj["_id"]))
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

        return self.hpo_term_collection.find_one({"_id": hpo_id})

    def hpo_terms(self, query=None, hpo_term=None, text=None, limit=None, skip=None):
        """Return all HPO terms

        If a query is sent hpo_terms will try to match with regex on term or
        description.

        Args:
            query(str): Part of a hpoterm or description
            hpo_term(str): Search for a specific hpo term
            limit(int): the number of desired results
            skip(int): the number of results to skip

        Returns:
            result(pymongo.Cursor): A cursor with hpo terms
        """
        query_dict = {}
        search_term = None
        if query:
            query_dict = {
                "$or": [
                    {"hpo_id": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                ]
            }
            search_term = query
        elif text:
            new_string = ""
            for i, word in enumerate(text.split(" ")):
                if i == 0:
                    new_string += word
                else:
                    new_string += ' "{0}"'.format(word)
            LOG.info("Search HPO terms with %s", new_string)
            query_dict["$text"] = {"$search": new_string}
            search_term = text
        elif hpo_term:
            query_dict["hpo_id"] = hpo_term
            search_term = hpo_term

        limit = limit or 0
        skip = skip or 0
        res = (
            self.hpo_term_collection.find(query_dict)
            .skip(skip)
            .limit(limit)
            .sort("hpo_number", pymongo.ASCENDING)
        )

        return res

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
                for hgnc_id in hpo_obj["genes"]:
                    if hgnc_id in genes:
                        genes[hgnc_id] += 1
                    else:
                        genes[hgnc_id] = 1
            else:
                LOG.warning("Term %s could not be found", term)

        sorted_genes = sorted(genes.items(), key=operator.itemgetter(1), reverse=True)
        return sorted_genes

    def organize_tree(self, all_terms, root):
        """Organizes a set of Tree node objects into a tree, according to their ancestors and children

        Args:
            all_terms(dict): a dictionary with "term_name" as keys and term_dict as values
            root(anytree.Node)
        Returns
            root(anytree.Node): the updated root node of the tree
        """
        # Move tree nodes in the right position according to the ontology
        for key, term in all_terms.items():
            ancestors = term["ancestors"]
            if len(ancestors) == 0:
                continue
            for ancestor in ancestors:
                ancestor_node = search.find_by_attr(root, ancestor)
                if ancestor_node is None:  # It's probably the term on the top
                    continue
                node = search.find_by_attr(root, key)
                node.parent = ancestor_node
        return root

    def build_phenotype_tree(self, hpo_id):
        """Creates an HPO Tree based on one or more given ancestors
        Args:
            hpo_id(str): an HPO term
        Returns:
            tree_dict(dict): a tree of all HPO children of the given term, as a dictionary
        """
        root = Node(id="root", name="root", parent=None)
        all_terms = {}
        unique_terms = set()

        def _hpo_terms_list(hpo_ids):
            for term_id in hpo_ids:
                term_obj = self.hpo_term(term_id)
                if term_obj is None:
                    continue
                # sort term children by ascending HPO number
                children = sorted(
                    term_obj["children"],
                    key=lambda x: int("".join([i for i in x if i.isdigit()])),
                )
                term_obj["children"] = children
                all_terms[term_id] = term_obj
                if term_id not in unique_terms:
                    node = Node(term_id, parent=root, description=term_obj["description"])
                    unique_terms.add(term_id)
                # recursive loop to collect children, children of children and so on
                _hpo_terms_list(term_obj["children"])

        # compile a list of all HPO term objects to include in the submodel
        _hpo_terms_list([hpo_id])  # trigger the recursive loop to collect nested HPO terms
        # rearrange tree according to the HPO ontology
        root = self.organize_tree(all_terms, root)
        node_resolver = resolver.Resolver("name")
        # Extract a tree structure having the chosen HPO term (hpo_id) as ancestor of all the children terms
        term_node = node_resolver.get(root, hpo_id)
        LOG.info(f"Built ontology for HPO term:{hpo_id}:\n{RenderTree(term_node)}")
        exporter = DictExporter()
        # Export this tree structure as dictionary, so that can be saved in database
        tree_dict = exporter.export(term_node)
        return tree_dict
