# -*- coding: utf-8 -*-
import datetime
import itertools
import json
import logging
import os
from base64 import b64encode

import query_phenomizer
import requests
from bs4 import BeautifulSoup
from bson.objectid import ObjectId
from flask import current_app, flash, redirect, request, url_for
from flask_login import current_user
from flask_mail import Message
from requests.auth import HTTPBasicAuth
from xlsxwriter import Workbook

from scout.constants import (
    CANCER_PHENOTYPE_MAP,
    CASE_REPORT_CASE_FEATURES,
    CASE_REPORT_CASE_IND_FEATURES,
    CASE_REPORT_VARIANT_TYPES,
    MT_COV_STATS_HEADER,
    MT_EXPORT_HEADER,
    PHENOTYPE_GROUPS,
    PHENOTYPE_MAP,
    SEX_MAP,
    VARIANT_REPORT_VARIANT_FEATURES,
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
from scout.parse.matchmaker import genomic_features, hpo_terms, omim_terms, parse_matches
from scout.server.blueprints.variant.controllers import variant as variant_decorator
from scout.server.blueprints.variants.controllers import get_manual_assessments
from scout.server.extensions import RerunnerError, matchmaker, rerunner, store
from scout.server.utils import institute_and_case
from scout.utils.scout_requests import delete_request_json, post_request_json

LOG = logging.getLogger(__name__)

STATUS_MAP = {"solved": "bg-success", "archived": "bg-warning"}
JSON_HEADERS = {"Content-type": "application/json; charset=utf-8", "Accept": "text/json"}


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

    # Fetch ids for grouped cases
    case_groups = {}
    case_group_label = {}
    if case_obj.get("group"):
        for group in case_obj.get("group"):
            case_groups[group] = list(store.cases(group=group))
            case_group_label[group] = store.case_group_label(group)

    # Fetch the variant objects for suspects and causatives
    suspects = [
        store.variant(variant_id) or variant_id for variant_id in case_obj.get("suspects", [])
    ]
    _populate_assessments(suspects)
    causatives = [
        store.variant(variant_id) or variant_id for variant_id in case_obj.get("causatives", [])
    ]
    _populate_assessments(causatives)

    # get evaluated variants
    evaluated_variants = store.evaluated_variants(case_obj["_id"])
    _populate_assessments(evaluated_variants)

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
    _populate_assessments(partial_causatives)

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

    if case_obj.get("rank_model_version"):
        rank_model_link = "".join(
            [
                current_app.config.get("RANK_MODEL_LINK_PREFIX", ""),
                str(case_obj["rank_model_version"]),
                current_app.config.get("RANK_MODEL_LINK_POSTFIX", ""),
            ]
        )
        case_obj["rank_model_link"] = rank_model_link

    if case_obj.get("sv_rank_model_version"):
        case_obj["sv_rank_model_link"] = "".join(
            [
                current_app.config.get("SV_RANK_MODEL_LINK_PREFIX", ""),
                str(case_obj["sv_rank_model_version"]),
                current_app.config.get("SV_RANK_MODEL_LINK_POSTFIX", ""),
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
        event["verb"] = VERBS_MAP.get(event["verb"], "did {} for".format(event["verb"]))

    case_obj["clinvar_variants"] = store.case_to_clinVars(case_obj["_id"])

    # if updated_at is a list, set it to the last update datetime
    if case_obj.get("updated_at") and isinstance(case_obj["updated_at"], list):
        case_obj["updated_at"] = max(case_obj["updated_at"])

    # Phenotype groups can be specific for an institute, there are some default groups
    pheno_groups = institute_obj.get("phenotype_groups") or PHENOTYPE_GROUPS

    # complete OMIM diagnoses specific for this case
    omim_terms = {term["disease_nr"]: term for term in store.case_omim_diagnoses(case_obj)}

    if case_obj.get("custom_images"):
        # re-encode images as base64
        for img_section in case_obj["custom_images"].values():
            for img in img_section:
                img["data"] = b64encode(img["data"]).decode("utf-8")

    data = {
        "status_class": STATUS_MAP.get(case_obj["status"]),
        "other_causatives": [var for var in store.check_causatives(case_obj=case_obj)],
        "managed_variants": [var for var in store.check_managed(case_obj=case_obj)],
        "comments": store.events(institute_obj, case=case_obj, comments=True),
        "hpo_groups": pheno_groups,
        "case_groups": case_groups,
        "case_group_label": case_group_label,
        "events": events,
        "suspects": suspects,
        "causatives": causatives,
        "evaluated_variants": evaluated_variants,
        "partial_causatives": partial_causatives,
        "collaborators": collab_ids,
        "cohort_tags": institute_obj.get("cohorts", []),
        "omim_terms": omim_terms,
        "manual_rank_options": MANUAL_RANK_OPTIONS,
        "cancer_tier_options": CANCER_TIER_OPTIONS,
    }

    return data


def _populate_assessments(variants_list):
    """
    Add ACMG classification, manual_rank, cancer_tier, dismiss_variant and mosaic_tags assessment options to a variant object.
    The list of variant objects can contain plain variant_id strings for deleted / no longer loaded variants.
    These should not be populated.

    Args:
        variants_list: list(variant_obj or str)

    Returns:

    """
    for variant in variants_list:
        if isinstance(variant, str):
            continue
        variant["clinical_assessments"] = get_manual_assessments(variant)


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


def case_report_variants(store, case_obj, institute_obj, data):
    """Gather evaluated variants info to include in case report

    Args:
        store(adapter.MongoAdapter)
        case_obj(dict): case dictionary
        data(dict): data dictionary containing case report information
    """
    evaluated_variants = {vt: [] for vt in CASE_REPORT_VARIANT_TYPES}
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
        for vt in CASE_REPORT_VARIANT_TYPES:
            keyword = CASE_REPORT_VARIANT_TYPES[vt]
            # When found we add it to the categpry
            # Eac variant can belong to multiple categories
            if keyword not in var_obj:
                continue
            evaluated_variants[vt].append(var_obj)

    data["variants"] = {}

    for var_type in evaluated_variants:
        decorated_variants = []
        for var_obj in evaluated_variants[var_type]:
            # We decorate the variant with some extra information
            filtered_var_obj = {}
            for feat in VARIANT_REPORT_VARIANT_FEATURES:
                filtered_var_obj[feat] = var_obj.get(feat)

            decorated_info = variant_decorator(
                store=store,
                institute_id=institute_obj["_id"],
                case_name=case_obj["display_name"],
                variant_id=None,
                variant_obj=filtered_var_obj,
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
        data["variants"][var_type] = decorated_variants


def case_report_content(store, institute_id, case_name):
    """Gather contents to be visualized in a case report

    Args:
        store(adapter.MongoAdapter)
        institute_id(str): _id of an institute
        case_name(str): case display name

    Returns:
        data(dict)

    """
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = {}
    # Populate data with required institute _id
    data["institute"] = {
        "_id": institute_obj["_id"],
    }
    # Populate case individuals with required information
    case_individuals = []
    for ind in case_obj.get("individuals"):
        ind_feat = {}
        for feat in CASE_REPORT_CASE_IND_FEATURES:
            ind_feat[feat] = ind.get(feat)
            pheno_map = PHENOTYPE_MAP
            if case_obj.get("track", "rare") == "cancer":
                pheno_map = CANCER_PHENOTYPE_MAP
            ind_feat["phenotype_human"] = pheno_map.get(ind["phenotype"])
        case_individuals.append(ind_feat)

    case_info = {"individuals": case_individuals}
    for feat in CASE_REPORT_CASE_FEATURES:
        case_info[feat] = case_obj.get(feat)

    data["case"] = case_info

    dismiss_options = DISMISS_VARIANT_OPTIONS
    data["cancer"] = case_obj.get("track") == "cancer"
    if data["cancer"]:
        dismiss_options = {
            **DISMISS_VARIANT_OPTIONS,
            **CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
        }

    data["comments"] = store.events(institute_obj, case=case_obj, comments=True)
    data["audits"] = store.case_events_by_verb(
        category="case", institute=institute_obj, case=case_obj, verb="filter_audit"
    )

    data["manual_rank_options"] = MANUAL_RANK_OPTIONS
    data["cancer_tier_options"] = CANCER_TIER_OPTIONS
    data["dismissed_options"] = dismiss_options
    data["genetic_models"] = dict(GENETIC_MODELS)
    data["report_created_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    case_report_variants(store, case_obj, institute_obj, data)

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


def mt_coverage_stats(individuals, ref_chrom="14"):
    """Send a request to chanjo report endpoint to retrieve MT vs autosome coverage stats

    Args:
        individuals(dict): case_obj["individuals"] object
        ref_chrom(str): reference chromosome (1-22)

    Returns:
        coverage_stats(dict): a dictionary with mean MT and autosome transcript coverage stats
    """
    coverage_stats = {}
    ind_ids = []
    for ind in individuals:
        ind_ids.append(ind["individual_id"])

    # Prepare complete url to Chanjo report chromosome mean coverage calculation endpoint
    cov_calc_url = url_for("report.json_chrom_coverage", _external=True)
    # Prepare request data to calculate mean MT coverage
    data = dict(sample_ids=",".join(ind_ids), chrom="MT")
    # Send POST request with data to chanjo endpoint
    resp = requests.post(cov_calc_url, json=data)
    mt_cov_data = json.loads(resp.text)

    # Change request data to calculate mean autosomal coverage
    data["chrom"] = str(ref_chrom)  # convert to string if an int is provided
    # Send POST request with data to chanjo endpoint
    resp = requests.post(cov_calc_url, json=data)
    ref_cov_data = json.loads(resp.text)  # mean coverage over the transcripts of ref chrom

    for ind in ind_ids:
        if not (mt_cov_data.get(ind) and ref_cov_data.get(ind)):
            continue
        coverage_info = dict(
            mt_coverage=round(mt_cov_data[ind], 2),
            autosome_cov=round(ref_cov_data[ind], 2),
            mt_copy_number=round((mt_cov_data[ind] / ref_cov_data[ind]) * 2, 2),
        )
        coverage_stats[ind] = coverage_info

    return coverage_stats


def mt_excel_files(store, case_obj, temp_excel_dir):
    """Collect MT variants and format line of a MT variant report
    to be exported in excel format. Create mt excel files, one for each sample,
    in a temporary directory.

    Args:
        store(adapter.MongoAdapter)
        case_obj(models.Case)
        temp_excel_dir(os.Path): folder where the temp excel files are written to

    Returns:
        written_files(int): the number of files written to temp_excel_dir

    """
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    samples = case_obj.get("individuals")
    file_header = MT_EXPORT_HEADER
    coverage_stats = None
    # if chanjo connection is established, include MT vs AUTOSOME coverage stats
    if current_app.config.get("SQLALCHEMY_DATABASE_URI"):
        coverage_stats = mt_coverage_stats(samples)

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

        if bool(
            coverage_stats
        ):  # it's None if app is not connected to Chanjo or {} if samples are not in Chanjo db
            # Write coverage stats header after introducing 2 empty lines
            for col, field in enumerate(MT_COV_STATS_HEADER):
                Report_Sheet.write(row + 3, col, field)

            # Write sample MT vs autosome coverage stats to excel sheet
            for col, item in enumerate(["mt_coverage", "autosome_cov", "mt_copy_number"]):
                Report_Sheet.write(row + 4, col, coverage_stats[sample_id].get(item))

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


def _update_case(store, case_obj, user_obj, institute_obj, verb):
    """Update case with new sample data, and create an associated event"""
    store.update_case(case_obj, keep_date=True)

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
        verb=verb,
        subject=case_obj["display_name"],
    )


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

    verb = "update_individual"
    _update_case(store, case_obj, user_obj, institute_obj, verb)


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

    verb = "update_sample"
    _update_case(store, case_obj, user_obj, institute_obj, verb)


def phenotypes_genes(store, case_obj, is_clinical=True):
    """Generate a dictionary consisting of phenotype terms with associated genes from the case HPO panel

    Args:
        store(adapter.MongoAdapter)
        case_obj(dict): models.Case
        is_clinical(bool): if True, only list genes from HPO that are among the case clinical_symbols

    Returns:
        hpo_genes(dict): a dictionary with HPO term IDs as keys and HPO terms and genes as values
                      If the dynamic phenotype panel is empty, or has been intersected to some level,
                      use dynamic gene list directly instead.
    """
    build = case_obj["genome_build"]
    # Make sure build is either "37" or "38"
    if "38" in str(build):
        build = "38"
    else:
        build = "37"
    dynamic_gene_list = [gene["hgnc_id"] for gene in case_obj.get("dynamic_gene_list", [])]

    hpo_genes = {}

    clinical_symbols = store.clinical_symbols(case_obj) if is_clinical else None
    unique_genes = hpo_genes_from_dynamic_gene_list(case_obj, is_clinical, clinical_symbols)

    by_phenotype = True  # display genes by phenotype
    hpo_gene_list = case_obj.get("dynamic_panel_phenotypes", [])
    if not hpo_gene_list and dynamic_gene_list:
        by_phenotype = False

    all_hpo_gene_list_genes = set()
    # Loop over the dynamic phenotypes of a case
    for hpo_id in hpo_gene_list:
        hpo_term = store.hpo_term(hpo_id)
        # Check that HPO term exists in database
        if hpo_term is None:
            LOG.warning(f"Could not find HPO term with ID '{hpo_id}' in database")
            continue
        # Create a list with all gene symbols (or HGNC ID if symbol is missing) associated with the phenotype
        gene_list = []
        for gene_id in hpo_term.get("genes", []):
            gene_obj = store.hgnc_gene(gene_id, build)
            if gene_obj is None:
                continue
            if gene_id not in dynamic_gene_list:
                # gene was filtered out because min matching phenotypes > 1 (or the panel was generated with older genotype-phenotype mapping)
                by_phenotype = False  # do not display genes by phenotype
                continue
            add_symbol = gene_obj.get("hgnc_symbol", f"hgnc:{gene_id}")
            if is_clinical and (add_symbol not in clinical_symbols):
                continue
            gene_list.append(add_symbol)
            all_hpo_gene_list_genes.add(add_symbol)

        hpo_genes[hpo_id] = {
            "description": hpo_term.get("description"),
            "genes": ", ".join(sorted(gene_list)),
        }

    if by_phenotype is True:
        # if some gene was manually added (or is left on dynamic panel for other reasons)
        non_hpo_genes = unique_genes - all_hpo_gene_list_genes
        if len(non_hpo_genes) > 0:
            hpo_genes["Analysed genes"] = {
                "description": "Non HPO panel genes",
                "genes": ", ".join(sorted(non_hpo_genes)),
            }

    if by_phenotype is False:
        hpo_genes = {}
        hpo_genes["Analysed genes"] = {
            "description": "HPO panel",
            "genes": ", ".join(sorted(unique_genes)),
        }

    return hpo_genes


def hpo_genes_from_dynamic_gene_list(case_obj, is_clinical, clinical_symbols):
    """
    Case where dynamic_panel_phenotypes is empty, perhaps because user has added custom genes to HPO panel

    Args:
        case_obj(dict): models.Case)
        is_clinical(bool): if True, only list genes from HPO that are among the case clinical_symbols
        clinical_symbols(set): set of clinical symbols
    Returns:
        hpo_genes(set):
    """

    gene_list = [
        gene.get("hgnc_symbol") or str(gene["hgnc_id"]) for gene in case_obj["dynamic_gene_list"]
    ]

    unique_genes = set(gene_list)
    if is_clinical:
        unique_genes = unique_genes.intersection(set(clinical_symbols))

    return unique_genes


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


def call_rerunner(store, institute_id, case_name, metadata):
    """Call rerunner with updated pedigree metadata."""
    # define the data to be passed
    payload = {"case_id": case_name, "sample_ids": [m["sample_id"] for m in metadata]}

    cnf = rerunner.connection_settings
    url = cnf.get("entrypoint")
    if not url:
        raise ValueError("Rerunner API entrypoint not configured")
    auth = HTTPBasicAuth(current_user.email, cnf.get("api_key"))
    LOG.info(f"Sending request -- {url}; params={payload}")
    resp = requests.post(
        url,
        params=payload,
        json=metadata,
        timeout=rerunner.timeout,
        headers={"Content-Type": "application/json"},
        auth=auth,
    )

    if resp.status_code == 200:
        LOG.info(f"Reanalysis was successfully started; case: {case_name}")
        # get institute, case and user objects for adding a notification of the rerun to the database
        institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
        user_obj = store.user(current_user.email)
        link = url_for("cases.case", institute_id=institute_id, case_name=case_name)
        store.request_rerun(institute_obj, case_obj, user_obj, link)
        # notfiy the user of the rerun
        flash(f"Reanalysis was successfully started; case: {case_name}", "info")

    else:
        raise RerunnerError(f"{resp.reason}, {resp.status_code}")


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


def add_case_group(store, current_user, institute_id, case_name, group=None):
    """Bind a case group in a selected a case, creating it in current institute if not given.

    Args:
        current_user    (user)current user
        institute_id    (str)institute id
        case_name       (str)case display name
        group           (str)case group id - converts to ObjectId
    Returns:
        updated_case    (InsertOneResult)
    """

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    link = url_for("cases.case", institute_id=institute_id, case_name=case_name)
    user_obj = store.user(current_user.email)

    if not group:
        group = store.init_case_group(institute_id)

    current_group_ids = set(case_obj.get("group", []))
    current_group_ids.add(ObjectId(group))

    updated_case = store.update_case_group_ids(
        institute_obj, case_obj, user_obj, link, list(current_group_ids)
    )
    return updated_case


def remove_case_group(store, current_user, institute_id, case_name, case_group):
    """Remove a case group from selected institute - and from db if it is no longer in use."""

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    link = url_for("cases.case", institute_id=institute_id, case_name=case_name)
    user_obj = store.user(current_user.email)

    current_group_ids = case_obj.get("group", [])

    # STR OBJID mismatch?
    current_group_ids.remove(ObjectId(case_group))
    updated_case = store.update_case_group_ids(
        institute_obj, case_obj, user_obj, link, current_group_ids
    )

    current_group_cases = store.case_ids_from_group_id(case_group)

    if current_group_cases == []:
        store.remove_case_group(case_group)

    return updated_case


def case_group_update_label(store, case_group_id, case_group_label):
    """Update a case group label."""

    result = store.case_group_update_label(ObjectId(case_group_id), case_group_label)

    return result


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


def prepare_beacon_req_params():
    """Prepares URL and Headers for sending a request to the beacon server.

    Returns:
        url, headers(tuple)
    """
    req_url = current_app.config.get("BEACON_URL")
    beacon_token = current_app.config.get("BEACON_TOKEN")
    if not req_url or not beacon_token:
        return
    req_headers = JSON_HEADERS
    req_headers["X-Auth-Token"] = beacon_token
    return req_url, req_headers


def beacon_remove(case_id):
    """Remove all variants from a case in Beacon by handling a POST request to the /apiv1.0/delete Beacon endpoint.

    Args:
        case_id(str): A case _id

    """
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
    """Save variants from one or more case samples to the Beacon server.
       Handle a POST request to the /apiv1.0/add Beacon endpoint

    Args:
        form(werkzeug.datastructures.ImmutableMultiDict): beacon submission form

    """
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


def matchmaker_check_requirements(request):
    """Make sure requirements are fulfilled before submitting any request to MatchMaker Exchange

    Args:
        request(werkzeug.local.LocalProxy)
    Returns:
        None, if requirements are fulfilled, otherwise redirects to previous page with error message
    """
    # Make sure all MME connection parameters are available in scout instance
    if (
        any(
            [
                hasattr(matchmaker, "host"),
                hasattr(matchmaker, "accept"),
                hasattr(matchmaker, "token"),
            ]
        )
        is None
    ):
        flash(
            "An error occurred reading matchmaker connection parameters. Please check config file!",
            "danger",
        )
        return redirect(request.referrer)

    # Check that request comes from an authorized user (mme_submitter role)
    user_obj = store.user(current_user.email)
    if "mme_submitter" not in user_obj.get("roles", []):
        flash("unauthorized request", "warning")
        return redirect(request.referrer)


def matchmaker_add(request, institute_id, case_name):
    """Add all affected individuals from a case to a MatchMaker server

    Args:
        request(werkzeug.local.LocalProxy)
        institute_id(str): _id of an institute
        case_name(str): display name of a case
    """
    # Check that general MME request requirements are fulfilled
    matchmaker_check_requirements(request)
    _, case_obj = institute_and_case(store, institute_id, case_name)
    candidate_vars = case_obj.get("suspects") or []
    if len(candidate_vars) > 3:
        flash(
            "At the moment it is not possible to save to MatchMaker more than 3 pinned variants",
            "warning",
        )
        return redirect(request.referrer)

    save_gender = "sex" in request.form
    features = (
        hpo_terms(case_obj)
        if "features" in request.form and case_obj.get("phenotype_terms")
        else []
    )
    disorders = omim_terms(case_obj) if "disorders" in request.form else []
    genes_only = request.form.get("genomicfeatures") == "genes"

    if not features and not candidate_vars:
        flash(
            "In order to upload a case to MatchMaker you need to pin a variant or at least assign a phenotype (HPO term)",
            "danger",
        )
        return redirect(request.referrer)

    # create contact dictionary
    user_obj = store.user(current_user.email)
    contact_info = {
        "name": user_obj["name"],
        "href": "".join(["mailto:", user_obj["email"]]),
        "institution": "Scout software user, Science For Life Laboratory, Stockholm, Sweden",
    }

    submitted_info = {
        "contact": contact_info,
        "sex": save_gender,
        "features": features,
        "disorders": disorders,
        "genes_only": genes_only,
        "patient_id": [],
        "server_responses": [],
    }
    server_responses = []
    n_updated = 0
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
        if save_gender:
            if individual["sex"] == "1":
                patient["sex"] = "MALE"
            else:
                patient["sex"] = "FEMALE"

        if candidate_vars:
            g_features = genomic_features(
                store, case_obj, individual.get("display_name"), genes_only
            )
            patient["genomicFeatures"] = g_features
        resp = matchmaker.patient_submit(patient)
        submitted_info["server_responses"].append(
            {
                "patient": patient,
                "message": resp.get("message"),
                "status_code": resp.get("status_code"),
            }
        )
        if resp.get("status_code") != 200:
            flash(
                "an error occurred while adding patient to matchmaker: {}".format(
                    resp.get("message")
                ),
                "warning",
            )
            continue
        flash(f"Patient {individual.get('display_name')} saved to MatchMaker", "success")
        n_updated += 1

    if n_updated > 0:
        store.case_mme_update(case_obj=case_obj, user_obj=user_obj, mme_subm_obj=submitted_info)

    return n_updated


def matchmaker_delete(request, institute_id, case_name):
    """Delete all affected samples for a case from MatchMaker

    Args:
        request(werkzeug.local.LocalProxy)
        institute_id(str): _id of an institute
        case_name(str): display name of a case
    """
    # Check that general MME request requirements are fulfilled
    matchmaker_check_requirements(request)

    _, case_obj = institute_and_case(store, institute_id, case_name)
    # Delete each patient submitted for this case
    for patient in case_obj.get("mme_submission", {}).get("patients", []):
        # Send delete request to server and capture server's response
        patient_id = patient["id"]
        resp = matchmaker.patient_delete(patient_id)
        category = "warning"
        if resp["status_code"] == 200:
            category = "success"
            # update case by removing mme submission
            # and create events for patients deletion from MME
            user_obj = store.user(current_user.email)
            store.case_mme_delete(case_obj=case_obj, user_obj=user_obj)

            flash(f"Deleted patient '{patient_id}', case '{case_name}' from MatchMaker", "success")
            continue

        flash(f"An error occurred while deleting patient from MatchMaker", "danger")


def matchmaker_matches(request, institute_id, case_name):
    """Show Matchmaker submission data for a sample and eventual matches.

    Args:
        request(werkzeug.local.LocalProxy)
        institute_id(str): _id of an institute
        case_name(str): display name of a case

    Returns:
        data(dict): data to display in the html template
    """
    # Check that general MME request requirements are fulfilled
    matchmaker_check_requirements(request)

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = {"institute": institute_obj, "case": case_obj, "server_errors": [], "panel": 1}
    matches = {}
    for patient in case_obj.get("mme_submission", {}).get("patients", []):
        patient_id = patient["id"]
        matches[patient_id] = None
        server_resp = matchmaker.patient_matches(patient_id)
        if server_resp.get("status_code") != 200:  # server returned error
            flash("MatchMaker server returned error:{}".format(data["server_errors"]), "danger")
            return redirect(request.referrer)
        # server returned a valid response
        pat_matches = []
        if server_resp.get("content", {}).get("matches"):
            pat_matches = parse_matches(patient_id, server_resp["content"]["matches"])
        matches[patient_id] = pat_matches

    data["matches"] = matches
    return data


def matchmaker_match(request, target, institute_id, case_name):
    """Initiate a MatchMaker match against either other Scout patients or external nodes

    Args:
        request(werkzeug.local.LocalProxy)
        target(str): 'internal' for matches against internal patients, or id of a specific node
        institute_id(str): _id of an institute
        case_name(str): display name of a case
    """
    # Check that general MME request requirements are fulfilled
    matchmaker_check_requirements(request)

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    query_patients = case_obj.get("mme_submission", {}).get("patients", [])
    ok_responses = 0
    for patient in query_patients:
        json_resp = None
        if target == "internal":  # Interal match against other patients on the MME server
            json_resp = matchmaker.match_internal(patient)
            if json_resp.get("status_code") != 200:
                flash(
                    f"An error occurred while matching patient against other patients of MatchMaker:{json_resp.get('message')}",
                    "danger",
                )
                continue
            ok_responses += 1
        else:  # external matches
            # Match every affected patient
            patient_id = patient["id"]
            # Against every node
            nodes = [node["id"] for node in matchmaker.connected_nodes]
            for node in nodes:
                if node != target:
                    continue
                json_resp = matchmaker.match_external(patient_id, node)
                if json_resp.get("status_code") != 200:
                    flash(
                        f"An error occurred while matching patient against external node: '{node}' : {json_resp.get('message')}",
                        "danger",
                    )
                    continue
                ok_responses += 1
    if ok_responses > 0:
        flash(
            "Matching request sent. Click on 'Past Matches' to review eventual matching results.'",
            "info",
        )

    return ok_responses
