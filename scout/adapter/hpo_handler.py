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
        logger.debug("Loading hpo term %s into database", hpo_obj['hpo_id'])
        hpo_obj.save()
        logger.debug("Hpo term saved")

    def hpo_term(self, hpo_id):
        """Fetch a hgnc gene"""
        logger.debug("Fetching hpo term %s" % hpo_id)
        try:
            hpo_obj = HpoTerm.objects.get(hpo_id=hpo_id)
        except DoesNotExist:
            hpo_obj = None

        return hpo_obj

    def hpo_terms(self, query=None):
        """Return all HPO terms"""
        logger.info("Fetching all hpo terms from database")
        if query:
            return HpoTerm.objects(description__icontains=query)
        return HpoTerm.objects()

    def disease_terms(self, hgnc_id=None):
        """Return all disease terms that overlaps a gene

            If no gene, return all disease terms
        """
        if hgnc_id:
            return DiseaseTerm.objects(genes=hgnc_id)
        else:
            return DiseaseTerm.objects()

    def load_disease_term(self, disease_obj):
        """Load a disease term into the database"""
        logger.debug("Loading disease %s into database", disease_obj.disease_id)
        disease_obj.save()
        logger.debug("Disease term saved")
