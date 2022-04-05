"""Scout supports integration with the Clinical Genomics SciLifeLab Beacon
   cgbeacon2: https://github.com/Clinical-Genomics/cgbeacon2
"""
import datetime
import json

from flask import flash
from flask_login import current_user
from werkzeug.datastructures import Headers

from scout.utils.scout_requests import delete_request_json, post_request_json


class Beacon:
    """Interface to cgbeacon2 server instance, reachable via REST API"""

    def __init__(self):
        self.add_variants_url = None
        self.delete_variants_url = None
        self.token = None

    def init_app(self, app):
        """Initialize the beacon extension and make its parametars available to the app."""
        self.token = app.config.get("BEACON_TOKEN")
        beacon_url = app.config.get("BEACON_URL")

        self.add_variants_url = "/".join([beacon_url, "add"])
        self.delete_variants_url = "/".join([beacon_url, "delete"])

    def base_submission_data(self, store, case_obj, form):
        """Create data dictionary to be send as json data in a POST request to the beacon "add" endpoint

        Args:
            store(adapter.MongoAdapter)
            case_obj(dict): scout.models.Case
            form(ImmutableMultiDict): request form submitted by user. Example:
                [('case', 'internal_id'), ('samples', 'affected'), ('vcf_files', 'vcf_snv'), ('vcf_files', 'vcf_snv_research'), ('panels', '6246b25121d86882e127710c')]

        Returns:
            data(dict): a dictionary with base info to be use as json data in beacon add request (lacks path to VCF file to extract variants from)
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
            flash("You don't have permission to use the Beacon tool", "warning")
            return

        base_data = self.base_submission_data(
            store, case_obj, form
        )  # create base dictionary to be used in add request. Lacks path to VCF file to extract variants from

        update_case = False  # if True, update case with Beacon submission in Scout database

        headers = Headers()
        headers = {"X-Auth-Token": self.token}

        # Loop over the list of VCF files selected by user (clinical SNVs, research SNVs, clinical SVs ..)
        for vcf_key in form.getlist("vcf_files"):
            base_data["vcf_path"] = case_obj["vcf_files"].get(
                vcf_key
            )  # add path to VCF file to request data

            flash(f"Sending request data to Beacon:{base_data}")

            # Send add variants request to Beacon
            json_resp = post_request_json(
                url=self.add_variants_url, headers=headers, data=base_data
            )

            if json_resp.get("status_code") == 200:
                flash(f"Beacon responded: {json_resp}", "success")
                update_case = True
            else:
                flash(
                    f"Error while submitting variant data to Beacon: {json_resp}. Request data:{base_data}",
                    "warning",
                )

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
        headers = Headers()
        headers = {"X-Auth-Token": self.token}

        json_resp = delete_request_json(
            url=self.delete_variants_url, headers=headers, data=req_data
        )

        if json_resp.get("status_code") == 200:
            flash(f"Beacon responded: {json_resp}", "success")
            store.case_collection.update_one({"_id": case_obj["_id"]}, {"$unset": {"beacon": 1}})
        else:
            flash(f"Error trying to remove variants from Beacon: {json_resp}", "warning")
