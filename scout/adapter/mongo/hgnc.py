import logging

logger = logging.getLogger(__name__)


class GeneHandler(object):

    def load_hgnc_gene(self, gene_obj):
        """Add a gene object with transcripts to the database

        Arguments:
            gene_obj(dict)

        """
        logger.debug("Loading gene %s, build %s into database" %
                     (gene_obj['hgnc_symbol'], gene_obj['build']))
        res = self.hgnc_collection.insert_one(gene_obj)
        logger.debug("Gene saved")
        return res

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
        logger.debug("Fetching gene %s" % hgnc_identifyer)
        gene_obj = self.hgnc_collection.find_one(query)
        return gene_obj

    def hgnc_id(self, hgnc_symbol, build='37'):
        """Query the genes with a hgnc symbol and return the hgnc id

        Args:
            hgnc_symbol(str)
            build(str)

        Returns:
            hgnc_id(int)
        """
        logger.debug("Fetching gene %s", hgnc_symbol)
        query = {'hgnc_symbol':hgnc_symbol, 'build':build}
        projection = {'hgnc_id':1, '_id':0}
        res = self.hgnc_collection.find(query, projection)

        if res.count() > 0:
            return res[0]['hgnc_id']
        else:
            return None

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
        logger.debug("Fetching genes with symbol %s" % hgnc_symbol)
        if search:
            return self.hgnc_collection.find(
                        {
                            'aliases': {'$regex': hgnc_symbol, '$options':'i'},
                            'build': build
                        }
                    )

        return self.hgnc_collection.find({'aliases': hgnc_symbol, 'build': build})

    def all_genes(self, build='37'):
        """Fetch all hgnc genes

            Returns:
                result()
        """
        logger.info("Fetching all genes")
        return self.hgnc_collection.find({'build': build}).sort('chromosome', 1)

    def nr_genes(self, build=None):
        """Return the number of hgnc genes in collection

        If build is used, return the number of genes of a certain build

            Returns:
                result()
        """
        if build:
            logger.info("Fetching all genes from build %s",  build)
        else:
            logger.info("Fetching all genes")

        return self.hgnc_collection.find({'build':build}).count()

    def drop_genes(self, build=None):
        """Delete the genes collection"""
        if build:
            logger.info("Dropping the hgnc_gene collection, build %s", build)
            self.hgnc_collection.delete_many({'build': build})
        else:
            logger.info("Dropping the hgnc_gene collection")
            self.hgnc_collection.drop()

    def hgncid_to_gene(self, build='37'):
        """Return a dictionary with hgnc_id as key and gene_obj as value
            
        The result will have ONE entry for each gene in the database.
        (For a specific build)

        Args:
            build(str):
        
        Returns:
            hgnc_dict(dict): {<hgnc_id(int)>: <gene(dict)>}

        """
        hgnc_dict = {}
        logger.info("Building hgncid_to_gene")
        for gene_obj in self.hgnc_collection.find({'build':build}):
            hgnc_dict[gene_obj['hgnc_id']] = gene_obj
        logger.info("All genes fetched")
        return hgnc_dict

    def hgncsymbol_to_gene(self):
        """Return a dictionary with hgnc_symbol as key and gene_obj as value
        
        The result will have ONE entry for each gene in the database.
        (For a specific build)

        Args:
            build(str)
        
        Returns:
            hgnc_dict(dict): {<hgnc_symbol(str)>: <gene(dict)>}
        
        """
        hgnc_dict = {}
        logger.info("Building hgncsymbol_to_gene")
        for gene_obj in self.hgnc_collection.find():
            hgnc_dict[gene_obj['hgnc_symbol']] = gene_obj
        logger.info("All genes fetched")
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
        res = self.hgnc_collection.find({'hgnc_symbol': symbol, 'build':build})
        if res.count() == 0:
            res = self.hgnc_collection.find({'aliases': symbol, 'build':build})
        
        return res

    def genes_by_alias(self, build='37'):
        """Return a dictionary with hgnc symbols as keys and a list of hgnc ids
             as value.

        If a gene symbol is listed as primary the list of ids will only consist
        of that entry if not the gene can not be determined so the result is a list
        of hgnc_ids
        
        Args:
            build(str)
        
        Returns:
            alias_genes(dict): {<hgnc_alias>: [<hgnc_id_1>, <hgnc_id_2>, ...]}
        """
        alias_genes = {}
        for gene in self.hgnc_collection.find({'build':build}):
            hgnc_id = gene['hgnc_id']
            hgnc_symbol = gene['hgnc_symbol']
            for alias in gene['aliases']:
                true_id = None
                if alias == hgnc_symbol:
                    true_id = hgnc_id
                if alias in alias_genes:
                    alias_genes[alias]['ids'].add(hgnc_id)
                    if true_id:
                        alias_genes[alias]['true'] = hgnc_id
                else:
                    alias_genes[alias] = {
                        'true': true_id,
                        'ids': set([hgnc_id])
                    }

        return alias_genes

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

