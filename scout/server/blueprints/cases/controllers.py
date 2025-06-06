# -*- coding: utf-8 -*-
import datetime
import itertools
import logging
import os
from typing import Dict, List, Set

import query_phenomizer
import requests
from bson.objectid import ObjectId
from flask import current_app, flash, redirect, url_for
from flask_login import current_user
from requests.auth import HTTPBasicAuth
from xlsxwriter import Workbook

from scout import __version__
from scout.adapter import MongoAdapter
from scout.constants import (
    CANCER_PHENOTYPE_MAP,
    CASE_REPORT_VARIANT_TYPES,
    CASE_TAGS,
    CUSTOM_CASE_REPORTS,
    DATE_DAY_FORMATTER,
    GENOME_REGION,
    HPO_LINK_URL,
    INHERITANCE_PALETTE,
    MITODEL_HEADER,
    MT_COV_STATS_HEADER,
    MT_EXPORT_HEADER,
    PHENOTYPE_GROUPS,
    PHENOTYPE_MAP,
    SAMPLE_SOURCE,
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
from scout.server.blueprints.variants.controllers import get_manual_assessments
from scout.server.extensions import (
    RerunnerError,
    bionano_access,
    chanjo2,
    chanjo_report,
    gens,
    matchmaker,
    rerunner,
    store,
)
from scout.server.links import disease_link
from scout.server.utils import (
    case_has_alignments,
    case_has_chanjo2_coverage,
    case_has_chanjo_coverage,
    case_has_mt_alignments,
    case_has_mtdna_report,
    case_has_rna_tracks,
    get_case_genome_build,
    get_case_mito_chromosome,
    institute_and_case,
)
from scout.utils.acmg import get_acmg_temperature
from scout.utils.ccv import get_ccv_temperature

LOG = logging.getLogger(__name__)

STATUS_MAP = {"solved": "bg-success", "archived": "bg-warning"}
JSON_HEADERS = {
    "Content-type": "application/json; charset=utf-8",
    "Accept": "text/json",
}

COVERAGE_REPORT_TIMEOUT = 20

PANEL_PROJECTION = {"version": 1, "display_name": 1, "genes": 1}
PANEL_HIDDEN_PROJECTION = {"version": 1, "display_name": 1, "hidden": 1}


def phenomizer_diseases(hpo_ids, case_obj, p_value_treshold=1):
    """Return the list of HGNC symbols that match annotated HPO terms on Phenomizer
    Args:
        hpo_ids(list)
        case_obj(models.Case)

    Returns:
        diseases(list of dictionaries) or None. Results contains the following key/values: p_value, gene_symbols, disease_nr, disease_source, OMIM, description, raw_line
    """
    if len(hpo_ids) == 0:
        hpo_ids = [term["phenotype_id"] for term in case_obj.get("phenotype_terms", [])]

    username = current_app.config["PHENOMIZER_USERNAME"]
    password = current_app.config["PHENOMIZER_PASSWORD"]
    try:
        results = query_phenomizer.query(username, password, *hpo_ids)
        diseases = [result for result in results if result["p_value"] <= p_value_treshold]
        return diseases
    except RuntimeError:
        flash("Could not establish a conection to Phenomizer", "danger")


def coverage_report_contents(base_url, institute_obj, case_obj):
    """Capture the contents of a case coverage report (chanjo-report), to be displayed in the general case report

    Args:
        base_url(str): base url of this application
        institute_obj(models.Institute)
        case_obj(models.Case)

    Returns:
        html_body_content(str): A string corresponding to the text within the <body> of an HTML chanjo-report page
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

    # Collect the coverage report HTML string
    try:
        resp = requests.post(
            base_url + "reports/report",
            timeout=COVERAGE_REPORT_TIMEOUT,
            data=request_data,
        )
    except requests.Timeout:
        html_body_content = "<span><b>Coverage report unavailable</b></span>"
        return html_body_content

    # Extract the contents between <body> and </body>
    html_body_content = resp.text.split("<body>")[1].split("</body>")[0]
    return html_body_content


def _populate_case_groups(
    store: MongoAdapter,
    case_obj: dict,
    case_groups: Dict[str, List[str]],
    case_group_label: Dict[str, str],
):
    """Case groups allow display of information about user linked cases together on one case.
    Notably variantS lists show shared annotations and alignment views show all alignments
    available for the group.

    Each case may belong to any of a list of groups. Groups have human readable labels
    that need to be fetched separately. Alignments for each case, that belongs to
    a group that the present case also belongs to, are added to the present case.

    Args:
         store(adapter.MongoAdapter)
         case_obj(models.Case)
         case_group(dict) - keys group ids, values list(case_ids)
         case_group_label(dict) - keys group ids, values case_group_labels(str)
    """
    if case_obj.get("group"):
        for group in case_obj.get("group"):
            case_groups[group] = list(store.cases(group=group))
            case_group_label[group] = store.case_group_label(group)


def _get_partial_causatives(store: MongoAdapter, institute_obj: dict, case_obj: dict) -> List[Dict]:
    """Check for partial causatives and associated phenotypes.
    Return any partial causatives a case has, populated as causative objs.
    """

    partial_causatives = []
    if case_obj.get("partial_causatives"):
        for var_id, values in case_obj["partial_causatives"].items():
            variant_obj = store.variant(var_id)
            if variant_obj:
                decorated_variant_obj = _get_decorated_var(
                    store, var_obj=variant_obj, institute_obj=institute_obj, case_obj=case_obj
                )
            causative_obj = {
                "variant": decorated_variant_obj or var_id,
                "disease_terms": values.get("diagnosis_phenotypes"),
                "hpo_terms": values.get("phenotype_terms"),
            }
            partial_causatives.append(causative_obj)
    return partial_causatives


def _set_rank_model_links(case_obj: Dict):
    """Add Rank Model links to case if rank model versions are set.

    Appropriate configuration file prefix and postfix are concatenated to the version string.
    """

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


def _populate_case_individuals(case_obj: Dict):
    """Populate case individuals for display

    Prepare the case to be displayed in the case view.

    Args:
        case_obj(models.Case)
    """
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


def _get_events(store, institute_obj, case_obj) -> List:
    """Prepare events for activity display."""
    events = list(store.events(institute_obj, case=case_obj))
    for event in events:
        event["verb"] = VERBS_MAP.get(event["verb"], "did {} for".format(event["verb"]))

    return events


def bionano_case(store, institute_obj, case_obj) -> Dict:
    """Preprocess a case for tabular view, BioNano."""

    _populate_case_individuals(case_obj)

    for individual in case_obj["individuals"]:
        fshd_loci = None
        if individual.get("bionano_access") and not individual.get("fshd_loci"):
            fshd_loci = bionano_access.get_fshd_report(
                individual["bionano_access"].get("project"),
                individual["bionano_access"].get("sample"),
            )
            if not fshd_loci:
                flash(
                    f"Sample FSHD report configured for {individual['bionano_access'].get('project')} - {individual['bionano_access'].get('sample')} but could not be retrieved or processed. Check BioNano Access server ({current_app.config.get('BIONANO_ACCESS')}) manually if the error persists.",
                    "danger",
                )
        individual["fshd_loci"] = fshd_loci

    data = {
        "institute": institute_obj,
        "case": case_obj,
        "bionano_access_url": current_app.config.get("BIONANO_ACCESS"),
        "comments": store.events(institute_obj, case=case_obj, comments=True),
        "events": _get_events(store, institute_obj, case_obj),
    }
    return data


def sma_case(store: MongoAdapter, institute_obj: dict, case_obj: dict) -> dict:
    """Preprocess a case for tabular view, SMA."""

    _populate_case_individuals(case_obj)

    case_has_alignments(case_obj)

    data = {
        "institute": institute_obj,
        "case": case_obj,
        "comments": store.events(institute_obj, case=case_obj, comments=True),
        "events": _get_events(store, institute_obj, case_obj),
        "region": GENOME_REGION[get_case_genome_build(case_obj)],
    }
    return data


def _get_suspects_or_causatives(
    store: MongoAdapter, institute_obj: dict, case_obj: dict, kind: str = "suspects"
) -> list:
    """Fetch the variant objects for suspects and causatives and decorate them.
    If no longer available, append variant_id instead."""

    marked_vars = []
    for variant_id in case_obj.get(kind, []):
        variant_obj = store.variant(variant_id)
        if variant_obj:
            marked_vars.append(
                _get_decorated_var(
                    store, var_obj=variant_obj, institute_obj=institute_obj, case_obj=case_obj
                )
            )
        else:
            marked_vars.append(variant_id)
    return marked_vars


def case(
    store: MongoAdapter, institute_obj: dict, case_obj: dict, hide_matching: bool = True
) -> dict:
    """Preprocess a single case.

    Prepare the case to be displayed in the case view.

    The return data dict includes the cases, how many there are and the limit.
    """
    # Convert individual information to more readable format
    _populate_case_individuals(case_obj)

    case_obj["assignees"] = [
        store.user(user_id=user_id) for user_id in case_obj.get("assignees", [])
    ]

    # Provide basic info on alignment files & coverage data availability for this case
    case_has_alignments(case_obj)
    case_has_mt_alignments(case_obj)
    case_has_chanjo_coverage(case_obj)
    case_has_chanjo2_coverage(case_obj)
    case_has_mtdna_report(case_obj)

    case_groups = {}
    case_group_label = {}
    _populate_case_groups(store, case_obj, case_groups, case_group_label)

    suspects = _get_suspects_or_causatives(store, institute_obj, case_obj, "suspects")
    _populate_assessments(suspects)

    causatives = _get_suspects_or_causatives(store, institute_obj, case_obj, "causatives")
    _populate_assessments(causatives)

    evaluated_variants = store.evaluated_variants(case_obj["_id"], case_obj["owner"])
    _populate_assessments(evaluated_variants)

    partial_causatives = _get_partial_causatives(store, institute_obj, case_obj)
    _populate_assessments(partial_causatives)

    case_obj["clinvar_variants"] = store.case_to_clinvars(case_obj["_id"])

    # check for variants submitted to clinVar but not present in suspects for the case
    clinvar_variants_not_in_suspects = [
        store.variant(variant_id) or variant_id
        for variant_id in case_obj["clinvar_variants"]
        if variant_id not in case_obj.get("suspects", [])
    ]

    case_obj["clinvar_variants_not_in_suspects"] = clinvar_variants_not_in_suspects

    case_obj["default_genes"] = _get_default_panel_genes(store, case_obj)

    _set_panel_removed(store, case_obj)

    for hpo_term in itertools.chain(
        case_obj.get("phenotype_groups") or [], case_obj.get("phenotype_terms") or []
    ):
        hpo_term["hpo_link"] = f"{HPO_LINK_URL}{hpo_term['phenotype_id']}"

    _set_rank_model_links(case_obj)

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

    # if updated_at is a list, set it to the last update datetime
    if case_obj.get("updated_at") and isinstance(case_obj["updated_at"], list):
        case_obj["updated_at"] = max(case_obj["updated_at"])

    # Phenotype groups can be specific for an institute, there are some default groups
    pheno_groups = institute_obj.get("phenotype_groups") or PHENOTYPE_GROUPS

    # If case diagnoses are a list of integers, convert into a list of dictionaries
    disease_terms = {}
    case_diagnoses = case_obj.get("diagnosis_phenotypes", [])
    if case_diagnoses:
        if isinstance(case_diagnoses[0], int):
            case_obj = store.convert_diagnoses_format(case_obj)
        # Fetch complete OMIM diagnoses specific for this case
        disease_terms = {
            term["disease_id"]: term
            for term in store.case_diseases(
                case_disease_list=case_obj.get("diagnosis_phenotypes"), filter_project=None
            )
        }
    add_link_for_disease(case_obj)
    if case_obj.get("custom_images"):
        # re-encode images as base64
        case_obj["custom_images"] = case_obj["custom_images"].get(
            "case_images", case_obj["custom_images"].get("case", {})
        )

    other_causatives = []
    other_causatives_in_default_panels = []
    default_managed_variants = []
    managed_variants = []

    if hide_matching is False:
        # Limit secondary findings according to institute settings
        limit_genes = store.safe_genes_filter(institute_obj["_id"])

        limit_genes_default_panels = _limit_genes_on_default_panels(
            case_obj["default_genes"], limit_genes
        )

        other_causatives, other_causatives_in_default_panels = _matching_causatives(
            store, case_obj, limit_genes, limit_genes_default_panels
        )

        managed_variants = [
            var for var in store.check_managed(case_obj=case_obj, limit_genes=limit_genes)
        ]
        default_managed_variants = [
            var
            for var in store.check_managed(
                case_obj=case_obj, limit_genes=limit_genes_default_panels
            )
        ]

    data = {
        "institute": institute_obj,
        "case": case_obj,
        "other_causatives": other_causatives,
        "default_other_causatives": other_causatives_in_default_panels,
        "managed_variants": managed_variants,
        "default_managed_variants": default_managed_variants,
        "comments": store.events(institute_obj, case=case_obj, comments=True),
        "hpo_groups": pheno_groups,
        "case_groups": case_groups,
        "case_group_label": case_group_label,
        "case_tag_options": CASE_TAGS,
        "events": _get_events(store, institute_obj, case_obj),
        "suspects": suspects,
        "causatives": causatives,
        "evaluated_variants": evaluated_variants,
        "partial_causatives": partial_causatives,
        "has_rna_tracks": case_has_rna_tracks(case_obj),
        "collaborators": collab_ids,
        "cohort_tags": institute_obj.get("cohorts", []),
        "disease_terms": disease_terms,
        "manual_rank_options": MANUAL_RANK_OPTIONS,
        "cancer_tier_options": CANCER_TIER_OPTIONS,
        "tissue_types": SAMPLE_SOURCE,
        "report_types": CUSTOM_CASE_REPORTS,
        "mme_nodes": matchmaker.connected_nodes,
        "gens_info": gens.connection_settings(get_case_genome_build(case_obj)),
        "display_rerunner": rerunner.connection_settings.get("display", False),
        "hide_matching": hide_matching,
        "audits": store.case_events_by_verb(
            category="case", institute=institute_obj, case=case_obj, verb="filter_audit"
        ),
    }

    return data


def _limit_genes_on_default_panels(default_genes: list, limit_genes: list) -> list:
    """Take two lists of genes, the default ones for the case and the limit list for the institute
    and intersect them.

    An empty set is interpreted permissively downstream. Hence we need a special rule if either input list
    is empty, but the other populated.
    If the limit gene list is empty this becomes the default genes set.
    If the default genes list is empty, this becomes the limit_genes set.

    Args:
        default_genes: list(str)
        limit_genes: list(str)
    Returns: list(str)
    """
    default_genes_set = set(default_genes)
    if not limit_genes:
        return default_genes
    if not default_genes:
        return limit_genes

    limit_genes_set = set(limit_genes)

    return list(default_genes_set.intersection(limit_genes_set))


def _set_panel_removed(store: MongoAdapter, case_obj: dict) -> list:
    """Flag panel on list removed if the latest panel version is marked hidden."""

    for panel_info in case_obj.get("panels", []):
        latest_panel = store.gene_panel(
            panel_info["panel_name"], projection=PANEL_HIDDEN_PROJECTION
        )
        panel_info["removed"] = (
            latest_panel.get("hidden", False) if latest_panel is not None else False
        )


def _get_default_panel_genes(store: MongoAdapter, case_obj: dict) -> list:
    """Get unique genes on case default panels.

    Also check if the default panels are up to date, and update case_obj with
    information about any out-dated panels, plus full panel names for coverage.

    Args:
        store(adapter.MongoAdapter)
        case_obj(dict)
    Returns:
        distinct_genes(list(str)): hgnc id for unique genes.
    """

    # Set of all unique genes in the default gene panels
    distinct_genes = set()
    case_obj["panel_names"] = []
    case_obj["outdated_panels"] = {}

    for panel_info in case_obj.get("panels", []):
        if not panel_info.get("display_name"):
            panel_info["display_name"] = panel_info["panel_name"]
        if not panel_info.get("is_default"):
            continue
        panel_name = panel_info["panel_name"]
        panel_version = panel_info.get("version")
        panel_obj = store.gene_panel(
            panel_name,
            version=panel_version,
            projection=PANEL_PROJECTION,
        )
        latest_panel = store.gene_panel(panel_name, projection=PANEL_PROJECTION)
        if not panel_obj:
            panel_obj = latest_panel
            if not panel_obj:
                flash(f"Case default panel '{panel_name}' could not be found.", "warning")
                continue
            flash(
                f"Case default panel '{panel_name}' version {panel_version} could not be found, using latest existing version",
                "warning",
            )

        distinct_genes.update([gene["hgnc_id"] for gene in panel_obj.get("genes", [])])

        # Check if case-specific panel is up-to-date with latest version of the panel
        if panel_obj["version"] < latest_panel["version"]:
            extra_genes, missing_genes = check_outdated_gene_panel(panel_obj, latest_panel)
            if extra_genes or missing_genes:
                case_obj["outdated_panels"][panel_name] = {
                    "missing_genes": missing_genes,
                    "extra_genes": extra_genes,
                }

        full_name = "{} ({})".format(panel_obj["display_name"], panel_obj["version"])
        case_obj["panel_names"].append(full_name)

    return list(distinct_genes)


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


def check_outdated_gene_panel(panel_obj, latest_panel):
    """Compare genes of a case gene panel with the latest panel version and return differences

    Args:
        panel_obj(dict): the gene panel of a case
        latest_panel(dict): the latest version of that gene panel

    returns:
        missing_genes, extra_genes
    """
    # Create a list of minified gene object for the case panel {hgnc_id, gene_symbol}
    case_panel_genes = set([gene.get("symbol", gene["hgnc_id"]) for gene in panel_obj["genes"]])
    # And for the latest panel
    latest_panel_genes = set(
        [gene.get("symbol", gene["hgnc_id"]) for gene in latest_panel["genes"]]
    )
    # Extract the genes unique to case panel
    extra_genes = case_panel_genes.difference(latest_panel_genes)

    # Extract the genes unique to latest panel
    missing_genes = latest_panel_genes.difference(case_panel_genes)

    return extra_genes, missing_genes


def add_bayesian_acmg_classification(variant_obj: dict):
    """Append info to display the ACMG VUS Bayesian score / temperature.
    Criteria have a term and a modifier field on the db document
    that are joined together in a string to conform to a regular
    ACMG term format. A set of such terms are passed on for evaluation
    to the same function as the ACMG classification form uses.
    """
    variant_acmg_classifications = list(
        store.get_evaluations_case_specific(document_id=variant_obj["_id"])
    )
    if variant_acmg_classifications:
        terms = set()
        for criterium in variant_acmg_classifications[0].get("criteria", []):
            term = criterium.get("term")
            if criterium.get("modifier"):
                term += f"_{criterium.get('modifier')}"
            terms.add(term)
        variant_obj["bayesian_acmg"] = get_acmg_temperature(terms)


def add_bayesian_ccv_classification(variant_obj: dict):
    """Append info to display the CCV VUS Bayesian score / temperature.
    Criteria have a term and a modifier field on the db document
    that are joined together in a string to conform to a regular
    CCV term format. A set of such terms are passed on for evaluation
    to the same function as the CCV classification form uses.
    """
    variant_ccv_classifications = list(
        store.get_ccv_evaluations_case_specific(document_id=variant_obj["_id"])
    )
    if variant_ccv_classifications:
        terms = set()
        for criterium in variant_ccv_classifications[0].get("ccv_criteria", []):
            term = criterium.get("term")
            if criterium.get("modifier"):
                term += f"_{criterium.get('modifier')}"
            terms.add(term)
        variant_obj["bayesian_ccv"] = get_ccv_temperature(terms)


def case_report_variants(store: MongoAdapter, case_obj: dict, institute_obj: dict, data: dict):
    """Gather evaluated variants info to include in case report."""

    evaluated_variants_by_type: Dict[str, list] = {vt: [] for vt in CASE_REPORT_VARIANT_TYPES}

    # Collect causative, partial causative and suspected variants
    for eval_category, case_key in CASE_REPORT_VARIANT_TYPES.items():
        for var_id in case_obj.get(case_key, []):
            var_obj = store.variant(document_id=var_id)
            if not var_obj:
                continue
            if case_key == "partial_causatives":
                var_obj["phenotypes"] = case_obj["partial_causatives"][var_id]
            add_bayesian_acmg_classification(var_obj)
            add_bayesian_ccv_classification(var_obj)
            evaluated_variants_by_type[eval_category].append(
                _get_decorated_var(
                    store, var_obj=var_obj, institute_obj=institute_obj, case_obj=case_obj
                )
            )

    for var_obj in store.evaluated_variants(
        case_id=case_obj["_id"], institute_id=institute_obj["_id"]
    ):
        _append_evaluated_variant_by_type(
            evaluated_variants_by_type, var_obj, institute_obj, case_obj
        )

    data["variants"] = evaluated_variants_by_type


def _get_decorated_var(
    store: MongoAdapter, var_obj: dict, institute_obj: dict, case_obj: dict
) -> dict:
    """Decorate a variant object for display using the variant controller"""
    return variant_decorator(
        store=store,
        variant_id=None,
        institute_id=institute_obj["_id"],
        case_name=case_obj["display_name"],
        variant_obj=var_obj,
        add_other=False,
        get_overlapping=False,
        variant_type=var_obj["category"],
        institute_obj=institute_obj,
        case_obj=case_obj,
    )["variant"]


def _append_evaluated_variant_by_type(
    evaluated_variants_by_type: dict, var_obj: dict, institute_obj: dict, case_obj: dict
):
    """We collect all evaluated variants except causative, partial causative and suspected variants,
    then partition them in the evaluated variants dict according to event type.
    Ensure variant actually has the corresponding key set, and that it is not just None.
    """
    for eval_category, variant_key in CASE_REPORT_VARIANT_TYPES.items():
        if variant_key in var_obj and var_obj[variant_key] is not None:

            add_bayesian_acmg_classification(var_obj)
            add_bayesian_ccv_classification(var_obj)

            evaluated_variants_by_type[eval_category].append(
                _get_decorated_var(
                    store, var_obj=var_obj, institute_obj=institute_obj, case_obj=case_obj
                )
            )


def case_report_content(store: MongoAdapter, institute_obj: dict, case_obj: dict) -> dict:
    """Gather data to be visualized in a case report."""

    data = {"institute": institute_obj}
    add_link_for_disease(case_obj=case_obj)
    data["case"] = case_obj
    data["cancer"] = case_obj.get("track") == "cancer"

    # Set a human-readable phenotype for the individuals
    pheno_map = CANCER_PHENOTYPE_MAP if data["cancer"] else PHENOTYPE_MAP
    for ind in case_obj.get("individuals"):
        ind["phenotype_human"] = pheno_map.get(ind["phenotype"])

    dismiss_options = DISMISS_VARIANT_OPTIONS
    if data["cancer"]:
        data["cancer_tier_options"] = CANCER_TIER_OPTIONS
        dismiss_options = {
            **DISMISS_VARIANT_OPTIONS,
            **CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
        }
        data["genes_in_panels"] = store.panels_to_genes(
            panel_ids=[
                panel["panel_id"]
                for panel in case_obj.get("panels", [])
                if panel.get("is_default", False) is True
            ],
            gene_format="symbol",
        )
    data["dismissed_options"] = dismiss_options

    data["comments"] = store.case_events_by_verb(
        category="case", institute=institute_obj, case=case_obj, verb="comment"
    )
    data["audits"] = store.case_events_by_verb(
        category="case", institute=institute_obj, case=case_obj, verb="filter_audit"
    )

    data["inherit_palette"] = INHERITANCE_PALETTE
    data["manual_rank_options"] = MANUAL_RANK_OPTIONS
    data["genetic_models"] = dict(GENETIC_MODELS)
    data["report_created_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    data["current_scout_version"] = __version__
    data["hpo_link_url"] = HPO_LINK_URL

    case_report_variants(store, case_obj, institute_obj, data)

    return data


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
    today = datetime.datetime.now().strftime(DATE_DAY_FORMATTER)
    samples = case_obj.get("individuals")
    coverage_stats = None

    case_has_chanjo_coverage(case_obj)
    case_has_chanjo2_coverage(case_obj)

    # Check if coverage and MT copy number stats are available via chanjo2 or chanjo
    if case_obj.get("chanjo2_coverage"):
        coverage_stats: Dict[str, dict] = chanjo2.mt_coverage_stats(case_obj=case_obj)
    elif case_obj.get("chanjo_coverage"):
        coverage_stats: Dict[str, dict] = chanjo_report.mt_coverage_stats(individuals=samples)

    query = {"chrom": get_case_mito_chromosome(case_obj)}
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

        # coverage_stats is None if app is not connected to Chanjo or {} if samples are not in Chanjo db
        if coverage_stats and sample_id in coverage_stats:
            # Write coverage stats header after introducing 2 empty lines
            for col, field in enumerate(MT_COV_STATS_HEADER):
                Report_Sheet.write(row + 3, col, field)

            # Write sample MT vs autosome coverage stats to excel sheet
            for col, item in enumerate(["mt_coverage", "autosome_cov", "mt_copy_number"]):
                Report_Sheet.write(row + 4, col, coverage_stats[sample_id].get(item))

        mitodel = sample.get("mitodel")

        if mitodel:
            for col, field in enumerate(MITODEL_HEADER):
                Report_Sheet.write(row + 6, col, field)

            for col, item in enumerate(["normal", "discordant", "ratioppk"]):
                Report_Sheet.write(row + 7, col, mitodel.get(item))

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

    link = url_for(
        "cases.case",
        institute_id=institute_obj["_id"],
        case_name=case_obj["display_name"],
    )

    store.update_case_individual(case_obj, user_obj, institute_obj, link)


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

    link = url_for(
        "cases.case",
        institute_id=institute_obj["_id"],
        case_name=case_obj["display_name"],
    )

    store.update_case_sample(case_obj, user_obj, institute_obj, link)


def _all_hpo_gene_list_genes(
    store: MongoAdapter,
    hpo_genes: Dict,
    build: str,
    is_clinical: bool,
    clinical_symbols: Set,
    dynamic_gene_list: List,
    hpo_gene_list: Set,
) -> Set:
    """Populate hpo_genes from dynamic gene list.

    Loop over dynamic phenotypes of a case, populating hpo_genes.
    Also return all gene symbols found as a set.

    An empty set returned indicates that genes should not be grouped by phenotype - use a single "Analysed genes" group.
    """

    all_hpo_gene_list_genes = set()

    # do not display genes by phenotype if we have no hpo gene list, but a dynamic one
    if not hpo_gene_list and dynamic_gene_list:
        return set()

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
            gene_caption = store.hgnc_gene_caption(gene_id, build)
            if gene_caption is None:
                continue
            if gene_id not in dynamic_gene_list:
                # gene was filtered out because min matching phenotypes > 1 (or the panel was generated with older genotype-phenotype mapping)
                return set()
            add_symbol = gene_caption.get("hgnc_symbol", f"hgnc:{gene_id}")
            if is_clinical and (add_symbol not in clinical_symbols):
                continue
            gene_list.append(add_symbol)
            all_hpo_gene_list_genes.add(add_symbol)

        hpo_genes[hpo_id] = {
            "description": hpo_term.get("description"),
            "genes": ", ".join(sorted(gene_list)),
        }

    return all_hpo_gene_list_genes


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

    hpo_gene_list = case_obj.get("dynamic_panel_phenotypes", [])

    all_hpo_gene_list_genes = _all_hpo_gene_list_genes(
        store,
        hpo_genes,
        build,
        is_clinical,
        clinical_symbols,
        dynamic_gene_list,
        hpo_gene_list,
    )

    if all_hpo_gene_list_genes:
        # if just some gene ware manually added (or is left on dynamic panel for other reasons)
        non_hpo_genes = unique_genes - all_hpo_gene_list_genes
        if len(non_hpo_genes) > 0:
            hpo_genes["Analysed genes"] = {
                "description": "Non HPO panel genes",
                "genes": ", ".join(sorted(non_hpo_genes)),
            }
        return hpo_genes

    # otherwise do not display genes by phenotype - one unique gene group only
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


def update_clinical_filter_hpo(store, current_user, institute_obj, case_obj, hpo_clinical_filter):
    """Update HPO clinical filter use for a case."""
    user_obj = store.user(current_user.email)
    link = url_for(
        "cases.case", institute_id=institute_obj["_id"], case_name=case_obj["display_name"]
    )
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
    try:
        institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    except Exception:
        flash(
            f"Could not find a case named {case_name} for institute {institute_id}",
            "warning",
        )
        return

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

    obj_id_group = ObjectId(case_group)
    if obj_id_group not in current_group_ids:
        return
    current_group_ids.remove(obj_id_group)
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
    candidate_vars = request.form.getlist("selected_var")

    if len(candidate_vars) > 3:
        flash(
            "At the moment it is not possible to save to MatchMaker more than 3 candidate variants / genes",
            "warning",
        )
        return redirect(request.referrer)

    save_gender = "sex" in request.form
    features = (
        hpo_terms(case_obj)
        if "features" in request.form and case_obj.get("phenotype_terms")
        else []
    )
    disorders = omim_terms(store, case_obj) if "disorders" in request.form else []
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
                store,
                case_obj,
                individual.get("display_name"),
                candidate_vars,
                genes_only,
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
                "an error occurred while adding patient to matchmaker: {}".format(resp),
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

            flash(
                f"Deleted patient '{patient_id}', case '{case_name}' from MatchMaker",
                "success",
            )
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
    data = {
        "institute": institute_obj,
        "case": case_obj,
        "server_errors": [],
        "panel": 1,
    }
    matches = {}
    for patient in case_obj.get("mme_submission", {}).get("patients", []):
        patient_id = patient["id"]
        matches[patient_id] = None
        server_resp = matchmaker.patient_matches(patient_id)
        if server_resp.get("status_code") != 200:  # server returned error
            flash(
                "MatchMaker server returned error:{}".format(data["server_errors"]),
                "danger",
            )
            return redirect(request.referrer)
        # server returned a valid response
        pat_matches = []
        if server_resp.get("content", {}).get("matches"):
            pat_matches = parse_matches(patient_id, server_resp["content"]["matches"])
        matches[patient_id] = pat_matches

    data["hpo_link_url"] = HPO_LINK_URL
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


def _matching_causatives(
    store, case_obj, other_causatives_filter=[], other_causatives_in_default_panels_filter=[]
) -> tuple:
    """Fetch and categorize matching causatives for a case

    Matching causative variants from other cases are fetched and sorted into a
    tuple of two lists of all matching causative variants and a subset of those
    found in default gene panels.

    Args:
        store(adapter.MongoAdapter)
        case_obj(models.Case)
        other_causatives_filter(list[str])
        other_causatives_in_default_panels_filter(list[str])

    Returns:
        tuple(
            other_causatives(list[dict]),
                All matched secondary findings, including secondary findings
                found in default gene panels
            other_causatives_in_default_panels(list[dict]),
                The subset of all secondary findings found in default gene panels
        )
    """
    matching_causatives = store.case_matching_causatives(case_obj=case_obj)

    other_causatives = []
    other_causatives_in_default_panels = []

    for causative in matching_causatives:
        hgnc_ids = {gene.get("hgnc_id") for gene in causative.get("genes", [])}
        # Fetch all matching causatives if no causatives_filter defined
        # or only causatives matching the filter:
        if not other_causatives_filter or (hgnc_ids & set(other_causatives_filter)):
            other_causatives.append(causative)
        # Only matching causatives in default gene panels:
        if hgnc_ids & set(other_causatives_in_default_panels_filter):
            other_causatives_in_default_panels.append(causative)

    return other_causatives, other_causatives_in_default_panels


def add_link_for_disease(case_obj: dict):
    """Updates the case diseases_phenotypes to include an external link for use in the frontend"""
    case_diagnoses = case_obj.get("diagnosis_phenotypes", [])

    if case_diagnoses and isinstance(case_diagnoses[0], dict):
        for diagnosis in case_diagnoses:
            #: Add link
            diagnosis.update({"disease_link": disease_link(disease_id=diagnosis["disease_id"])})


def remove_dynamic_genes(store: dict, case_obj: dict, institute_obj: dict, request_form: dict):
    """Remove one or more genes from the dynamic gene list. If there are no more
    genes on the list, also stop using the HPO panel for clinical filter."""
    case_dynamic_genes = [dyn_gene["hgnc_id"] for dyn_gene in case_obj.get("dynamic_gene_list")]
    genes_to_remove = [int(gene_id) for gene_id in request_form.getlist("dynamicGene")]
    hgnc_ids = list(set(case_dynamic_genes) - set(genes_to_remove))
    store.update_dynamic_gene_list(
        case_obj,
        hgnc_ids=hgnc_ids,
        delete_only=True,
    )
    if not hgnc_ids:
        hpo_clinical_filter = False
        case_obj["hpo_clinical_filter"] = hpo_clinical_filter
        update_clinical_filter_hpo(
            store, current_user, institute_obj, case_obj, hpo_clinical_filter
        )
