# -*- coding: utf-8 -*-
import datetime
import itertools
import logging
import os

import query_phenomizer
import requests
from bs4 import BeautifulSoup
from flask import current_app, url_for, flash
from flask_login import current_user
from flask_mail import Message
from xlsxwriter import Workbook

from scout.constants import (
    CANCER_PHENOTYPE_MAP,
    MT_EXPORT_HEADER,
    PHENOTYPE_GROUPS,
    PHENOTYPE_MAP,
    SEX_MAP,
    VERBS_MAP,
)
from scout.constants.variant_tags import (
    CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
    CANCER_TIER_OPTIONS,
    DISMISS_VARIANT_OPTIONS,
    GENETIC_MODELS,
    MANUAL_RANK_OPTIONS,
)
from scout.export.variant import export_mt_variants
from scout.parse.matchmaker import (
    genomic_features,
    hpo_terms,
    omim_terms,
    parse_matches,
)
from scout.server.blueprints.variant.controllers import variant as variant_decorator
from scout.server.utils import institute_and_case
from scout.utils.matchmaker import matchmaker_request

LOG = logging.getLogger(__name__)

STATUS_MAP = {"solved": "bg-success", "archived": "bg-warning"}


def case(store, institute_obj, case_obj):
    """Preprocess a single case.

    Prepare the case to be displayed in the case view.

    Args:
        store(adapter.MongoAdapter)
        institute_obj(models.Institute)
        case_obj(models.Case)

    Returns:
        data(dict): includes the cases, how many there are and the limit.

    """
    # Convert individual information to more readable format
    case_obj["individual_ids"] = []
    for individual in case_obj["individuals"]:
        try:
            sex = int(individual.get("sex", 0))
        except ValueError as err:
            sex = 0
        individual["sex_human"] = SEX_MAP[sex]

        pheno_map = PHENOTYPE_MAP
        if case_obj.get("track", "rare") == "cancer":
            pheno_map = CANCER_PHENOTYPE_MAP

        individual["phenotype_human"] = pheno_map.get(individual["phenotype"])
        case_obj["individual_ids"].append(individual["individual_id"])

    case_obj["assignees"] = [store.user(user_email) for user_email in case_obj.get("assignees", [])]

    # Fetch the variant objects for suspects and causatives
    suspects = [
        store.variant(variant_id) or variant_id for variant_id in case_obj.get("suspects", [])
    ]
    causatives = [
        store.variant(variant_id) or variant_id for variant_id in case_obj.get("causatives", [])
    ]
    # check for partial causatives and associated phenotypes
    partial_causatives = []
    if case_obj.get("partial_causatives"):
        for var_id, values in case_obj["partial_causatives"].items():
            causative_obj = {
                "variant": store.variant(var_id) or var_id,
                "omim_terms": values.get("diagnosis_phenotypes"),
                "hpo_terms": values.get("phenotype_terms"),
            }
            partial_causatives.append(causative_obj)

    # Set of all unique genes in the default gene panels
    distinct_genes = set()
    case_obj["panel_names"] = []
    case_obj["outdated_panels"] = {}
    for panel_info in case_obj.get("panels", []):
        if not panel_info.get("is_default"):
            continue
        panel_name = panel_info["panel_name"]
        panel_version = panel_info.get("version")
        panel_obj = store.gene_panel(panel_name, version=panel_version)
        latest_panel = store.gene_panel(panel_name)
        if not panel_obj:
            panel_obj = latest_panel
            if not panel_obj:
                flash(f"Case default panel '{panel_name}' could not be found.", "warning")
                continue
            flash(
                f"Case default panel '{panel_name}' version {panel_version} could not be found, using latest existing version",
                "warning",
            )

        # Check if case-specific panel is up-to-date with latest version of the panel
        if panel_obj["version"] < latest_panel["version"]:
            extra_genes, missing_genes = _check_outdated_gene_panel(panel_obj, latest_panel)
            if extra_genes or missing_genes:
                case_obj["outdated_panels"][panel_name] = {
                    "missing_genes": missing_genes,
                    "extra_genes": extra_genes,
                }

        distinct_genes.update([gene["hgnc_id"] for gene in panel_obj.get("genes", [])])
        full_name = "{} ({})".format(panel_obj["display_name"], panel_obj["version"])
        case_obj["panel_names"].append(full_name)

    case_obj["default_genes"] = list(distinct_genes)

    for hpo_term in itertools.chain(
        case_obj.get("phenotype_groups", []), case_obj.get("phenotype_terms", [])
    ):
        hpo_term["hpo_link"] = "http://hpo.jax.org/app/browse/term/{}".format(
            hpo_term["phenotype_id"]
        )

    rank_model_link_prefix = current_app.config.get("RANK_MODEL_LINK_PREFIX", "")
    if case_obj.get("rank_model_version"):
        rank_model_link_postfix = current_app.config.get("RANK_MODEL_LINK_POSTFIX", "")
        rank_model_link = "".join(
            [
                rank_model_link_prefix,
                str(case_obj["rank_model_version"]),
                rank_model_link_postfix,
            ]
        )
        print(rank_model_link)
        case_obj["rank_model_link"] = rank_model_link
    sv_rank_model_link_prefix = current_app.config.get("SV_RANK_MODEL_LINK_PREFIX", "")
    if case_obj.get("sv_rank_model_version"):
        sv_rank_model_link_postfix = current_app.config.get("SV_RANK_MODEL_LINK_POSTFIX", "")
        case_obj["sv_rank_model_link"] = "".join(
            [
                sv_rank_model_link_prefix,
                str(case_obj["sv_rank_model_version"]),
                sv_rank_model_link_postfix,
            ]
        )
    # other collaborators than the owner of the case
    o_collaborators = []
    for collab_id in case_obj.get("collaborators", []):
        if collab_id != case_obj["owner"] and store.institute(collab_id):
            o_collaborators.append(store.institute(collab_id))

    case_obj["o_collaborators"] = [
        (collab_obj["_id"], collab_obj["display_name"]) for collab_obj in o_collaborators
    ]

    collab_ids = None
    if institute_obj.get("collaborators"):
        collab_ids = [
            (collab["_id"], collab["display_name"])
            for collab in store.institutes()
            if institute_obj.get("collaborators")
            and collab["_id"] in institute_obj.get("collaborators")
        ]

    events = list(store.events(institute_obj, case=case_obj))
    for event in events:
        event["verb"] = VERBS_MAP[event["verb"]]

    case_obj["clinvar_variants"] = store.case_to_clinVars(case_obj["_id"])

    # if updated_at is a list, set it to the last update datetime
    if case_obj.get("updated_at") and isinstance(case_obj["updated_at"], list):
        case_obj["updated_at"] = max(case_obj["updated_at"])

    # Phenotype groups can be specific for an institute, there are some default groups
    pheno_groups = institute_obj.get("phenotype_groups") or PHENOTYPE_GROUPS

    # complete OMIM diagnoses specific for this case
    omim_terms = {term["disease_nr"]: term for term in store.case_omim_diagnoses(case_obj)}

    data = {
        "status_class": STATUS_MAP.get(case_obj["status"]),
        "other_causatives": [var for var in store.check_causatives(case_obj=case_obj)],
        "comments": store.events(institute_obj, case=case_obj, comments=True),
        "hpo_groups": pheno_groups,
        "events": events,
        "suspects": suspects,
        "causatives": causatives,
        "partial_causatives": partial_causatives,
        "collaborators": collab_ids,
        "cohort_tags": institute_obj.get("cohorts", []),
        "omim_terms": omim_terms,
        "manual_rank_options": MANUAL_RANK_OPTIONS,
        "cancer_tier_options": CANCER_TIER_OPTIONS,
    }

    return data


