import logging

logger = logging.getLogger(__name__)


class PanelHandler(object):

    def add_gene_panel(self, panel_obj):
        """Add a gene panel to the database

            Args:
                panel_obj(GenePanel)
        """
        self.mongoengine_adapter.add_gene_panel(
            panel_obj = panel_obj
        )

    def gene_panel(self, panel_id=None, version=None):
        """Fetch a gene panel.
        
        If no panel is sent return all panels

        Args:
            panel_id (str): unique id for the panel
            version (str): version of the panel. If 'None' latest version will be returned

        Returns:
            GenePanel: gene panel object
        """
        return self.mongoengine_adapter.gene_panel(
            panel_id = panel_id,
            version = version
        )

    def gene_to_panels(self):
        """Fetch all gene panels and group them by gene
    
            Args:
                adapter(MongoAdapter)
            Returns:
                gene_dict(dict): A dictionary with gene as keys and a list of
                                 panel names as value
        """
        return self.mongoengine_adapter.gene_to_panels()
