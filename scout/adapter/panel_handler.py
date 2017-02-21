import logging
import math

from datetime import datetime

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

    def gene_panels(self, institute_id=None):
        """Fetch gene panels."""
        if institute_id:
            return GenePanel.objects(institute=institute_id)
        else:
            return GenePanel.objects

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
            result = GenePanel.objects(panel_name=panel_id).order_by('-version').first()
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

    def update_panel(self, panel_obj, version=None):
        """Update a gene panel

        Updates a gene panel and its version.
        Add, remove or edit genes.

        Args:
            panel_obj(dict): The gene panel that should be updated
        """
        version = version or panel_obj['version']

        # If the user choosed a lower version set it to old version
        if version < panel_obj['version']:
            version = panel_obj['version']
        logger.info("Updating gene panel %s", panel_obj['panel_name'])

        if version == panel_obj['version']:
            if version.is_integer:
                new_version = version + 1
            else:
                new_version = version or float(math.ceil(version))
        else:
            new_version = version
        logger.info("Updating version to %s", new_version)

        existing_genes = panel_obj['genes']
        genes_to_add = [] # List of gene objs
        genes_to_remove = [] # List of gene objs
        ids_to_remove = [] # List of hgnc ids

        for gene_obj in panel_obj['pending_genes']:
            gene_obj['database_entry_version'] = str(new_version)
            if gene_obj['action'] == 'add':
                existing_genes.append(gene_obj)
                genes_to_add.append(gene_obj)
            elif gene_obj['action'] == 'delete':
                ids_to_remove.append(gene_obj['hgnc_id'])
                genes_to_remove.append(gene_obj)

        new_panel_genes = [gene_obj for gene_obj in existing_genes if
                           gene_obj['hgnc_id'] not in ids_to_remove]

        new_panel = GenePanel(
            panel_name = panel_obj['panel_name'],
            institute = panel_obj['institute'],
            version = new_version,
            date = datetime.now(),
            display_name = panel_obj['display_name'],
            genes = new_panel_genes,
            pending_genes = panel_obj['pending_genes'],
        )

        self.add_gene_panel(new_panel)
