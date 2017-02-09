import logging

from scout.exceptions import IntegrityError
from mongoengine import DoesNotExist
from scout.models.panel import GenePanel

logger = logging.getLogger(__name__)


class PanelHandler(object):

    def add_gene_panel(self, panel_obj):
        """Add a gene panel to the database

            Args:
                panel_obj(GenePanel)
        """
        panel_name = panel_obj['panel_name']
        panel_version = panel_obj['version']

        logger.info("loading panel {0}, version {1} to database".format(
            panel_name, panel_version
        ))
        if self.gene_panel(panel_name, panel_version):
            raise IntegrityError("Panel {0} with version {1} already"\
                                 " exist in database".format(
                                 panel_name, panel_version))
        panel_obj.save()
        logger.debug("Panel saved")
    
    def gene_panel(self, panel_id=None, version=None):
        """Fetch a gene panel.
        
        If no panel is sent return all panels

        Args:
            panel_id (str): unique id for the panel
            version (str): version of the panel. If 'None' latest version will be returned

        Returns:
            GenePanel: gene panel object
        """
        if version:
            if not panel_id:
                raise SyntaxError("Please provide a panel id")
            try:
                logger.debug("Fetch gene panel {0}, version {1} from database".format(
                    panel_id, version
                ))
                result = GenePanel.objects.get(panel_name=panel_id, version=version)
            except DoesNotExist:
                result = None
        elif panel_id:
            logger.info("Fething gene panels %s from database" % panel_id)
            result = GenePanel.objects(panel_name=panel_id).order_by('-version')
        else:
            logger.info("Fething all gene panels from database")
            result = GenePanel.objects()

        return result

    def gene_to_panels(self):
        """Fetch all gene panels and group them by gene
    
            Args:
                adapter(MongoAdapter)
            Returns:
                gene_dict(dict): A dictionary with gene as keys and a list of
                                 panel names as value
        """
        logger.info("Building gene to panels")
        gene_dict = {}
        for panel in self.gene_panel():
            for gene in panel.genes:
                hgnc_id = gene['hgnc_id']
                if hgnc_id in gene_dict:
                    gene_dict[hgnc_id].add(panel.panel_name)
                else:
                    gene_dict[hgnc_id] = set([panel.panel_name])
        logger.info("Gene to panels")
    
        return gene_dict
    