def _check_outdated_gene_panel(panel_obj, latest_panel):
    """Compare genes of a case gene panel with the latest panel version and return differences

    Args:
        panel_obj(dict): the gene panel of a case
        latest_panel(dict): the latest version of that gene panel

    returns:
        missing_genes, extra_genes
    """
    # Create a list of minified gene object for the case panel {hgnc_id, gene_symbol}
    case_panel_genes = [
        {"hgnc_id": gene["hgnc_id"], "symbol": gene.get("symbol", gene["hgnc_id"])}
        for gene in panel_obj["genes"]
    ]
    # And for the latest panel
    latest_panel_genes = [
        {"hgnc_id": gene["hgnc_id"], "symbol": gene.get("symbol", gene["hgnc_id"])}
        for gene in latest_panel["genes"]
    ]
    # Extract the genes unique to case panel
    extra_genes = [gene["symbol"] for gene in case_panel_genes if gene not in latest_panel_genes]
    # Extract the genes unique to latest panel
    missing_genes = [gene["symbol"] for gene in latest_panel_genes if gene not in case_panel_genes]
    return extra_genes, missing_genes


def case_report_content(store, institute_obj, case_obj):
    """Gather contents to be visualized in a case report

    Args:
        store(adapter.MongoAdapter)
        institute_obj(models.Institute)
        case_obj(models.Case)

    Returns:
        data(dict)

    """
    variant_types = {
        "causatives_detailed": "causatives",
        "partial_causatives_detailed": "partial_causatives",
        "suspects_detailed": "suspects",
        "classified_detailed": "acmg_classification",
        "tagged_detailed": "manual_rank",
        "tier_detailed": "cancer_tier",
        "dismissed_detailed": "dismiss_variant",
        "commented_detailed": "is_commented",
    }
    data = case_obj

    for individual in data["individuals"]:
        try:
            sex = int(individual.get("sex", 0))
        except ValueError as err:
            sex = 0
        individual["sex_human"] = SEX_MAP[sex]
        individual["phenotype_human"] = PHENOTYPE_MAP.get(individual["phenotype"])

    dismiss_options = DISMISS_VARIANT_OPTIONS
    if case_obj.get("track") == "cancer":
        dismiss_options = {
            **DISMISS_VARIANT_OPTIONS,
            **CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
        }

    # Add the case comments
    data["comments"] = store.events(institute_obj, case=case_obj, comments=True)

    data["manual_rank_options"] = MANUAL_RANK_OPTIONS
    data["cancer_tier_options"] = CANCER_TIER_OPTIONS
    data["dismissed_options"] = dismiss_options
    data["genetic_models"] = dict(GENETIC_MODELS)
    data["report_created_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    evaluated_variants = {vt: [] for vt in variant_types}
    # We collect all causatives (including the partial ones) and suspected variants
    # These are handeled in separate since they are on case level
    for var_type in ["causatives", "suspects", "partial_causatives"]:
        # These include references to variants
        vt = "_".join([var_type, "detailed"])
        for var_id in case_obj.get(var_type, []):
            variant_obj = store.variant(var_id)
            if not variant_obj:
                continue
            if var_type == "partial_causatives":  # Collect associated phenotypes
                variant_obj["phenotypes"] = [
                    value for key, value in case_obj["partial_causatives"].items() if key == var_id
                ][0]
            evaluated_variants[vt].append(variant_obj)

    ## get variants for this case that are either classified, commented, tagged or dismissed.
    for var_obj in store.evaluated_variants(case_id=case_obj["_id"]):
        # Check which category it belongs to
        for vt in variant_types:
            keyword = variant_types[vt]
            # When found we add it to the categpry
            # Eac variant can belong to multiple categories
            if keyword not in var_obj:
                continue
            evaluated_variants[vt].append(var_obj)

    for var_type in evaluated_variants:
        decorated_variants = []
        for var_obj in evaluated_variants[var_type]:
            # We decorate the variant with some extra information
            decorated_info = variant_decorator(
                store=store,
                institute_id=institute_obj["_id"],
                case_name=case_obj["display_name"],
                variant_id=None,
                variant_obj=var_obj,
                add_case=False,
                add_other=False,
                get_overlapping=False,
                add_compounds=False,
                variant_type=var_obj["category"],
                institute_obj=institute_obj,
                case_obj=case_obj,
            )
            decorated_variants.append(decorated_info["variant"])
        # Add the decorated variants to the case
        data[var_type] = decorated_variants

    return data


def coverage_report_contents(store, institute_obj, case_obj, base_url):
    """Posts a request to chanjo-report and capture the body of the returned response to include it in case report

    Args:
        store(adapter.MongoAdapter)
        institute_obj(models.Institute)
        case_obj(models.Case)
        base_url(str): base url of server

    Returns:
        coverage_data(str): string rendering of the content between <body </body> tags of a coverage report
    """

    request_data = {}
    # extract sample ids from case_obj and add them to the post request object:
    request_data["sample_id"] = [ind["individual_id"] for ind in case_obj["individuals"]]

    # extract default panel names and default genes from case_obj and add them to the post request object
    distinct_genes = set()
    panel_names = []
    for panel_info in case_obj.get("panels", []):
        if panel_info.get("is_default") is False:
            continue
        panel_obj = store.gene_panel(panel_info["panel_name"], version=panel_info.get("version"))
        distinct_genes.update([gene["hgnc_id"] for gene in panel_obj.get("genes", [])])
        full_name = "{} ({})".format(panel_obj["display_name"], panel_obj["version"])
        panel_names.append(full_name)
    panel_names = " ,".join(panel_names)
    request_data["gene_ids"] = ",".join([str(gene_id) for gene_id in list(distinct_genes)])
    request_data["panel_name"] = panel_names
    request_data["request_sent"] = datetime.datetime.now()

    # add institute-specific cutoff level to the post request object
    request_data["level"] = institute_obj.get("coverage_cutoff", 15)

    # send get request to chanjo report
    # disable default certificate verification
    resp = requests.post(base_url + "reports/report", data=request_data)

    # read response content
    soup = BeautifulSoup(resp.text)

    # remove links in the printed version of coverage report
    for tag in soup.find_all("a"):
        tag.replaceWith("")

    # extract body content using BeautifulSoup
    coverage_data = "".join(["%s" % x for x in soup.body.contents])

    return coverage_data


def mt_excel_files(store, case_obj, temp_excel_dir):
    """Collect MT variants and format line of a MT variant report
    to be exported in excel format

    Args:
        store(adapter.MongoAdapter)
        case_obj(models.Case)
        temp_excel_dir(os.Path): folder where the temp excel files are written to

    Returns:
        written_files(int): the number of files written to temp_excel_dir

    """
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    samples = case_obj.get("individuals")

    query = {"chrom": "MT"}
    mt_variants = list(
        store.variants(case_id=case_obj["_id"], query=query, nr_of_variants=-1, sort_key="position")
    )

    written_files = 0
    for sample in samples:
        sample_id = sample["individual_id"]
        display_name = sample["display_name"]
        sample_lines = export_mt_variants(variants=mt_variants, sample_id=sample_id)

        # set up document name
        document_name = ".".join([case_obj["display_name"], display_name, today]) + ".xlsx"
        workbook = Workbook(os.path.join(temp_excel_dir, document_name))
        Report_Sheet = workbook.add_worksheet()

        # Write the column header
        row = 0
        for col, field in enumerate(MT_EXPORT_HEADER):
            Report_Sheet.write(row, col, field)

        # Write variant lines, after header (start at line 1)
        for row, line in enumerate(sample_lines, 1):  # each line becomes a row in the document
            for col, field in enumerate(line):  # each field in line becomes a cell
                Report_Sheet.write(row, col, field)
        workbook.close()

        if os.path.exists(os.path.join(temp_excel_dir, document_name)):
            written_files += 1

    return written_files


def update_synopsis(store, institute_obj, case_obj, user_obj, new_synopsis):
    """Update synopsis."""
    # create event only if synopsis was actually changed
    if case_obj["synopsis"] != new_synopsis:
        link = url_for(
            "cases.case",
            institute_id=institute_obj["_id"],
            case_name=case_obj["display_name"],
        )
        store.update_synopsis(institute_obj, case_obj, user_obj, link, content=new_synopsis)


def update_individuals(store, institute_obj, case_obj, user_obj, ind, age, tissue):
    """Handle update of individual data (age and/or Tissue type) for a case"""

    case_individuals = case_obj.get("individuals")
    for subject in case_individuals:
        if subject["individual_id"] == ind:
            if age:
                subject["age"] = round(float(age), 1)
            else:
                subject["age"] = None
            if tissue:
                subject["tissue_type"] = tissue

    case_obj["individuals"] = case_individuals
    # update case with new individual data
    store.update_case(case_obj, keep_date=True)

    # create an associated event
    link = url_for(
        "cases.case",
        institute_id=institute_obj["_id"],
        case_name=case_obj["display_name"],
    )
    store.create_event(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        category="case",
        verb="update_individual",
        subject=case_obj["display_name"],
    )


def update_cancer_samples(
    store, institute_obj, case_obj, user_obj, ind, tissue, tumor_type, tumor_purity
):
    """Handle update of sample data data (tissue, tumor_type, tumor_purity) for a cancer case"""

    case_samples = case_obj.get("individuals")
    for sample in case_samples:
        if sample["individual_id"] == ind:
            if tissue:
                sample["tissue_type"] = tissue
            if tumor_type:
                sample["tumor_type"] = tumor_type
            else:
                sample["tumor_type"] = None
            if tumor_purity:
                sample["tumor_purity"] = float(tumor_purity)
            else:
                sample["tumor_purity"] = None

    case_obj["individuals"] = case_samples
    # update case with new sample data
    store.update_case(case_obj, keep_date=True)

    # create an associated event
    link = url_for(
        "cases.case",
        institute_id=institute_obj["_id"],
        case_name=case_obj["display_name"],
    )

    store.create_event(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        category="case",
        verb="update_sample",
        subject=case_obj["display_name"],
    )


def hpo_diseases(username, password, hpo_ids, p_value_treshold=1):
    """Return the list of HGNC symbols that match annotated HPO terms.

    Args:
        username (str): username to use for phenomizer connection
        password (str): password to use for phenomizer connection

    Returns:
        query_result: a generator of dictionaries on the form
        {
            'p_value': float,
            'disease_source': str,
            'disease_nr': int,
            'gene_symbols': list(str),
            'description': str,
            'raw_line': str
        }
    """
    # skip querying Phenomizer unless at least one HPO terms exists
    try:
        results = query_phenomizer.query(username, password, *hpo_ids)
        diseases = [result for result in results if result["p_value"] <= p_value_treshold]
        return diseases
    except SystemExit:
        return None


def rerun(store, mail, current_user, institute_id, case_name, sender, recipient):
    """Request a rerun by email."""

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for("cases.case", institute_id=institute_id, case_name=case_name)

    if case_obj.get("rerun_requested") and case_obj["rerun_requested"] is True:
        flash("Rerun already pending", "info")
        return

    store.request_rerun(institute_obj, case_obj, user_obj, link)

    # this should send a JSON document to the SuSy API in the future
    html = """
        <p>{institute}: {case} ({case_id})</p>
        <p>Re-run requested by: {name}</p>
    """.format(
        institute=institute_obj["display_name"],
        case=case_obj["display_name"],
        case_id=case_obj["_id"],
        name=user_obj["name"].encode(),
    )

    # compose and send the email message
    msg = Message(
        subject=("SCOUT: request RERUN for {}".format(case_obj["display_name"])),
        html=html,
        sender=sender,
        recipients=[recipient],
        # cc the sender of the email for confirmation
        cc=[user_obj["email"]],
    )
    if recipient:
        mail.send(msg)
    else:
        LOG.error("Cannot send rerun message: no recipient defined in config.")


def update_default_panels(store, current_user, institute_id, case_name, panel_ids):
    """Update default panels for a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for("cases.case", institute_id=institute_id, case_name=case_name)
    panel_objs = [store.panel(panel_id) for panel_id in panel_ids]
    store.update_default_panels(institute_obj, case_obj, user_obj, link, panel_objs)


def update_clinical_filter_hpo(store, current_user, institute_id, case_name, hpo_clinical_filter):
    """Update HPO clinical filter use for a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for("cases.case", institute_id=institute_id, case_name=case_name)
    store.update_clinical_filter_hpo(institute_obj, case_obj, user_obj, link, hpo_clinical_filter)


def vcf2cytosure(store, institute_id, case_name, individual_id):
    """vcf2cytosure CGH file for inidividual."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)

    for individual in case_obj["individuals"]:
        if individual["individual_id"] == individual_id:
            individual_obj = individual

    return (individual_obj["display_name"], individual_obj["vcf2cytosure"])


def multiqc(store, institute_id, case_name):
    """Find MultiQC report for the case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    return dict(institute=institute_obj, case=case_obj)


def mme_add(
    store,
    user_obj,
    case_obj,
    add_gender,
    add_features,
    add_disorders,
    genes_only,
    mme_base_url,
    mme_accepts,
    mme_token,
):
    """Add a patient to MatchMaker server

    Args:
        store(adapter.MongoAdapter)
        user_obj(dict) a scout user object (to be added as matchmaker contact)
        case_obj(dict) a scout case object
        add_gender(bool) if True case gender will be included in matchmaker
        add_features(bool) if True HPO features will be included in matchmaker
        add_disorders(bool) if True OMIM diagnoses will be included in matchmaker
        genes_only(bool) if True only genes and not variants will be shared
        mme_base_url(str) base url of the MME server
        mme_accepts(str) request content accepted by MME server
        mme_token(str) auth token of the MME server

    Returns:
        submitted_info(dict) info submitted to MatchMaker and its responses
    """

    if not mme_base_url or not mme_accepts or not mme_token:
        return "Please check that Matchmaker connection parameters are valid"
    url = "".join([mme_base_url, "/patient/add"])
    features = []  # this is the list of HPO terms
    disorders = []  # this is the list of OMIM diagnoses
    g_features = []

    # create contact dictionary
    contact_info = {
        "name": user_obj["name"],
        "href": "".join(["mailto:", user_obj["email"]]),
        "institution": "Scout software user, Science For Life Laboratory, Stockholm, Sweden",
    }
    if add_features:  # create features dictionaries
        features = hpo_terms(case_obj)

    if add_disorders:  # create OMIM disorders dictionaries
        disorders = omim_terms(case_obj)

    # send a POST request and collect response for each affected individual in case
    server_responses = []

    submitted_info = {
        "contact": contact_info,
        "sex": add_gender,
        "features": features,
        "disorders": disorders,
        "genes_only": genes_only,
        "patient_id": [],
    }
    for individual in case_obj.get("individuals"):
        if not individual["phenotype"] in [
            2,
            "affected",
        ]:  # include only affected individuals
            continue

        patient = {
            "contact": contact_info,
            "id": ".".join(
                [case_obj["_id"], individual.get("individual_id")]
            ),  # This is a required field form MME
            "label": ".".join([case_obj["display_name"], individual.get("display_name")]),
            "features": features,
            "disorders": disorders,
        }
        if add_gender:
            if individual["sex"] == "1":
                patient["sex"] = "MALE"
            else:
                patient["sex"] = "FEMALE"

        if case_obj.get("suspects"):
            g_features = genomic_features(
                store, case_obj, individual.get("display_name"), genes_only
            )
            patient["genomicFeatures"] = g_features

        # send add request to server and capture response
        resp = matchmaker_request(
            url=url,
            token=mme_token,
            method="POST",
            content_type=mme_accepts,
            accept="application/json",
            data={"patient": patient},
        )

        server_responses.append(
            {
                "patient": patient,
                "message": resp.get("message"),
                "status_code": resp.get("status_code"),
            }
        )
    submitted_info["server_responses"] = server_responses
    return submitted_info


def mme_delete(case_obj, mme_base_url, mme_token):
    """Delete all affected samples for a case from MatchMaker

    Args:
        case_obj(dict) a scout case object
        mme_base_url(str) base url of the MME server
        mme_token(str) auth token of the MME server

    Returns:
         server_responses(list): a list of object of this type:
                    {
                        'patient_id': patient_id
                        'message': server_message,
                        'status_code': server_status_code
                    }
    """
    server_responses = []

    if not mme_base_url or not mme_token:
        return "Please check that Matchmaker connection parameters are valid"

    # for each patient of the case in matchmaker
    for patient in case_obj["mme_submission"]["patients"]:

        # send delete request to server and capture server's response
        patient_id = patient["id"]
        url = "".join([mme_base_url, "/patient/delete/", patient_id])
        resp = matchmaker_request(url=url, token=mme_token, method="DELETE")

        server_responses.append(
            {
                "patient_id": patient_id,
                "message": resp.get("message"),
                "status_code": resp.get("status_code"),
            }
        )

    return server_responses


def mme_matches(case_obj, institute_obj, mme_base_url, mme_token):
    """Show Matchmaker submission data for a sample and eventual matches.

    Args:
        case_obj(dict): a scout case object
        institute_obj(dict): an institute object
        mme_base_url(str) base url of the MME server
        mme_token(str) auth token of the MME server

    Returns:
        data(dict): data to display in the html template
    """
    data = {"institute": institute_obj, "case": case_obj, "server_errors": []}
    matches = {}
    # loop over the submitted samples and get matches from the MatchMaker server
    if not case_obj.get("mme_submission"):
        return None

    for patient in case_obj["mme_submission"]["patients"]:
        patient_id = patient["id"]
        matches[patient_id] = None
        url = "".join([mme_base_url, "/matches/", patient_id])
        server_resp = matchmaker_request(url=url, token=mme_token, method="GET")
        if "status_code" in server_resp:  # the server returned a valid response
            # and this will be a list of match objects sorted by desc date
            pat_matches = []
            if server_resp.get("matches"):
                pat_matches = parse_matches(patient_id, server_resp["matches"])
            matches[patient_id] = pat_matches
        else:
            LOG.warning("Server returned error message: {}".format(server_resp["message"]))
            data["server_errors"].append(server_resp["message"])

    data["matches"] = matches

    return data


def mme_match(case_obj, match_type, mme_base_url, mme_token, nodes=None, mme_accepts=None):
    """Initiate a MatchMaker match against either other Scout patients or external nodes

    Args:
        case_obj(dict): a scout case object already submitted to MME
        match_type(str): 'internal' or 'external'
        mme_base_url(str): base url of the MME server
        mme_token(str): auth token of the MME server
        mme_accepts(str): request content accepted by MME server (only for internal matches)

    Returns:
        matches(list): a list of eventual matches
    """
    query_patients = []
    server_responses = []
    url = None
    # list of patient dictionaries is required for internal matching
    query_patients = case_obj["mme_submission"]["patients"]
    if match_type == "internal":
        url = "".join([mme_base_url, "/match"])
        for patient in query_patients:
            json_resp = matchmaker_request(
                url=url,
                token=mme_token,
                method="POST",
                content_type=mme_accepts,
                accept=mme_accepts,
                data={"patient": patient},
            )
            resp_obj = {
                "server": "Local MatchMaker node",
                "patient_id": patient["id"],
                "results": json_resp.get("results"),
                "status_code": json_resp.get("status_code"),
                "message": json_resp.get("message"),  # None if request was successful
            }
            server_responses.append(resp_obj)
    else:  # external matching
        # external matching requires only patient ID
        query_patients = [patient["id"] for patient in query_patients]
        node_ids = [node["id"] for node in nodes]
        if match_type in node_ids:  # match is against a specific external node
            node_ids = [match_type]

        # Match every affected patient
        for patient in query_patients:
            # Against every node
            for node in node_ids:
                url = "".join([mme_base_url, "/match/external/", patient, "?node=", node])
                json_resp = matchmaker_request(url=url, token=mme_token, method="POST")
                resp_obj = {
                    "server": node,
                    "patient_id": patient,
                    "results": json_resp.get("results"),
                    "status_code": json_resp.get("status_code"),
                    "message": json_resp.get("message"),  # None if request was successful
                }
                server_responses.append(resp_obj)
    return server_responses
