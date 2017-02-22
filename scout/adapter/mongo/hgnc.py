import logging
import re

logger = logging.getLogger(__name__)


class GeneHandler(object):

    def load_hgnc_gene(self, gene_obj):
        """Add a gene object with transcripts to the database

        Arguments:
            gene_obj(dict)

        """
        logger.debug("Loading gene %s into database" % gene_obj['hgnc_symbol'])
        res = self.hgnc_collection.insert_one(gene_obj)
        logger.debug("Gene saved")
        return res

    def hgnc_gene(self, hgnc_id, build='37'):
        """Fetch a hgnc gene

            Args:
                hgnc_id(int)

            Returns:
                gene_obj(HgncGene)
        """
        logger.debug("Fetching gene %s" % hgnc_id)
        gene_obj = self.hgnc_collection.find_one({'hgnc_id':hgnc_id, 'build': build})

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
        logger.debug("Fetching genes with symbol %s" % hgnc_symbol)
        if search:
            regx = re.compile(hgnc_symbol, re.IGNORECASE)
            return self.hgnc_collection.find({'aliases': {'$in': [regx]}, 'build': build})
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

    def drop_genes(self):
        """Delete the genes collection"""
        logger.info("Dropping the hgnc_gene collection")
        self.hgnc_collection.drop()

    def hgncid_to_gene(self):
        """Return a dictionary with hgnc_id as key and gene_obj as value"""
        hgnc_dict = {}
        logger.info("Building hgncid_to_gene")
        for gene_obj in self.hgnc_collection.find():
            hgnc_dict[gene_obj['hgnc_id']] = gene_obj
        logger.info("All genes fetched")
        return hgnc_dict

    def hgncsymbol_to_gene(self):
        """Return a dictionary with hgnc_symbol as key and gene_obj as value"""
        hgnc_dict = {}
        logger.info("Building hgncsymbol_to_gene")
        for gene_obj in self.hgnc_collection.find():
            hgnc_dict[gene_obj['hgnc_symbol']] = gene_obj
        logger.info("All genes fetched")
        return hgnc_dict

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

