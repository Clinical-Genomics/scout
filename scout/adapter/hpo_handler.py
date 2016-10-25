import logging

from mongoengine import DoesNotExist

from scout.models import (HpoTerm, DiseaseTerm)

logger = logging.getLogger(__name__)

class HpoHandler(object):
    
    def load_hpo_term(self, hpo_obj):
        """Add a hpo object

        Arguments:
            hpo_obj(HgncGene)

        """
        logger.debug("Loading gene {0} into database".format(gene_obj['hgnc_symbol']))
        hpo_obj.save()
        logger.debug("Gene saved")
    
    def hpo_term(self, hpo_id):
        """Fetch a hgnc gene"""
        logger.debug("Fetching hpo term %s" % hpo_id)
        try:
            hpo_obj = HpoTerm.objects.get(hpo_id=hpo_id)
        except DoesNotExist:
            hpo_obj = None
        
        return hpo_obj