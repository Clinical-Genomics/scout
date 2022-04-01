"""Scout supports integration with the Clinical Genomics SciLifeLab Beacon
   cgbeacon2: https://github.com/Clinical-Genomics/cgbeacon2
"""
import json

from werkzeug.datastructures import Headers

# from scout.utils import scout_requests


class Beacon:
    """Interface to cgbeacon2 server instance, reachable via REST API"""

    def __init__(self):
        self.add_variants_url = None
        self.add_dataset_url = None
        self.delete_variants_url = None
        self.token = None

    def init_app(self, app):
        """Initialize the beacon extension and make its parametars available to the app."""
        endpoints = app.config.get("BEACON_ENDPOINTS")
        beacon_url = app.config.get("BEACON_URL")

        self.add_variants_url = "/".join([beacon_url, endpoints.get("add_variants")])
        self.add_dataset_url = "/".join([beacon_url, endpoints.get("add_dataset")])
        self.delete_variants_url = "/".join([beacon_url, endpoints.get("remove_variants")])
        self.token = app.config.get("BEACON_TOKEN")


"""
    def request(self, url, data):
        Send a request to MatchMaker and return its response

        Args:
            url(str): could be either "beacon-host/add" or "beacon-host/add_dataset"
            data(dict): data to be sent in request as json

        Returns:
            json_response(dict): beacon server response

        headers = Headers()
        headers = {"X-Auth-Token": self.token}

        json_response = scout_requests.post_request_json(url=url, headers=headers, data=data)
        return json_response



def prepare_beacon_req_params():
    Prepares URL and Headers for sending a request to the beacon server.

    Returns:
        url, headers(tuple)
    req_url = current_app.config.get("BEACON_URL")
    beacon_token = current_app.config.get("BEACON_TOKEN")
    if not req_url or not beacon_token:
        return
    req_headers = JSON_HEADERS
    req_headers["X-Auth-Token"] = beacon_token
    return req_url, req_headers


def beacon_remove(case_id):
    Remove all variants from a case in Beacon by handling a POST request to the /apiv1.0/delete Beacon endpoint.

    Args:
        case_id(str): A case _id

    if prepare_beacon_req_params() is None:
        flash(
            "Please check config file. It should contain both BEACON_URL and BEACON_TOKEN",
            "warning",
        )
        return
    request_url, req_headers = prepare_beacon_req_params()

    case_obj = store.case(case_id=case_id)
    beacon_submission = case_obj.get("beacon")

    if beacon_submission is None:
        flash("Couldn't find a valid beacon submission for this case", "warning")
        return

    # Prepare beacon request data
    assembly = "GRCh37" if "37" in str(case_obj["genome_build"]) else "GRCh38"
    dataset_id = "_".join([case_obj["owner"], assembly])
    samples = [sample for sample in beacon_submission.get("samples", [])]
    data = {"dataset_id": dataset_id, "samples": samples}
    resp = delete_request_json("/".join([request_url, "delete"]), req_headers, data)
    flash_color = "success"
    message = resp.get("content", {}).get("message")
    if resp.get("status_code") == 200:
        store.case_collection.update_one({"_id": case_obj["_id"]}, {"$unset": {"beacon": 1}})
    else:
        flash_color = "warning"
    flash(f"Beacon responded:{message}", flash_color)


def beacon_add(form):
    Save variants from one or more case samples to the Beacon server.
       Handle a POST request to the /apiv1.0/add Beacon endpoint

    Args:
        form(werkzeug.datastructures.ImmutableMultiDict): beacon submission form


    if prepare_beacon_req_params() is None:
        flash(
            "Please check config file. It should contain both BEACON_URL and BEACON_TOKEN",
            "warning",
        )
        return
    request_url, req_headers = prepare_beacon_req_params()

    case_obj = store.case(case_id=form.get("case"))
    # define case individuals (individual_id, same as in VCF) to filter VCF files with
    individuals = []
    if form.get("samples") == "affected":
        individuals = [
            ind["individual_id"] for ind in case_obj["individuals"] if ind["phenotype"] == 2
        ]
    else:
        individuals = [ind["individual_id"] for ind in case_obj["individuals"]]

    # define genes to filter VCF files with
    gene_filter = set()
    for panel in form.getlist("panels"):
        gene_filter.update(store.panel_to_genes(panel_id=panel, gene_format="hgnc_id"))
    gene_filter = list(gene_filter)

    submission = {
        "created_at": datetime.datetime.now(),
        "user": current_user.email,
        "samples": individuals,
        "panels": form.getlist("panels"),
        "vcf_files": [],
    }

    # Prepare beacon request data
    assembly = "GRCh37" if "37" in str(case_obj["genome_build"]) else "GRCh38"
    data = {
        "dataset_id": "_".join([case_obj["owner"], assembly]),
        "samples": individuals,
        "assemblyId": assembly,
    }
    if gene_filter:  # Gene filter is not mandatory
        data["genes"] = {"ids": gene_filter, "id_type": "HGNC"}

    # loop over selected VCF files and send an add request to Beacon for each one of them
    vcf_files = form.getlist("vcf_files")
    if not vcf_files:
        flash("Please select at least one VCF file to save to Beacon", "warning")
        return
    for vcf_key in form.getlist("vcf_files"):
        data["vcf_path"] = case_obj["vcf_files"].get(vcf_key)
        resp = post_request_json("/".join([request_url, "add"]), data, req_headers)
        if resp.get("status_code") != 200:
            flash(f"Beacon responded:{resp.get('content',{}).get('message')}", "warning")
            continue
        submission["vcf_files"].append(vcf_key)

    if len(submission["vcf_files"]) > 0:
        flash(
            f"Variants from the following files are going to be saved to Beacon:{submission['vcf_files']}",
            "success",
        )
        store.case_collection.find_one_and_update(
            {"_id": case_obj["_id"]}, {"$set": {"beacon": submission}}
        )
    return
"""
