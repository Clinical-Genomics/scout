import logging

from mongoengine import DoesNotExist

from scout.models.hgnc_map import (HgncGene, HgncGene38)

logger = logging.getLogger(__name__)


class GeneHandler(object):

    def load_hgnc_gene(self, gene_obj):
        """Add a gene object with transcripts to the database

        Arguments:
            gene_obj(HgncGene)

        """
        logger.debug("Loading gene {0} into database".format(gene_obj['hgnc_symbol']))
        gene_obj.save()
        logger.debug("Gene saved")

    def hgnc_gene(self, hgnc_id=None, build='37'):
        """Fetch a hgnc gene
        
            If no hgnc_id return all genes.
        
            Args:
                hgnc_id(int)

            Returns:
                gene_obj(HgncGene)
        """
        if hgnc_id:
            logger.debug("Fetching gene %s from build %s" % (hgnc_id, build))
            try:
                if build == '37':
                    gene_obj = HgncGene.objects.get(hgnc_id=hgnc_id)
                else:
                    gene_obj = HgncGene38.objects.get(hgnc_id=hgnc_id)
            except DoesNotExist:
                gene_obj = None
        else:
            logger.info("Fetching all genes from build %s" % build)
            if build == '37':
                gene_obj = HgncGene.objects()
            else:
                gene_obj = HgncGene38.objects()

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

    def all_genes(self, build='37'):
        """Fetch all hgnc genes

            Returns:
                result()
        """
        logger.info("Fetching all genes from build %s" % build)
        if build == '37':
            return HgncGene.objects().order_by('chromosome')
        else:
            return HgncGene38.objects().order_by('chromosome')

    def drop_genes(self, build='37'):
        """Delete the genes collection"""
        logger.info("Dropping the HgncGene collection build %s" % build)
        if build == '37':
            print(HgncGene.drop_collection())
        else:
            print(HgncGene38.drop_collection())

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
