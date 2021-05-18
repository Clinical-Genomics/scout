"""Code to handle panels in the mongo database"""
import datetime as dt
import logging
import math
from copy import deepcopy

import pymongo
from bson import ObjectId

from scout.build import build_panel
from scout.exceptions import IntegrityError
from scout.parse.panel import get_omim_panel_genes
from scout.utils.date import get_date

LOG = logging.getLogger(__name__)


class PanelHandler:
    """Code to handle interactions with the mongo database for panels"""

    def load_panel(self, parsed_panel):
        """Load a gene panel based on the info sent
        A panel object is built and integrity checks are made.
        The panel object is then loaded into the database.

        Args:
            path(str): Path to panel file
            institute(str): Name of institute that owns the panel
            panel_id(str): Panel id
            date(datetime.datetime): Date of creation
            version(float)
            full_name(str): Option to have a long name

            panel_info(dict): {
                'file': <path to panel file>(str),
                'institute': <institute>(str),
                'type': <panel type>(str),
                'date': date,
                'version': version,
                'panel_name': panel_id,
                'full_name': name,
            }
        """
        panel_obj = build_panel(parsed_panel, self)

        self.add_gene_panel(panel_obj)

    def load_omim_panel(self, genemap2_lines, mim2gene_lines, institute=None):
        """Create and load the OMIM-AUTO panel

        If the panel already exists, update with new information and increase version

        Args:
            genemap_lines(iterable(str)): The genemap2 file information
            mim2gene_lines(iterable(str)): The mim2genes file information
            institute(str): What institute that is responsible. Default: 'cust002'

        """
        institute = institute or "cust002"
        existing_panel = self.gene_panel(panel_id="OMIM-AUTO")
        if not existing_panel:
            LOG.warning("OMIM-AUTO does not exists in database")
            LOG.info("Creating a first version")

        version = 1.0
        if existing_panel:
            version = float(math.floor(existing_panel["version"]) + 1)

        LOG.info("Setting version to %s", version)

        date_string = None
        # Get the correct date when omim files where released
        for line in genemap2_lines:
            if "Generated" in line:
                date_string = line.split(":")[-1].strip()
                break

        date_obj = get_date(date_string)

        if existing_panel:
            if existing_panel["date"] == date_obj:
                LOG.warning("There is no new version of OMIM")
                return

        panel_data = {
            "path": None,
            "type": "clinical",
            "date": date_obj,
            "panel_id": "OMIM-AUTO",
            "institute": institute,
            "version": version,
            "display_name": "OMIM-AUTO",
            "genes": [],
        }

        alias_genes = self.genes_by_alias()

        genes = get_omim_panel_genes(
            genemap2_lines=genemap2_lines,
            mim2gene_lines=mim2gene_lines,
            alias_genes=alias_genes,
        )

        for gene in genes:
            panel_data["genes"].append(gene)

        panel_obj = build_panel(panel_data, self)

        if existing_panel:
            new_genes = self.compare_mim_panels(existing_panel, panel_obj)
            if not new_genes:
                LOG.info("The new version of omim does not differ from the old one")
                LOG.info("No update is added")
                return
            self.update_mim_version(new_genes, panel_obj, old_version=existing_panel["version"])

        self.add_gene_panel(panel_obj)

    @staticmethod
    def compare_mim_panels(existing_panel, new_panel):
        """Check if the latest version of OMIM differs from the most recent in database
           Return all genes that where not in the previous version.

        Args:
            existing_panel(dict)
            new_panel(dict)

        Returns:
            new_genes(set(str))
        """
        existing_genes = {gene["hgnc_id"] for gene in existing_panel["genes"]}
        new_genes = {gene["hgnc_id"] for gene in new_panel["genes"]}

        return new_genes.difference(existing_genes)

    @staticmethod
    def update_mim_version(new_genes, new_panel, old_version):
        """Set the correct version for each gene
        Loop over the genes in the new panel

        Args:
            new_genes(set(str)): Set with the new gene symbols
            new_panel(dict)

        """
        LOG.info("Updating versions for new genes")
        version = new_panel["version"]
        nr_genes = 0
        for nr_genes, gene in enumerate(new_panel["genes"]):
            gene_symbol = gene["hgnc_id"]
            # If the gene is new we add the version
            if gene_symbol in new_genes:
                gene["database_entry_version"] = version
                continue
            # If the gene is old it will have the previous version
            gene["database_entry_version"] = old_version

        LOG.info("Updated %s genes", nr_genes)

    def add_gene_panel(self, panel_obj):
        """Add a gene panel to the database

        Args:
            panel_obj(dict)
        """
        panel_name = panel_obj["panel_name"]
        panel_version = panel_obj["version"]
        display_name = panel_obj.get("display_name", panel_name)

        if self.gene_panel(panel_name, panel_version):
            raise IntegrityError(
                "Panel {0} with version {1} already"
                " exist in database".format(panel_name, panel_version)
            )
        LOG.info("loading panel %s, version %s to database", display_name, panel_version)
        LOG.info("Nr genes in panel: %s", len(panel_obj.get("genes", [])))
        result = self.panel_collection.insert_one(panel_obj)
        LOG.debug("Panel saved")
        return result.inserted_id

    def panel(self, panel_id):
        """Fetch a gene panel by '_id'.

        Args:
            panel_id (str, ObjectId): str or ObjectId of document ObjectId

        Returns:
            dict: panel object or `None` if panel not found
        """
        if not isinstance(panel_id, ObjectId):
            panel_id = ObjectId(panel_id)
        panel_obj = self.panel_collection.find_one({"_id": panel_id})
        return panel_obj

    def delete_panel(self, panel_obj):
        """Delete a panel by '_id'.

        Args:
            panel_obj(dict)

        Returns:
            res(pymongo.DeleteResult)
        """
        res = self.panel_collection.delete_one({"_id": panel_obj["_id"]})
        LOG.warning(
            "Deleting panel %s, version %s" % (panel_obj["panel_name"], panel_obj["version"])
        )
        return res

    def gene_panel(self, panel_id, version=None):
        """Fetch a gene panel.

        If no panel is sent return all panels

        Args:
            panel_id (str): unique id for the panel
            version (str): version of the panel. If 'None' latest version will be returned

        Returns:
            gene_panel: gene panel object
        """
        query = {"panel_name": panel_id}
        if version:
            LOG.info("Fetch gene panel {0}, version {1} from database".format(panel_id, version))
            query["version"] = version
            return self.panel_collection.find_one(query)

        LOG.info("Fetching gene panels %s from database", panel_id)
        res = self.panel_collection.find(query).sort("version", -1)

        for panel in res:
            return panel

        LOG.info("No gene panel found")

        return None

    def gene_panels(self, panel_id=None, institute_id=None, version=None):
        """Return all gene panels

        If panel_id return all versions of panels by that panel name

        Args:
            panel_id(str)

        Returns:
            cursor(pymongo.cursor)
        """
        query = {}
        if panel_id:
            query["panel_name"] = panel_id
            if version:
                query["version"] = version
        if institute_id:
            query["institute"] = institute_id

        return self.panel_collection.find(query)

    def hgnc_to_panels(self, hgnc_id):
        """Get a list of gene panel objects for a hgnc_id

        Args:
            hgnc_id(int)

        Returns:
            hgnc_panels(dict): A dictionary with hgnc as keys and lists of
                               gene panel objects as values
        """
        return self.panel_collection.find({"genes.hgnc_id": hgnc_id})

    def gene_to_panels(self, case_obj):
        """Fetch all gene panels and group them by gene

        Args:
            case_obj(scout.models.Case)
        Returns:
            gene_dict(dict): A dictionary with gene as keys and a set of
                             panel names as value
        """
        LOG.info("Building gene to panels")
        gene_dict = {}

        for panel_info in case_obj.get("panels", []):
            panel_name = panel_info["panel_name"]
            panel_version = panel_info["version"]
            panel_obj = self.gene_panel(panel_name, version=panel_version)
            if not panel_obj:
                ## Raise exception here???
                LOG.warning(
                    "Panel: {0}, version {1} does not exist in database".format(
                        panel_name, panel_version
                    )
                )

            for gene in panel_obj["genes"]:
                hgnc_id = gene["hgnc_id"]

                if hgnc_id not in gene_dict:
                    gene_dict[hgnc_id] = set([panel_name])
                    continue

                gene_dict[hgnc_id].add(panel_name)

        LOG.info("Gene to panels done")

        return gene_dict

    def panel_to_genes(self, panel_id=None, panel_name=None, gene_format="symbol"):
        """Return all hgnc_ids for a given gene panel

        Args:
            panel_id(ObjectId): _id of a gene panel (to collect specific version of a panel)
            panel_name(str): Name of a gene panel (to collect latest version of a panel)
            gene_format(str): either "symbol" or "hgnc_id"

        Returns:
            gene_list(list): a list of hgnc terms (either symbols or HGNC ids)

        """
        panel_obj = None
        if panel_id:
            panel_obj = self.panel(panel_id)
        elif panel_name:
            panel_obj = self.gene_panel(panel_name)

        if panel_obj is None:
            return []

        gene_list = [gene_obj.get(gene_format, "") for gene_obj in panel_obj.get("genes", [])]
        return gene_list

    def update_panel(self, panel_obj, version=None, date_obj=None, maintainer=None):
        """Replace a existing gene panel with a new one

        Keeps the object id

        Args:
            panel_obj(dict)
            version(float)
            date_obj(datetime.datetime)
            maintainer(list(user._id))

        Returns:
            updated_panel(dict)
        """
        LOG.info("Updating panel %s", panel_obj["panel_name"])
        # update date of panel to "today"
        date = panel_obj["date"]
        if version:
            LOG.info("Updating version from %s to version %s", panel_obj["version"], version)
            panel_obj["version"] = version
            # Updating version should not update date
            if date_obj:
                date = date_obj
        elif maintainer is not None:
            LOG.info(
                "Updating maintainer from {} to {}".format(panel_obj.get("maintainer"), maintainer)
            )
            panel_obj["maintainer"] = maintainer
        else:
            date = date_obj or dt.datetime.now()
        panel_obj["date"] = date

        updated_panel = self.panel_collection.find_one_and_replace(
            {"_id": panel_obj["_id"]},
            panel_obj,
            return_document=pymongo.ReturnDocument.AFTER,
        )

        return updated_panel

    def add_pending(self, panel_obj, hgnc_gene, action, info=None):
        """Add a pending action to a gene panel

        Store the pending actions in panel.pending

        Args:
            panel_obj(dict): The panel that is about to be updated
            hgnc_gene(dict)
            action(str): choices=['add','delete','edit']
            info(dict): additional gene info (disease_associated_transcripts,
                        reduced_penetrance, mosaicism, database_entry_version,
                        inheritance_models, custom_inheritance_models, comment)

        Returns:
            updated_panel(dict):

        """

        valid_actions = ["add", "delete", "edit"]
        if action not in valid_actions:
            raise ValueError("Invalid action {0}".format(action))

        info = info or {}
        pending_action = {
            "hgnc_id": hgnc_gene["hgnc_id"],
            "action": action,
            "info": info,
            "symbol": hgnc_gene["hgnc_symbol"],
        }

        updated_panel = self.panel_collection.find_one_and_update(
            {"_id": panel_obj["_id"]},
            {"$addToSet": {"pending": pending_action}},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        return updated_panel

    def reset_pending(self, panel_obj):
        """Reset the pending status of a gene panel

        Args:
            panel_obj(dict): panel in database to update

        Returns:
            updated_panel(dict): the updated gene panel
        """

        if "pending" in panel_obj:
            del panel_obj["pending"]

        updated_panel = self.panel_collection.find_one_and_replace(
            {"_id": panel_obj["_id"]},
            panel_obj,
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_panel

    def apply_pending(self, panel_obj, version):
        """Apply the pending changes to an existing gene panel or create a new version of the same panel.

        Args:
            panel_obj(dict): panel in database to update
            version(double): panel version to update

        Returns:
            inserted_id(str): id of updated panel or the new one
        """

        updates = {}
        new_panel = deepcopy(panel_obj)
        new_panel["pending"] = []
        new_panel["date"] = dt.datetime.now()
        info_fields = [
            "disease_associated_transcripts",
            "inheritance_models",
            "custom_inheritance_models",
            "reduced_penetrance",
            "mosaicism",
            "database_entry_version",
            "comment",
        ]
        new_genes = []

        for update in panel_obj.get("pending", []):
            hgnc_id = update["hgnc_id"]

            # If action is add we create a new gene object
            if update["action"] != "add":
                updates[hgnc_id] = update
                continue
            info = update.get("info", {})
            gene_obj = {"hgnc_id": hgnc_id, "symbol": update["symbol"]}

            for field in info_fields:
                if field in info:
                    gene_obj[field] = info[field]
            new_genes.append(gene_obj)

        for gene in panel_obj.get("genes", []):
            hgnc_id = gene["hgnc_id"]

            if hgnc_id not in updates:
                new_genes.append(gene)
                continue

            current_update = updates[hgnc_id]
            action = current_update["action"]
            info = current_update["info"]

            # If action is delete we do not add the gene to new genes
            if action == "delete":
                continue

            if action == "edit":
                for field in info_fields:
                    if field in info:
                        gene[field] = info[field]
                new_genes.append(gene)

        new_panel["genes"] = new_genes
        new_panel["version"] = float(version)

        inserted_id = None
        # if the same version of the panel should be updated
        if new_panel["version"] == panel_obj["version"]:
            # replace panel_obj with new_panel
            result = self.panel_collection.find_one_and_replace(
                {"_id": panel_obj["_id"]},
                new_panel,
                return_document=pymongo.ReturnDocument.AFTER,
            )
            inserted_id = result["_id"]
        else:  # create a new version of the same panel
            new_panel.pop("_id")

            # archive the old panel
            panel_obj["is_archived"] = True
            self.update_panel(panel_obj=panel_obj, date_obj=panel_obj["date"])

            # insert the new panel
            inserted_id = self.panel_collection.insert_one(new_panel).inserted_id

        return inserted_id

    def latest_panels(self, institute_id):
        """Return the latest version of each panel."""
        panel_names = self.gene_panels(institute_id=institute_id).distinct("panel_name")
        for panel_name in panel_names:
            panel_obj = self.gene_panel(panel_name)
            yield panel_obj

    def clinical_symbols(self, case_obj):
        """Return all the clinical gene symbols for a case."""
        panel_ids = [panel["panel_id"] for panel in case_obj["panels"]]
        query = self.panel_collection.aggregate(
            [
                {"$match": {"_id": {"$in": panel_ids}}},
                {"$unwind": "$genes"},
                {"$group": {"_id": "$genes.symbol"}},
            ]
        )
        return set(item["_id"] for item in query)
