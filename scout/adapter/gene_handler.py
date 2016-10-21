import logging

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
        