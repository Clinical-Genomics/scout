import logging
from pprint import pprint as pp
import intervaltree

from .transcript import TranscriptHandler
from scout.build.genes.exon import build_exon
from pymongo.errors import (DuplicateKeyError, BulkWriteError)

from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)

class GeneHandler(TranscriptHandler):

    def load_hgnc_gene(self, gene_obj):
        """Add a gene object with transcripts to the database

        Arguments:
            gene_obj(dict)
        
        Returns:
            res(pymongo.results.insertOneResult)

        """
        res = self.hgnc_collection.insert_one(gene_obj)
        return res

    def load_hgnc_bulk(self, gene_objs):
        """Load a bulk of hgnc gene objects
        
        Raises IntegrityError if there are any write concerns

        Args:
            gene_objs(iterable(scout.models.hgnc_gene))

        Returns:
            result (pymongo.results.InsertManyResult)
        """

        LOG.info("Loading gene bulk with length %s", len(gene_objs))
        try:
            result = self.hgnc_collection.insert_many(gene_objs)
        except (DuplicateKeyError, BulkWriteError) as err:
            raise IntegrityError(err)

        return result

    def hgnc_gene(self, hgnc_identifyer, build='37'):
        """Fetch a hgnc gene

            Args:
                hgnc_id(int)

            Returns:
                gene_obj(HgncGene)
        """
        query = {}
        try:
            # If the identifier is a integer we search for hgnc_id
            hgnc_identifyer = int(hgnc_identifyer)
            query['hgnc_id'] = hgnc_identifyer
        except ValueError:
            # Else we seach for a hgnc_symbol
            query['hgnc_symbol'] = hgnc_identifyer

        query['build'] = build
        #LOG.debug("Fetching gene %s" % hgnc_identifyer)
        gene_obj = self.hgnc_collection.find_one(query)
        if not gene_obj:
            return None
        
        # Add the transcripts:
        transcripts = []
        tx_objs = self.transcripts(build='37', hgnc_id=gene_obj['hgnc_id'])
        for tx in tx_objs:
            transcripts.append(tx)
        gene_obj['transcripts'] = transcripts
        
        return gene_obj

    def hgnc_genes(self, hgnc_symbol, build='37', search=False):
        """Fetch all hgnc genes that match a hgnc symbol

            Check both hgnc_symbol and aliases

            Args:
                hgnc_symbol(str)
                build(str): The build in which to search
                search(bool): if partial searching should be used

            Returns:
                result()
        """
        LOG.debug("Fetching genes with symbol %s" % hgnc_symbol)
        query = self._hgnc_query(build=build, hgnc_symbol=hgnc_symbol, search=search)
        
        return self.hgnc_collection.find(query)

    def all_genes(self, build='37'):
        """Fetch all hgnc genes

            Returns:
                result()
        """
        LOG.info("Fetching all genes")
        query = self._hgnc_query(build=build)

        return self.hgnc_collection.find(query).sort('chromosome', 1)

    def _hgnc_query(self, build=None, hgnc_symbol=None, search=False):
        """Create a query for hgnc genes
        
        Args:
            build(str)
            hgnc_symbol(str): Could be symbol or id
            search(bool): If partial search should be used
        
        Returns:
            mongo_query(dict)
        """
        mongo_query = {}
        if hgnc_symbol:
            mongo_query['aliases'] = hgnc_symbol

        if search:
            mongo_query = {
                '$or': [
                    {'aliases': hgnc_symbol},
                    {'hgnc_id': int(hgnc_symbol) if hgnc_symbol.isdigit() else None},
                ],
            }
            # If no documents where found we search with regex
            if self.hgnc_collection.count_documents(mongo_query) == 0:
                mongo_query = {
                    'aliases': {'$regex': hgnc_symbol, '$options': 'i'},
                }

        if build:
            LOG.info("Fetching all genes from build %s",  build)
            mongo_query['build'] = build
        
        return mongo_query

    def nr_genes(self, build=None, hgnc_symbol=None, search=False):
        """Return the number of hgnc genes in collection

        If build is used, return the number of genes of a certain build

            Returns:
                result()
        """
        query = self._hgnc_query(build=build, hgnc_symbol=hgnc_symbol, search=search)

        return self.hgnc_collection.count_documents(query)

    def drop_genes(self, build=None):
        """Delete the genes collection"""
        if build:
            LOG.info("Dropping the hgnc_gene collection, build %s", build)
            self.hgnc_collection.delete_many({'build': build})
        else:
            LOG.info("Dropping the hgnc_gene collection")
            self.hgnc_collection.drop()

    def hgncid_to_gene(self, build='37', genes=None):
        """Return a dictionary with hgnc_id as key and gene_obj as value

        The result will have ONE entry for each gene in the database.
        (For a specific build)

        Args:
            build(str):
            genes(iterable(scout.models.HgncGene)):

        Returns:
            hgnc_dict(dict): {<hgnc_id(int)>: <gene(dict)>}

        """
        hgnc_dict = {}
        query = self._hgnc_query(build=build)
        LOG.info("Building hgncid_to_gene")
        if not genes:
            genes = self.hgnc_collection.find(query)

        for gene_obj in genes:
            hgnc_dict[gene_obj['hgnc_id']] = gene_obj

        return hgnc_dict

    def hgncsymbol_to_gene(self, build='37', genes=None):
        """Return a dictionary with hgnc_symbol as key and gene_obj as value

        The result will have ONE entry for each gene in the database.
        (For a specific build)

        Args:
            build(str)
            genes(iterable(scout.models.HgncGene)):

        Returns:
            hgnc_dict(dict): {<hgnc_symbol(str)>: <gene(dict)>}

        """
        hgnc_dict = {}
        LOG.info("Building hgncsymbol_to_gene")
        query = self._hgnc_query(build=build)
        if not genes:
            genes = self.hgnc_collection.find(query)

        for gene_obj in genes:
            hgnc_dict[gene_obj['hgnc_symbol']] = gene_obj
        LOG.info("All genes fetched")
        return hgnc_dict

    def gene_by_alias(self, symbol, build='37'):
        """Return a iterable with hgnc_genes.

        If the gene symbol is listed as primary the iterable will only have
        one result. If not the iterable will include all hgnc genes that have
        the symbol as an alias.

        Args:
            symbol(str)
            build(str)

        Returns:
            res(pymongo.Cursor(dict))
        """
        query = {'hgnc_symbol': symbol, 'build':build}
        if self.hgnc_collection.count_documents(query) == 0:
            query = {'aliases': symbol, 'build':build}

        res = self.hgnc_collection.find(query)

        return res

    def genes_by_alias(self, build='37', genes=None):
        """Return a dictionary with hgnc symbols as keys and a list of hgnc ids
             as value.

        If a gene symbol is listed as primary the list of ids will only consist
        of that entry if not the gene can not be determined so the result is a list
        of hgnc_ids

        Args:
            build(str)
            genes(iterable(scout.models.HgncGene)):

        Returns:
            alias_genes(dict): {<hgnc_alias>: {'true': <hgnc_id>, 'ids': {<hgnc_id_1>, <hgnc_id_2>, ...}}}
        """
        LOG.info("Fetching all genes by alias")
        # Collect one entry for each alias symbol that exists
        alias_genes = {}
        query = self._hgnc_query(build=build)
        # Loop over all genes
        if not genes:
            genes = self.hgnc_collection.find(query)

        for gene in genes:
            # Collect the hgnc_id
            hgnc_id = gene['hgnc_id']
            # Collect the true symbol given by hgnc
            hgnc_symbol = gene['hgnc_symbol']
            # Loop aver all aliases
            for alias in gene['aliases']:
                true_id = None
                # If the alias is the same as hgnc symbol we know the true id
                if alias == hgnc_symbol:
                    true_id = hgnc_id
                # If the alias is already in the list we add the id
                if alias in alias_genes:
                    alias_genes[alias]['ids'].add(hgnc_id)
                    if true_id:
                        alias_genes[alias]['true'] = hgnc_id
                else:
                    alias_genes[alias] = {
                        'true': hgnc_id,
                        'ids': set([hgnc_id])
                    }

        return alias_genes

    def ensembl_genes(self, build='37'):
        """Return a dictionary with ensembl ids as keys and gene objects as value.

        Args:
            build(str)
        
        Returns:
            genes(dict): {<ensg_id>: gene_obj, ...}
        """
        genes = {}
        query = self._hgnc_query(build=build)
        LOG.info("Fetching all genes")
        for gene_obj in self.hgnc_collection.find(query):
            ensg_id = gene_obj['ensembl_id']
            hgnc_id = gene_obj['hgnc_id']
            
            genes[ensg_id] = gene_obj
        
        LOG.info("Ensembl genes fetched")

        return genes

    def to_hgnc(self, hgnc_alias, build='37'):
        """Check if a hgnc symbol is an alias

            Return the correct hgnc symbol, if not existing return None

            Args:
                hgnc_alias(str)

            Returns:
                hgnc_symbol(str)
        """
        result = self.hgnc_genes(hgnc_symbol=hgnc_alias, build=build)
        if result:
            for gene in result:
                return gene['hgnc_symbol']
        else:
            return None

    def add_hgnc_id(self, genes):
        """Add the correct hgnc id to a set of genes with hgnc symbols

        Args:
            genes(list(dict)): A set of genes with hgnc symbols only

        """
        genes_by_alias = self.genes_by_alias()

        for gene in genes:
            id_info = genes_by_alias.get(gene['hgnc_symbol'])
            if not id_info:
                LOG.warning("Gene %s does not exist in scout", gene['hgnc_symbol'])
                continue
            gene['hgnc_id'] = id_info['true']
            if not id_info['true']:
                if len(id_info['ids']) > 1:
                    LOG.warning("Gene %s has ambiguous value, please choose one hgnc id in result", gene['hgnc_symbol'])
                gene['hgnc_id'] = ','.join([str(hgnc_id) for hgnc_id in id_info['ids']])

    def get_coding_intervals(self, build='37', genes=None):
        """Return a dictionary with chromosomes as keys and interval trees as values

        Each interval represents a coding region of overlapping genes.

        Args:
            build(str): The genome build
            genes(iterable(scout.models.HgncGene)):

        Returns:
            intervals(dict): A dictionary with chromosomes as keys and overlapping genomic intervals as values
        """
        intervals = {}
        if not genes:
            genes = self.all_genes(build=build)
        LOG.info("Building interval trees...")
        for i,hgnc_obj in enumerate(genes):
            chrom = hgnc_obj['chromosome']
            start = max((hgnc_obj['start'] - 5000), 1)
            end = hgnc_obj['end'] + 5000

            # If this is the first time a chromosome is seen we create a new
            # interval tree with current interval
            if chrom not in intervals:
                intervals[chrom] = intervaltree.IntervalTree()
                intervals[chrom].addi(start, end, i)
                continue

            res = intervals[chrom].search(start, end)

            # If the interval did not overlap any other intervals we insert it and continue
            if not res:
                intervals[chrom].addi(start, end, i)
                continue

            # Loop over the overlapping intervals
            for interval in res:
                # Update the positions to new max and mins
                if interval.begin < start:
                    start = interval.begin

                if interval.end > end:
                    end = interval.end

                # Delete the old interval
                intervals[chrom].remove(interval)

            # Add the new interval consisting och the overlapping ones
            intervals[chrom].addi(start, end, i)

        return intervals
