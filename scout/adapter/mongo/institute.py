import logging
from datetime import datetime

import pymongo

from scout.constants import PHENOTYPE_GROUPS
from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)


class InstituteHandler(object):
    def add_institute(self, institute_obj):
        """Add a institute to the database

        Args:
            institute_obj(Institute)
        """
        internal_id = institute_obj["internal_id"]
        display_name = institute_obj["display_name"]

        # Check if institute already exists
        if self.institute(institute_id=internal_id):
            raise IntegrityError("Institute {0} already exists in database".format(display_name))

        LOG.info(
            "Adding institute with internal_id: {0} and "
            "display_name: {1}".format(internal_id, display_name)
        )

        insert_info = self.institute_collection.insert_one(institute_obj)

        LOG.info("Institute saved")

    def update_institute(
        self,
        internal_id,
        sanger_recipient=None,
        sanger_recipients=None,
        coverage_cutoff=None,
        frequency_cutoff=None,
        display_name=None,
        remove_sanger=None,
        phenotype_groups=None,
        gene_panels=None,
        gene_panels_matching=None,
        group_abbreviations=None,
        add_groups=None,
        sharing_institutes=None,
        cohorts=None,
        loqusdb_ids=[],
        alamut_key=None,
        check_show_all_vars=None,
    ):
        """Update the information for an institute

        Args:
            internal_id(str): The internal institute id
            sanger_recipient(str): Email adress to add for sanger order
            sanger_recipients(list): A list of sanger recipients email addresses
            coverage_cutoff(int): Update coverage cutoff
            frequency_cutoff(float): New frequency cutoff
            display_name(str): New display name
            remove_sanger(str): Email adress for sanger user to be removed
            phenotype_groups(iterable(str)): New phenotype groups
            gene_panels(dict): a dictionary of panels with key=panel_name and value=display_name
            gene_panels_matching(dict): panels to limit search of matching variants (managed, causatives) to. Dict with key=panel_name and value=display_name
            group_abbreviations(iterable(str))
            add_groups(bool): If groups should be added. If False replace groups
            sharing_institutes(list(str)): Other institutes to share cases with
            cohorts(list(str)): patient cohorts
            loqusdb_ids(list(str)): list of ids of loqusdb instances Scout is connected to
            alamut_key(str): optional, Alamut Plus API key -> https://extranet.interactive-biosoftware.com/alamut-visual-plus_API.html

        Returns:
            updated_institute(dict)

        """
        add_groups = add_groups or False
        institute_obj = self.institute(internal_id)
        if not institute_obj:
            raise IntegrityError("Institute {} does not exist in database".format(internal_id))

        updates = {"$set": {}}
        updated_institute = institute_obj

        if sanger_recipient:
            user_obj = self.user(sanger_recipient)
            if not user_obj:
                raise IntegrityError("user {} does not exist in database".format(sanger_recipient))

            LOG.info(
                "Updating sanger recipients for institute: {0} with {1}".format(
                    internal_id, sanger_recipient
                )
            )
            updates["$push"] = {"sanger_recipients": sanger_recipient}

        if remove_sanger:
            LOG.info(
                "Removing sanger recipient {0} from institute: {1}".format(
                    remove_sanger, internal_id
                )
            )
            updates["$pull"] = {"sanger_recipients": remove_sanger}

        # Set a number of items
        GENERAL_SETTINGS = {
            "cohorts": cohorts,
            "collaborators": sharing_institutes,
            "coverage_cutoff": coverage_cutoff,
            "display_name": display_name,
            "frequency_cutoff": frequency_cutoff,
            "gene_panels": gene_panels,
            "gene_panels_matching": gene_panels_matching,
            "loqusdb_id": loqusdb_ids,
            "sanger_recipients": sanger_recipients,
        }
        for key, value in GENERAL_SETTINGS.items():
            if value not in [None, ""]:
                updates["$set"][key] = value

        if phenotype_groups is not None:
            if group_abbreviations:
                group_abbreviations = list(group_abbreviations)
            existing_groups = {}
            if add_groups:
                existing_groups = institute_obj.get("phenotype_groups", PHENOTYPE_GROUPS)
            for i, hpo_term in enumerate(phenotype_groups):
                hpo_obj = self.hpo_term(hpo_term)
                if not hpo_obj:
                    return "Term {} does not exist in database".format(hpo_term)
                hpo_id = hpo_obj["hpo_id"]
                description = hpo_obj["description"]
                abbreviation = None
                if group_abbreviations:
                    abbreviation = group_abbreviations[i]
                existing_groups[hpo_term] = {"name": description, "abbr": abbreviation}
            updates["$set"]["phenotype_groups"] = existing_groups

        if alamut_key is not None:
            updates["$set"]["alamut_key"] = (
                alamut_key if alamut_key != "" else None
            )  # allows to reset Alamut key to None

        updates["$set"]["check_show_all_vars"] = check_show_all_vars is not None

        if updates["$set"].keys() or updates.get("$push") or updates.get("$pull"):
            updates["$set"]["updated_at"] = datetime.now()
            updated_institute = self.institute_collection.find_one_and_update(
                {"_id": internal_id},
                updates,
                return_document=pymongo.ReturnDocument.AFTER,
            )

            LOG.info("Institute updated")

        return updated_institute

    def institute(self, institute_id):
        """Featch a single institute from the backend

        Args:
            institute_id(str)

        Returns:
            Institute object
        """
        institute_obj = self.institute_collection.find_one({"_id": institute_id})
        if institute_obj is None:
            LOG.debug("Could not find institute {0}".format(institute_id))

        return institute_obj

    def safe_genes_filter(self, institute_id):
        """Returns a list of "safe" HGNC IDs to filter variants with. These genes are retrieved from the institute.gene_panels_matching
        Can be used to limit secondary findings when retrieving other causatives or matching managed variants

        Args:
            institute_id(str): _id of an institute

        Returns:
            safe_genes(list of HGNC ids)
        """
        safe_genes = []
        institute_obj = self.institute(institute_id)
        if not institute_obj:
            return safe_genes  # return an empty list
        for panel_name in institute_obj.get("gene_panels_matching", {}).keys():
            safe_genes += self.panel_to_genes(panel_name=panel_name, gene_format="hgnc_id")
        return safe_genes

    def institutes(self, institute_ids=None):
        """Fetch all institutes.

        Args:
            institute_ids(list(str))

        Returns:
            res(pymongo.Cursor)
        """
        query = {}
        if institute_ids:
            query["_id"] = {"$in": institute_ids}
        return self.institute_collection.find(query)
