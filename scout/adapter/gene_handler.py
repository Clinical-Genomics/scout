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
        """Fetch a hgnc gene"""
        logger.debug("Fetching gene %s" % hgnc_id)
        try:
            gene_obj = HgncGene.objects.get(hgnc_id=hgnc_id)
        except DoesNotExist:
            gene_obj = None
        
        return gene_obj