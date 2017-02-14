import logging

from mongoengine import DoesNotExist

from scout.models import HgncGene

logger = logging.getLogger(__name__)


class GeneHandler(object):

    def load_hgnc_gene(self, gene_obj):
        """Add a gene object with transcripts to the database

        Arguments:
            gene_obj(dict)

        """
        logger.debug("Loading gene %s into database" % gene_obj['hgnc_symbol'])
        obj_id = self.db.hgnc_gene.insert_one(gene_obj)
        logger.debug("Gene saved")

    def hgnc_gene(self, hgnc_id, build='37'):
        """Fetch a hgnc gene

            Args:
                hgnc_id(int)

            Returns:
                gene_obj(HgncGene)
        """
        logger.debug("Fetching gene %s" % hgnc_id)
        gene_obj = self.db.hgnc_gene.find_one({'hgnc_id':hgnc_id, 'build': build})
        
        return gene_obj

    def hgnc_genes(self, hgnc_symbol):
        """Fetch all hgnc genes that match a hgnc symbol

            Check both hgnc_symbol and aliases

            Args:
                hgnc_symbol(str)

            Returns:
                result()
        """
        logger.debug("Fetching genes with symbol %s" % hgnc_symbol)

        return HgncGene.objects(aliases=hgnc_symbol)

    def all_genes(self):
        """Fetch all hgnc genes

            Returns:
                result()
        """
        logger.info("Fetching all genes")
        return HgncGene.objects().order_by('chromosome')

    def drop_genes(self):
        """Delete the genes collection"""
        logger.info("Dropping the HgncGene collection")
        print(HgncGene.drop_collection())

    def hgncid_to_gene(self):
        """Return a dictionary with hgnc_id as key and gene_obj as value"""
        hgnc_dict = {}
        logger.info("Building hgncid_to_gene")
        for gene_obj in self.all_genes():
            hgnc_dict[gene_obj['hgnc_id']] = gene_obj
        logger.info("All genes fetched")
        return hgnc_dict

    def hgncsymbol_to_gene(self):
        """Return a dictionary with hgnc_symbol as key and gene_obj as value"""
        hgnc_dict = {}
        logger.info("Building hgncsymbol_to_gene")
        for gene_obj in self.all_genes():
            hgnc_dict[gene_obj['hgnc_symbol']] = gene_obj
        logger.info("All genes fetched")
        return hgnc_dict
