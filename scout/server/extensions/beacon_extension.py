"""Scout supports integration with the Clinical Genomics SciLifeLab Beacon
   cgbeacon2: https://github.com/Clinical-Genomics/cgbeacon2
"""
import datetime
import logging

from flask import flash, url_for
from flask_login import current_user

from scout.utils.scout_requests import delete_request_json, get_request_json, post_request_json

LOG = logging.getLogger(__name__)
DATASET_BUILDS = ["GRCh37", "GRCh38"]


class Beacon:
    """Interface to cgbeacon2 server instance, reachable via REST API"""

    def __init__(self):
        self.add_variants_url = None
        self.delete_variants_url = None
        self.token = None
        self.dataset_builds = DATASET_BUILDS

    def init_app(self, app):
        """Initialize the beacon extension and make its parametars available to the app."""
        self.token = app.config.get("BEACON_TOKEN")
        self.beacon_url = app.config.get("BEACON_URL")

        self.add_dataset_url = "/".join([self.beacon_url, "add_dataset"])
        self.add_variants_url = "/".join([self.beacon_url, "add"])
        self.delete_variants_url = "/".join([self.beacon_url, "delete"])

    def get_datasets(self):
        """Makes a call to the Beacon's info endpoint (/) and extracts a complete list of available datasets
        Returns:
            datasets(list): list of dataset _ids. Example: ["cust002_GRCh37", "cust000_GRCh38", ..]
        """
        datasets = []
        json_resp = get_request_json(url=f"{self.beacon_url}/")
        if json_resp.get("status_code") == 200:
            datasets = json_resp.get("content", {}).get("datasets", [])
        else:
            flash("Error retrieving Beacon's dataset list:{json_resp}", "warning")
        return [dset["id"] for dset in datasets]

    def base_submission_data(self, store, case_obj, form):
        """Create data dictionary to be sent as json data in a POST request to the beacon "add" endpoint

        Args:
            store(adapter.MongoAdapter)
            case_obj(dict): scout.models.Case
            form(ImmutableMultiDict): request form submitted by user. Example:
                [('case', 'internal_id'), ('samples', 'affected'), ('vcf_files', 'vcf_snv'), ('vcf_files', 'vcf_snv_research'), ('panels', '6246b25121d86882e127710c')]

        Returns:
            data(dict): a dictionary with base info to be used as json data in beacon add request (lacks path to VCF file to extract variants from)
        """
        # Initialize key/values to be sent in request:
        assembly = "GRCh38" if "38" in str(case_obj.get("genome_build", "37")) else "GRCh37"
        dataset_id = "_".join([case_obj["owner"], case_obj.get("build", assembly)])

        samples = []
        if form.get("samples") == "affected":
            samples = [
                ind["individual_id"]
                for ind in case_obj.get("individuals", [])
                if ind["phenotype"] == 2
            ]
        else:
            samples = [ind["individual_id"] for ind in case_obj.get("individuals")]

        data = {
            "dataset_id": dataset_id,
            "samples": samples,
            "assemblyId": assembly,
        }

        gene_ids = set()
        for panel in form.getlist("panels"):
            gene_ids.update(store.panel_to_genes(panel_id=panel, gene_format="hgnc_id"))

        if gene_ids:
            data["genes"] = {"ids": list(gene_ids), "id_type": "HGNC"}

        return data

    def add_dataset(self, institute_obj, dataset_id):
        """Add a missing dataset for an institute

        Args:
            institute_obj(dict): scout.models.Institute
            dataset_id(str): a string like this "<institute_id>_<genome_build>". Example: cust000_GRCh38
        """
        genome_build = dataset_id.split("_")[1]
        dataset_obj = {
            "id": dataset_id,
            "name": dataset_id,
            "description": f"Scout dataset. Institute:{institute_obj.get('display_name')} - genome build:{genome_build}",
            "build": genome_build,
            "authlevel": "public",  # Standard publuc dataset, this can be fixed later
            "version": "v1.0",
        }
        headers = {"X-Auth-Token": self.token}
        json_resp = post_request_json(url=self.add_dataset_url, headers=headers, data=dataset_obj)

        flash_code = "warning"

        if json_resp.get("status_code") == 200:  # If dataset was created successfully
            flash_code = "success"

        flash(f"Beacon responded: {json_resp}", flash_code)
        return json_resp.get("status_code")

    def add_variants(self, store, case_obj, form):
        """Adding variants from one of more individuals of case to Beacon

        Args:
            store(adapter.MongoAdapter)
            case_obj(dict): scout.models.Case
            form(ImmutableMultiDict): request form submitted by user. Example:
                [('case', 'internal_id'), ('samples', 'affected'), ('vcf_files', 'vcf_snv'), ('vcf_files', 'vcf_snv_research'), ('panels', '6246b25121d86882e127710c')]

        """

        # Check if user has rights to submit case to beacon
        user_obj = store.user(current_user.email)

        if "beacon_submitter" not in user_obj.get("roles", []):
            flash(
                "You don't have permission to use this tool yet. Please write to support and ask your institute primary contact to approve you as a Beacon submitter",
                "warning",
            )
            return

        base_data = self.base_submission_data(
            store, case_obj, form
        )  # create base dictionary to be used in add request. Lacks path to VCF file to extract variants from

        if base_data["dataset_id"] not in self.get_datasets():
            flash(
                f"In order to submit this sample, an admin needs to create a new Beacon dataset named '{base_data['dataset_id']}' first",
                "warning",
            )
            return

        headers = {"X-Auth-Token": self.token}
        update_case = False  # if True, update case with Beacon submission in Scout database

        # Loop over the list of VCF files selected by user (clinical SNVs, research SNVs, clinical SVs ..)
        for vcf_key in form.getlist("vcf_files"):
            base_data["vcf_path"] = case_obj["vcf_files"].get(
                vcf_key
            )  # add path to VCF file to request data

            # Send add variants request to Beacon
            json_resp = post_request_json(
                url=self.add_variants_url, headers=headers, data=base_data
            )

            status_code = "warning"
            # If Beacon accepts request (status code 202):
            if json_resp.get("status_code") == 202:
                status_code = "success"
                update_case = True

            flash(f"Beacon responded: {json_resp}", status_code)

        if update_case:
            submission = {
                "created_at": datetime.datetime.now(),
                "user": current_user.email,
                "samples": base_data["samples"],
                "panels": form.getlist("panels"),
                "vcf_files": form.getlist("vcf_files"),
            }
            store.case_collection.find_one_and_update(
                {"_id": case_obj["_id"]}, {"$set": {"beacon": submission}}
            )
            # Create a relative event in database
            self.update_event_collection(store, user_obj, case_obj, "beacon_add")

    def remove_variants(self, store, institute_id, case_obj):
        """
        Removing all variants from a scout case from Beacon

        Args:
            store(adapter.MongoAdapter)
            institute_id(str): _id of an institute
            case_obj(dict): scout.models.Case
        """
        # Check if user has rights to remove case from Beacon
        user_obj = store.user(current_user.email)

        if "beacon_submitter" not in user_obj.get("roles", []):
            flash("You don't have permission to edit Beacon submissions from Scout", "warning")

        assembly = "GRCh37" if "37" in str(case_obj.get("genome_build", "37")) else "GRCh38"

        # Prepare data to be sent as json to Beacon delete endpoint
        req_data = {
            "dataset_id": "_".join([institute_id, assembly]),
            "samples": case_obj.get("beacon", {}).get("samples", []),
        }
        headers = {"X-Auth-Token": self.token}

        json_resp = delete_request_json(
            url=self.delete_variants_url, headers=headers, data=req_data
        )

        update_case = False
        status_code = "warning"

        # If Beacon accepts request (status code 202):
        if json_resp.get("status_code") == 202:
            status_code = "success"
            update_case = True

        flash(f"Beacon responded: {json_resp}", status_code)

        if update_case:
            store.case_collection.update_one({"_id": case_obj["_id"]}, {"$unset": {"beacon": 1}})
            # Create a relative event in database
            self.update_event_collection(store, user_obj, case_obj, "beacon_remove")

    def update_event_collection(self, store, user_obj, case_obj, verb):
        """Update the event database collection whenever variants are added of remove from the BEACON_URL

        Args:
            store(adapter.MongoAdapter)
            user_obj(dict): scout.models.
            case_obj(dict): scout.models.User
            verb(string): "beacon_add" or "beacon_remove"
        """
        institute_obj = store.institute(case_obj["owner"])

        link = url_for(
            "cases.case", institute_id=institute_obj["_id"], case_name=case_obj["display_name"]
        )

        store.create_event(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link=link,
            category="case",
            verb=verb,
            subject=case_obj["display_name"],
            level="specific",
        )
