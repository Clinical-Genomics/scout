import logging
from datetime import datetime
from typing import List, Optional, Union

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
        internal_id: str,
        sanger_recipient: Optional[str] = None,
        sanger_recipients: Optional[List[str]] = None,
        coverage_cutoff: Optional[int] = None,
        frequency_cutoff: Optional[float] = None,
        show_all_cases_status: Optional[List[str]] = None,
        display_name: Optional[str] = None,
        remove_sanger: Optional[str] = None,
        phenotype_groups: Optional[List[str]] = None,
        gene_panels: Optional[dict] = None,
        gene_panels_matching: Optional[dict] = None,
        group_abbreviations: Optional[List[str]] = None,
        add_groups: Optional[bool] = None,
        sharing_institutes: Optional[List[str]] = None,
        cohorts: Optional[List[str]] = None,
        loqusdb_ids: Optional[List[str]] = [],
        alamut_key: Optional[str] = None,
        alamut_institution: Optional[str] = None,
        check_show_all_vars: Optional[str] = None,
        clinvar_key: Optional[str] = None,
        clinvar_submitters: Optional[List[str]] = None,
        soft_filters: Optional[dict] = None,
    ) -> Union[dict, str]:
        """Update the information for an institute."""

        def get_phenotype_groups() -> dict:
            """Returns a dictionary with phenotype descriptions and abbreviations."""
            existing_groups = (
                institute_obj.get("phenotype_groups", PHENOTYPE_GROUPS) if add_groups else {}
            )

            if not phenotype_groups:
                return existing_groups

            group_abbreviations_list = list(group_abbreviations) if group_abbreviations else []

            for i, hpo_term in enumerate(phenotype_groups):
                hpo_obj = self.hpo_term(hpo_term)
                if not hpo_obj:
                    continue

                existing_groups[hpo_term] = {
                    "name": hpo_obj["description"],
                    "abbr": group_abbreviations_list[i] if group_abbreviations_list else None,
                }

            return existing_groups

        institute_obj = self.institute(internal_id)
        if not institute_obj:
            raise IntegrityError("Institute {} does not exist in database".format(internal_id))

        updates = {"$set": {}, "$unset": {}}
        updated_institute = institute_obj

        if sanger_recipient:
            old_recipients = institute_obj.get("sanger_recipients", [])
            sanger_recipients = old_recipients + [sanger_recipient]

        if remove_sanger:
            sanger_recipients = list(
                set(institute_obj.get("sanger_recipients", [])) - set([remove_sanger])
            )

        UPDATE_SETTINGS = {
            "alamut_institution": alamut_institution,  # Admin setting
            "alamut_key": alamut_key,  # Admin setting
            "check_show_all_vars": check_show_all_vars is not None,
            "clinvar_key": clinvar_key,  # Admin setting
            "clinvar_submitters": clinvar_submitters,
            "cohorts": cohorts,
            "collaborators": sharing_institutes,
            "coverage_cutoff": coverage_cutoff,
            "display_name": display_name,
            "frequency_cutoff": frequency_cutoff,
            "gene_panels": gene_panels,
            "gene_panels_matching": gene_panels_matching,
            "loqusdb_id": loqusdb_ids,
            "phenotype_groups": get_phenotype_groups(),
            "sanger_recipients": sanger_recipients,
            "show_all_cases_status": show_all_cases_status,  # Admin setting
            "soft_filters": soft_filters,  # Admin setting
        }
        for key, value in UPDATE_SETTINGS.items():
            if bool(value) is True:
                updates["$set"][key] = value
            else:
                updates["$unset"][key] = ""  # Remove the key from the institute document

        if any(updates.get(op) for op in ["$set", "$unset"]):
            updates["$set"]["updated_at"] = datetime.now()
            updated_institute = self.institute_collection.find_one_and_update(
                {"_id": internal_id},
                updates,
                return_document=pymongo.ReturnDocument.AFTER,
            )
            LOG.info("Institute updated")

        return updated_institute

    def institute(self, institute_id: str):
        """Featch a single institute from the backend

        Returns:
            Institute object
        """
        institute_obj = self.institute_collection.find_one({"_id": institute_id})
        if institute_obj is None:
            LOG.debug("Could not find institute {0}".format(institute_id))

        return institute_obj

    def safe_genes_filter(self, institute_id: str) -> List[int]:
        """Returns a list of "safe" HGNC IDs to filter variants with. These genes are retrieved from the institute.gene_panels_matching
        Can be used to limit secondary findings when retrieving other causatives or matching managed variants.
        """
        safe_genes = []
        institute_obj = self.institute(institute_id)
        if not institute_obj:
            return safe_genes  # return an empty list
        for panel_name in institute_obj.get("gene_panels_matching", {}).keys():
            safe_genes += self.panel_to_genes(panel_name=panel_name, gene_format="hgnc_id")
        return list(set(safe_genes))

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
