import logging

from mongoengine import DoesNotExist

from scout.models import HgncGene

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

    def hgnc_gene(self, hgnc_id):
        """Fetch a hgnc gene

            Args:
                hgnc_id(int)

            Returns:
                gene_obj(HgncGene)
        """
        logger.debug("Fetching gene %s" % hgnc_id)
        try:
            gene_obj = HgncGene.objects.get(hgnc_id=hgnc_id)
        except DoesNotExist:
            gene_obj = None
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
