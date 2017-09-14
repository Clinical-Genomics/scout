import datetime as dt
import logging

import pymongo
from bson import ObjectId

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
            raise IntegrityError("Panel {0} with version {1} already"
                                 " exist in database".format(panel_name, panel_version))
        logger.debug("Panel saved")

        self.panel_collection.insert_one(panel_obj)

    def panel(self, panel_id):
        """Fetch a gene panel by '_id'.

        Args:
            panel_id (str, ObjectId): str or ObjectId of document ObjectId

        Returns:
            dict: panel object or `None` if panel not found
        """
        if not isinstance(panel_id, ObjectId):
            panel_id = ObjectId(panel_id)
        panel_obj = self.panel_collection.find_one({'_id': panel_id})
        return panel_obj

    def gene_panel(self, panel_id, version=None):
        """Fetch a gene panel.

        If no panel is sent return all panels

        Args:
            panel_id (str): unique id for the panel
            version (str): version of the panel. If 'None' latest version will be returned

        Returns:
            gene_panel: gene panel object
        """
        query = {'panel_name': panel_id}
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

    def gene_panels(self, panel_id=None, institute_id=None):
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
        if institute_id:
            query['institute'] = institute_id

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

    def update_panel(self, panel_obj):
        """Replace a existing gene panel with a new one

        Keeps the object id

        Args:
            panel_obj(dict)

        Returns:
            updated_panel(dict)
        """
        logger.info("Updating panel %s", panel_obj['panel_name'])
        # update date of panel to "today"
        panel_obj['date'] = dt.datetime.now()
        updated_panel = self.panel_collection.find_one_and_replace(
            {'_id': panel_obj['_id']},
            panel_obj,
            return_document=pymongo.ReturnDocument.AFTER
        )

        return updated_panel

    def add_pending(self, panel_obj, hgnc_id, action, info=None):
        """Add a pending action to a gene panel

        Store the pending actions in panel.pending

        Args:
            panel_obj(dict): The panel that is about to be updated
            hgnc_id(int):
            action(str): choices=['add','delete','edit']

        Returns:
            updated_panel(dict):

        """
        valid_actions = ['add', 'delete', 'edit']
        if action not in valid_actions:
            raise ValueError("Invalid action {0}".format(action))

        hgnc_gene = self.hgnc_gene(hgnc_id)
        info = info or {}
        pending_action = {
            'hgnc_id': hgnc_id,
            'action': action,
            'info': info,
            'symbol': hgnc_gene['hgnc_symbol'],
        }

        updated_panel = self.panel_collection.find_one_and_update(
            {'_id': panel_obj['_id']},
            {
                '$push': {
                    'pending': pending_action
                }
            },
            return_document=pymongo.ReturnDocument.AFTER
        )

        return updated_panel

    def apply_pending(self, panel_obj):
        """Apply the pending changes to an existing gene panel

        Args:
            panel_obj(dict)

        Returns:
            new_panel(dict): Panel with changes
        """
        updates = {}
        new_panel = dict(panel_obj)
        new_panel.pop('_id')
        new_panel['pending'] = []

        new_genes = []

        for update in panel_obj.get('pending', []):
            hgnc_id = update['hgnc_id']

            # If action is add we create a new gene object
            if update['action'] == 'add':
                info = update.get('info', {})
                gene_obj = {
                    'hgnc_id': hgnc_id,
                    'symbol': update['symbol']
                }
                if info.get('disease_associated_transcripts'):
                    gene_obj['disease_associated_transcripts'] = info['disease_associated_transcripts']
                if info.get('inheritance_models'):
                    gene_obj['inheritance_models'] = info['inheritance_models']
                if info.get('reduced_penetrance'):
                    gene_obj['reduced_penetrance'] = info['reduced_penetrance']
                if info.get('mosaicism'):
                    gene_obj['mosaicism'] = info['mosaicism']
                if info.get('database_entry_version'):
                    gene_obj['database_entry_version'] = info['database_entry_version']
                new_genes.append(gene_obj)

            else:
                updates[hgnc_id] = update

        for gene in panel_obj['genes']:
            hgnc_id = gene['hgnc_id']

            if hgnc_id in updates:
                current_update = updates[hgnc_id]
                action = current_update['action']
                info = current_update['info']

                # If action is delete we do not add the gene to new genes
                if action == 'delete':
                    pass
                elif action == 'edit':
                    if info.get('disease_associated_transcripts'):
                        gene['disease_associated_transcripts'] = info['disease_associated_transcripts']
                    if info.get('inheritance_models'):
                        gene['inheritance_models'] = info['inheritance_models']
                    if info.get('reduced_penetrance'):
                        gene['reduced_penetrance'] = info['reduced_penetrance']
                    if info.get('mosaicism'):
                        gene['mosaicism'] = info['mosaicism']
                    if info.get('database_entry_version'):
                        gene['database_entry_version'] = info['database_entry_version']
                    new_genes.append(gene)
            else:
                new_genes.append(gene)

        new_panel['genes'] = new_genes
        new_panel['version'] = panel_obj['version'] + 1

        self.panel_collection.insert_one(new_panel)

        # archive the old panel
        panel_obj['is_archived'] = True
        self.update_panel(panel_obj)
        return new_panel

    def latest_panels(self, institute_id):
        """Return the latest version of each panel."""
        panel_names = self.gene_panels(institute_id=institute_id).distinct('panel_name')
        for panel_name in panel_names:
            panel_obj = self.gene_panel(panel_name)
            yield panel_obj
