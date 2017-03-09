import logging

from scout.exceptions import IntegrityError

logger = logging.getLogger(__name__)

class PanelHandler(object):

    def add_gene_panel(self, panel_obj):
        """Add a gene panel to the database

            Args:
                panel_obj(dict)
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
        logger.debug("Panel saved")
        
        self.panel_collection.insert_one(panel_obj)

    def gene_panel(self, panel_id, version=None):
        """Fetch a gene panel.
        
        If no panel is sent return all panels

        Args:
            panel_id (str): unique id for the panel
            version (str): version of the panel. If 'None' latest version will be returned

        Returns:
            gene_panel: gene panel object
        """
        query = {'panel_name':panel_id}
        if version:
            logger.debug("Fetch gene panel {0}, version {1} from database".format(
                panel_id, version
            ))
            query['version'] = version
            return self.panel_collection.find_one(query)
        else:
            logger.info("Fething gene panels %s from database" % panel_id)
            res = self.panel_collection.find(query).sort('version', -1)
            if res.count() > 0:
                return res[0]
            else:
                logger.info("No gene panel found")
                return None

    def gene_panels(self, panel_id=None):
        """Return all gene panels
        
        If panel_id return all versions of that panel
        
        Args:
            panel_id(str)
        
        Returns:
            cursor(pymongo.cursor)
        """
        query = {}
        if panel_id:
            query['panel_name'] = panel_id
        
        return self.panel_collection.find(query)
        

    def gene_to_panels(self):
        """Fetch all gene panels and group them by gene
    
            Args:
                adapter(MongoAdapter)
            Returns:
                gene_dict(dict): A dictionary with gene as keys and a set of
                                 panel names as value
        """
        logger.info("Building gene to panels")
        gene_dict = {}
        for panel in self.gene_panels():
            for gene in panel['genes']:
                hgnc_id = gene['hgnc_id']
                if hgnc_id in gene_dict:
                    gene_dict[hgnc_id].add(panel['panel_name'])
                else:
                    gene_dict[hgnc_id] = set([panel['panel_name']])
        logger.info("Gene to panels done")

        return gene_dict
        
