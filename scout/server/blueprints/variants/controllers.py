import datetime
import logging
import os.path
import urllib.parse
from datetime import date
from pprint import pprint as pp

from flask import Response, flash, request, url_for
from flask_login import current_user
from flask_mail import Message
from werkzeug.datastructures import Headers, MultiDict
from xlsxwriter import Workbook

from scout.constants import (
    ACMG_COMPLETE_MAP,
    ACMG_MAP,
    ACMG_OPTIONS,
    CALLERS,
    CANCER_TIER_OPTIONS,
    CLINSIG_MAP,
    DISMISS_VARIANT_OPTIONS,
    CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
    MANUAL_RANK_OPTIONS,
    MOSAICISM_OPTIONS,
    SEVERE_SO_TERMS,
    SPIDEX_HUMAN,
    VERBS_MAP,
)
from scout.constants.acmg import ACMG_CRITERIA
from scout.constants.variants_export import EXPORT_HEADER, VERIFIED_VARIANTS_HEADER
from scout.export.variant import export_verified_variants
from scout.server.blueprints.genes.controllers import gene
from scout.server.blueprints.variant.utils import predictions
from scout.server.links import str_source_link, ensembl, cosmic_link
from scout.server.utils import (
    case_append_alignments,
    institute_and_case,
    user_institutes,
    variant_case,
)
from scout.utils.scout_requests import fetch_refseq_version

from .forms import CancerFiltersForm, FiltersForm, StrFiltersForm, SvFiltersForm, VariantFiltersForm

LOG = logging.getLogger(__name__)


def variants(store, institute_obj, case_obj, variants_query, variant_count, page=1, per_page=50):
    """Pre-process list of variants."""

    skip_count = per_page * max(page - 1, 0)
    more_variants = True if variant_count > (skip_count + per_page) else False
    variant_res = variants_query.skip(skip_count).limit(per_page)

    genome_build = str(case_obj.get("genome_build", "37"))
    if genome_build not in ["37", "38"]:
        genome_build = "37"

    variants = []
    for variant_obj in variant_res:
        overlapping_svs = [sv for sv in store.overlapping(variant_obj)]
        variant_obj["overlapping"] = overlapping_svs or None

        evaluations = []
        is_research = variant_obj["variant_type"] == "research"
        # Get previous ACMG evalautions of the variant from other cases
        for evaluation_obj in store.get_evaluations(variant_obj):
            if evaluation_obj["case_id"] == case_obj["_id"]:
                continue

            classification = evaluation_obj["classification"]

            if is_research or classification not in ["pathogenic", "likely_pathogenic"]:
                evaluation_obj["classification"] = ACMG_COMPLETE_MAP.get(classification)
                evaluations.append(evaluation_obj)

        variant_obj["evaluations"] = evaluations

        clinical_var_obj = variant_obj
        if is_research:
            variant_obj["research_assessments"] = get_manual_assessments(variant_obj)

            clinical_var_obj = store.variant(
                case_id=case_obj["_id"], simple_id=variant_obj["simple_id"], variant_type="clinical"
            )

        variant_obj["clinical_assessments"] = get_manual_assessments(clinical_var_obj)

        if case_obj.get("group"):
            variant_obj["group_assessments"] = _get_group_assessments(store, case_obj, variant_obj)

        variants.append(
            parse_variant(
                store, institute_obj, case_obj, variant_obj, update=True, genome_build=genome_build
            )
        )

    return {"variants": variants, "more_variants": more_variants}


def _get_group_assessments(store, case_obj, variant_obj):
    """Return manual variant assessments for other cases grouped with this one.

    Args:
        case_obj
    Returns:
        group_assessments(list(dict))
    """
    group_assessments = []

    group_case_ids = set()
    for group_id in case_obj.get("group"):
        group_case_ids.update(store.case_ids_from_group_id(group_id))

        for group_case_id in group_case_ids:
            # Returning an extra assessment for variants from the same case is pointless
            if group_case_id == case_obj["_id"]:
                continue

            cohort_var_obj = store.variant(
                case_id=group_case_id,
                simple_id=variant_obj["simple_id"],
                variant_type=variant_obj["variant_type"],
            )
            group_assessments.extend(get_manual_assessments(cohort_var_obj))

    return group_assessments


def sv_variants(store, institute_obj, case_obj, variants_query, variant_count, page=1, per_page=50):
    """Pre-process list of SV variants."""
    skip_count = per_page * max(page - 1, 0)

    more_variants = True if variant_count > (skip_count + per_page) else False
    variants = []
    genome_build = str(case_obj.get("genome_build", "37"))
    if genome_build not in ["37", "38"]:
        genome_build = "37"

    for variant_obj in variants_query.skip(skip_count).limit(per_page):
        # show previous classifications for research variants
        clinical_var_obj = variant_obj
        if variant_obj["variant_type"] == "research":
            clinical_var_obj = store.variant(
                case_id=case_obj["_id"], simple_id=variant_obj["simple_id"], variant_type="clinical"
            )
        if clinical_var_obj is not None:
            variant_obj["clinical_assessments"] = get_manual_assessments(clinical_var_obj)

        variants.append(
            parse_variant(store, institute_obj, case_obj, variant_obj, genome_build=genome_build)
        )

    return {"variants": variants, "more_variants": more_variants}


def str_variants(
    store, institute_obj, case_obj, variants_query, variant_count, page=1, per_page=50
):
    """Pre-process list of STR variants."""

    # case bam_files for quick access to alignment view.
    case_append_alignments(case_obj)

    return variants(
        store, institute_obj, case_obj, variants_query, variant_count, page=page, per_page=per_page
    )


def get_manual_assessments(variant_obj):
    """Return manual assessments ready for display.

    An assessment dict of str has keys "title", "label" and "display_class".

    args:
        variant_obj(variant)

    returns:
        assessments(array(dict))
    """

    ## display manual input of interest: classified, commented, tagged, mosaicism or dismissed.
    assessment_keywords = [
        "acmg_classification",
        "manual_rank",
        "cancer_tier",
        "dismiss_variant",
        "mosaic_tags",
    ]

    assessments = []

    if variant_obj is None:
        return assessments

    for assessment_type in assessment_keywords:
        assessment = {}
        if variant_obj.get(assessment_type) is not None:
            if assessment_type == "manual_rank":
                manual_rank = variant_obj[assessment_type]
                assessment["title"] = "Manual rank: {}".format(
                    MANUAL_RANK_OPTIONS[manual_rank]["description"]
                )
                assessment["label"] = MANUAL_RANK_OPTIONS[manual_rank]["label"]
                assessment["display_class"] = MANUAL_RANK_OPTIONS[manual_rank]["label_class"]

            if assessment_type == "cancer_tier":
                cancer_tier = variant_obj[assessment_type]
                assessment["title"] = "Cancer tier: {}".format(
                    CANCER_TIER_OPTIONS[cancer_tier]["description"]
                )
                assessment["label"] = CANCER_TIER_OPTIONS[cancer_tier]["label"]
                assessment["display_class"] = CANCER_TIER_OPTIONS[cancer_tier]["label_class"]

            if assessment_type == "acmg_classification":
                classification = variant_obj[assessment_type]
                if isinstance(classification, int):
                    acmg_code = ACMG_MAP[classification]
                    classification = ACMG_COMPLETE_MAP[acmg_code]

                assessment["title"] = "ACMG: {}".format(classification["label"])
                assessment["label"] = classification["short"]
                assessment["display_class"] = classification["color"]

            if assessment_type == "dismiss_variant":
                dismiss_variant_options = {
                    **DISMISS_VARIANT_OPTIONS,
                    **CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
                }
                assessment["label"] = "Dismissed"
                assessment["title"] = "dismiss:<br>"
                for reason in variant_obj[assessment_type]:
                    if not isinstance(reason, int):
                        reason = int(reason)
                        assessment["title"] += "<strong>{}</strong> - {}<br><br>".format(
                            dismiss_variant_options[reason]["label"],
                            dismiss_variant_options[reason]["description"],
                        )
                assessment["display_class"] = "secondary"

            if assessment_type == "mosaic_tags":
                assessment["label"] = "Mosaicism"
                assessment["title"] = "mosaicism:<br>"
                for reason in variant_obj[assessment_type]:
                    if not isinstance(reason, int):
                        reason = int(reason)
                    assessment["title"] += "<strong>{}</strong> - {}<br><br>".format(
                        MOSAICISM_OPTIONS[reason]["label"], MOSAICISM_OPTIONS[reason]["description"]
                    )
                assessment["display_class"] = "secondary"

            assessments.append(assessment)

    return assessments


def parse_variant(
    store, institute_obj, case_obj, variant_obj, update=False, genome_build="37", get_compounds=True
):
    """Parse information about variants.
    - Adds information about compounds
    - Updates the information about compounds if necessary and 'update=True'
    Args:
        store(scout.adapter.MongoAdapter)
        institute_obj(scout.models.Institute)
        case_obj(scout.models.Case)
        variant_obj(scout.models.Variant)
        update(bool): If variant should be updated in database
        genome_build(str)
    """
    has_changed = False
    compounds = variant_obj.get("compounds", [])
    if compounds and get_compounds:
        # Check if we need to add compound information
        # If it is the first time the case is viewed we fill in some compound information
        if "not_loaded" not in compounds[0]:
            new_compounds = store.update_variant_compounds(variant_obj)
            variant_obj["compounds"] = new_compounds
            has_changed = True

        # sort compounds on combined rank score
        variant_obj["compounds"] = sorted(
            variant_obj["compounds"], key=lambda compound: -compound["combined_score"]
        )

    # Update the hgnc symbols if they are incorrect
    variant_genes = variant_obj.get("genes")
    if variant_genes is not None:
        for gene_obj in variant_genes:
            # If there is no hgnc id there is nothin we can do
            if not gene_obj["hgnc_id"]:
                continue
            # Else we collect the gene object and check the id
            if gene_obj.get("hgnc_symbol") is None or gene_obj.get("phenotypes") is None:
                hgnc_gene = store.hgnc_gene(gene_obj["hgnc_id"], build=genome_build)
                if not hgnc_gene:
                    continue
                has_changed = True
                gene_obj["hgnc_symbol"] = hgnc_gene["hgnc_symbol"]
                # phenotypes may not exist for the hgnc_gene either, but try
                gene_obj["phenotypes"] = hgnc_gene.get("phenotypes")

    # We update the variant if some information was missing from loading
    # Or if symbold in reference genes have changed
    if update and has_changed:
        variant_obj = store.update_variant(variant_obj)

    variant_obj["comments"] = store.events(
        institute_obj, case=case_obj, variant_id=variant_obj["variant_id"], comments=True
    )

    if variant_genes:
        variant_obj.update(predictions(variant_genes))
        if variant_obj.get("category") == "cancer":
            variant_obj.update(get_variant_info(variant_genes))

    for compound_obj in compounds:
        compound_obj.update(predictions(compound_obj.get("genes", [])))

    classification = variant_obj.get("acmg_classification")
    if isinstance(classification, int):
        acmg_code = ACMG_MAP[variant_obj["acmg_classification"]]
        variant_obj["acmg_classification"] = ACMG_COMPLETE_MAP[acmg_code]

    # convert length for SV variants
    variant_length = variant_obj.get("length")
    variant_obj["length"] = {100000000000: "inf", -1: "n.d."}.get(variant_length, variant_length)
    if not "end_chrom" in variant_obj:
        variant_obj["end_chrom"] = variant_obj["chromosome"]

    # variant level links shown on variants page
    variant_obj["cosmic_link"] = cosmic_link(variant_obj)
    variant_obj["str_source_link"] = str_source_link(variant_obj)

    return variant_obj


def download_variants(store, case_obj, variant_objs):
    """Download filtered variants for a case to an excel file

    Args:
        store(adapter.MongoAdapter)
        case_obj(dict)
        variant_objs(PyMongo cursor)

    Returns:
        an HTTP response containing a csv file
    """
    document_header = variants_export_header(case_obj)
    export_lines = []
    # Return max 500 variants
    export_lines = variant_export_lines(store, case_obj, variant_objs.limit(500))

    def generate(header, lines):
        yield header + "\n"
        for line in lines:
            yield line + "\n"

    headers = Headers()
    headers.add(
        "Content-Disposition",
        "attachment",
        filename=str(case_obj["display_name"]) + "-filtered_sv-variants.csv",
    )
    # return a csv with the exported variants
    return Response(
        generate(",".join(document_header), export_lines), mimetype="text/csv", headers=headers
    )


def variant_export_lines(store, case_obj, variants_query):
    """Get variants info to be exported to file, one list (line) per variant.
    Args:
        store(scout.adapter.MongoAdapter)
        case_obj(scout.models.Case)
        variants_query: a list of variant objects, each one is a dictionary
    Returns:
        export_variants: a list of strings. Each string  of the list corresponding to the fields
                         of a variant to be exported to file, separated by comma
    """

    export_variants = []

    for variant in variants_query:
        variant_line = []
        position = variant["position"]
        change = variant["reference"] + ">" + variant["alternative"]
        variant_line.append(variant["rank_score"])
        variant_line.append(variant["chromosome"])
        variant_line.append(position)
        variant_line.append(change)
        variant_line.append("_".join([str(position), change]))

        # gather gene info:
        gene_list = variant.get("genes")  # this is a list of gene objects

        # if variant is in genes
        if gene_list is not None and len(gene_list) > 0:
            gene_info = variant_export_genes_info(store, gene_list)
            variant_line += gene_info
        else:
            empty_col = 0
            while empty_col < 3:
                variant_line.append(
                    "-"
                )  # empty HGNC id, emoty gene name and empty transcripts columns
                empty_col += 1

        variant_gts = variant["samples"]  # list of coverage and gt calls for case samples
        for individual in case_obj["individuals"]:
            for variant_gt in variant_gts:
                if individual["individual_id"] == variant_gt["sample_id"]:
                    # gather coverage info
                    variant_line.append(variant_gt["allele_depths"][0])  # AD reference
                    variant_line.append(variant_gt["allele_depths"][1])  # AD alternate
                    # gather genotype quality info
                    variant_line.append(variant_gt["genotype_quality"])

        variant_line = [str(i) for i in variant_line]
        export_variants.append(",".join(variant_line))

    return export_variants


def variant_export_genes_info(store, gene_list):
    """Adds gene info to a list of fields corresponding to a variant to be exported.

    Args:
        gene_list(list) A list of gene objects contained in the variant

    Returns:
        gene_info(list) A list of gene-relates string info
    """
    gene_ids = []
    gene_names = []
    canonical_txs = []
    hgvs_c = []
    pt_c = []

    gene_info = []

    for gene_obj in gene_list:
        hgnc_id = gene_obj["hgnc_id"]
        gene_name = gene(store, hgnc_id)["symbol"]

        gene_ids.append(hgnc_id)
        gene_names.append(gene_name)

        if gene_obj.get("canonical_transcript"):
            canonical_txs.append(gene_obj.get("canonical_transcript"))

        hgvs_nucleotide = "-"
        protein_change = "-"
        # gather HGVS info from gene transcripts

        transcripts_list = gene_obj.get("transcripts")
        for transcript_obj in transcripts_list:
            if transcript_obj["transcript_id"] == gene_obj.get("canonical_transcript"):
                hgvs_nucleotide = transcript_obj.get("coding_sequence_name") or "-"
                protein_change = transcript_obj.get("protein_sequence_name") or "-"
        hgvs_c.append(hgvs_nucleotide)
        pt_c.append(protein_change)

    for item in [gene_ids, gene_names, canonical_txs, hgvs_c, pt_c]:
        gene_info.append(";".join(str(x) for x in item))

    return gene_info


def variants_export_header(case_obj):
    """Returns a header for the CSV file with the filtered variants to be exported.
    Args:
        case_obj(scout.models.Case)
    Returns:
        header: includes the fields defined in scout.constants.variants_export EXPORT_HEADER
                + AD_reference, AD_alternate, GT_quality for each sample analysed for a case
    """
    header = []
    header = header + EXPORT_HEADER
    # Add fields specific for case samples
    for individual in case_obj["individuals"]:
        display_name = str(individual["display_name"])
        header.append("AD_reference_" + display_name)  # Add AD reference field for a sample
        header.append("AD_alternate_" + display_name)  # Add AD alternate field for a sample
        header.append("GT_quality_" + display_name)  # Add Genotype quality field for a sample
    return header


def get_variant_info(genes):
    """Get variant information"""
    data = {"canonical_transcripts": []}
    for gene_obj in genes:
        if not gene_obj.get("canonical_transcripts"):
            tx = gene_obj["transcripts"][0]
            tx_id = tx["transcript_id"]
            exon = tx.get("exon", "-")
            c_seq = tx.get("coding_sequence_name", "-")
        else:
            tx_id = gene_obj["canonical_transcripts"]
            exon = gene_obj.get("exon", "-")
            c_seq = gene_obj.get("hgvs_identifier", "-")

        if len(c_seq) > 20:
            c_seq = c_seq[:20] + "..."

        gene_id = gene_obj.get("hgnc_symbol") or str(gene_obj["hgnc_id"])
        value = ":".join([gene_id, tx_id, exon, c_seq])
        data["canonical_transcripts"].append(value)

    return data


def cancer_variants(store, institute_id, case_name, variants_query, variant_count, form, page=1):
    """Fetch data related to cancer variants for a case."""

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    per_page = 50
    skip_count = per_page * max(page - 1, 0)
    more_variants = True if variant_count > (skip_count + per_page) else False

    variant_res = variants_query.skip(skip_count).limit(per_page)

    variants_list = []

    for variant in variant_res:
        elem = parse_variant(store, institute_obj, case_obj, variant, update=True)
        variants_list.append(elem)

    data = dict(
        page=page,
        more_variants=more_variants,
        institute=institute_obj,
        case=case_obj,
        variants=variants_list,
        manual_rank_options=MANUAL_RANK_OPTIONS,
        cancer_tier_options=CANCER_TIER_OPTIONS,
        form=form,
    )
    return data


def get_clinvar_submission(store, institute_id, case_name, variant_id, submission_id):
    """Collects all variants from the clinvar submission collection with a specific submission_id
    Args:
        store(scout.adapter.MongoAdapter)
        institute_id(str): Institute ID
        case_name(str): case ID
        variant_id(str): variant._id
        submission_id(str): clinvar submission id, i.e. SUB76578
    Returns:
        A dictionary with all the data to display the clinvar_update.html template page
    """

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    pinned = [
        store.variant(variant_id) or variant_id for variant_id in case_obj.get("suspects", [])
    ]
    variant_obj = store.variant(variant_id)
    clinvar_submission_objs = store.clinvars(submission_id=submission_id)
    return dict(
        today=str(date.today()),
        institute=institute_obj,
        case=case_obj,
        variant=variant_obj,
        pinned_vars=pinned,
        clinvars=clinvar_submission_objs,
    )


def upload_panel(store, institute_id, case_name, stream):
    """Parse out HGNC symbols from a stream."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    raw_symbols = [
        line.strip().split("\t")[0] for line in stream if line and not line.startswith("#")
    ]
    # check if supplied gene symbols exist
    hgnc_symbols = []
    for raw_symbol in raw_symbols:
        if store.hgnc_genes_find_one(raw_symbol) is None:
            hgnc_symbols.append(raw_symbol)
        else:
            flash("HGNC symbol not found: {}".format(raw_symbol), "warning")

    return hgnc_symbols


def gene_panel_choices(institute_obj, case_obj):
    """Populates the multiselect containing all the gene panels to be used in variants filtering
    Args:
        institute_obj(dict): an institute dictionary
        case_obj(dict): a case dictionary

    Returns:
        panel_list(list): a list of tuples containing the multiselect panel values/display name
    """
    panel_list = []
    # Add case default panels and the institute-specific panels to the panel select options
    for panel in case_obj.get("panels", []):
        panel_option = (panel["panel_name"], panel["display_name"])
        panel_list.append(panel_option)

    institute_choices = institute_obj.get("gene_panels", {})

    for panel_name, display_name in institute_choices.items():
        panel_option = (panel_name, display_name)
        if panel_option not in panel_list:
            panel_list.append(panel_option)

    # Add HPO panel
    panel_list.append(("hpo", "HPO"))
    return panel_list


def populate_filters_form(store, institute_obj, case_obj, user_obj, category, request_form):
    # Update filter settings if Clinical Filter was requested
    form = None
    clinical_filter_panels = []

    default_panels = []
    for panel in case_obj.get("panels", []):
        if panel.get("is_default"):
            default_panels.append(panel["panel_name"])

    # The clinical filter button will only
    if case_obj.get("hpo_clinical_filter"):
        clinical_filter_panels = ["hpo"]
    else:
        clinical_filter_panels = default_panels

    FiltersFormClass = VariantFiltersForm
    if category == "snv":
        FiltersFormClass = FiltersForm
        clinical_filter = MultiDict(
            {
                "variant_type": "clinical",
                "region_annotations": ["exonic", "splicing"],
                "functional_annotations": SEVERE_SO_TERMS,
                "clinsig": [4, 5],
                "clinsig_confident_always_returned": True,
                "gnomad_frequency": str(institute_obj["frequency_cutoff"]),
                "gene_panels": clinical_filter_panels,
            }
        )
    elif category in ("sv", "cancer_sv"):
        FiltersFormClass = SvFiltersForm
        clinical_filter = MultiDict(
            {
                "variant_type": "clinical",
                "region_annotations": ["exonic", "splicing"],
                "functional_annotations": SEVERE_SO_TERMS,
                "thousand_genomes_frequency": str(institute_obj["frequency_cutoff"]),
                "clingen_ngi": 10,
                "swegen": 10,
                "size": 100,
                "gene_panels": clinical_filter_panels,
            }
        )
    elif category == "cancer":
        FiltersFormClass = CancerFiltersForm
        clinical_filter = MultiDict(
            {
                "variant_type": "clinical",
                "region_annotations": ["exonic", "splicing"],
                "functional_annotations": SEVERE_SO_TERMS,
            }
        )
    elif category == "str":
        FiltersFormClass = StrFiltersForm

    if bool(request_form.get("clinical_filter")):
        form = FiltersFormClass(clinical_filter)
    elif bool(request_form.get("save_filter")):
        # The form should be applied and remain set the page after saving
        form = FiltersFormClass(request_form)
        # Stash the filter to db to make available for this institute
        filter_obj = request_form
        store.stash_filter(filter_obj, institute_obj, case_obj, user_obj, category)
    elif bool(request_form.get("load_filter")):
        filter_id = request_form.get("filters")
        filter_obj = store.retrieve_filter(filter_id)
        if filter_obj is not None:
            form = FiltersFormClass(MultiDict(filter_obj))
        else:
            flash("Requested filter was not found", "warning")
    elif bool(request_form.get("delete_filter")):
        filter_id = request_form.get("filters")
        institute_id = institute_obj.get("_id")
        filter_obj = store.delete_filter(filter_id, institute_id, current_user.email)
        if filter_obj is not None:
            form = FiltersFormClass(request_form)
        else:
            flash("Requested filter was not found", "warning")
    if form is None:
        form = FiltersFormClass(request_form)

    return form


def case_default_panels(case_obj):
    """Get a list of case default panels from a case dictionary

    Args:
        case_obj(dict): a case object

    Returns:
        case_panels(list): a list of panels (panel_name)
    """
    case_panels = [
        panel["panel_name"]
        for panel in case_obj.get("panels", [])
        if panel.get("is_default", None) is True
    ]
    return case_panels


def populate_sv_filters_form(store, institute_obj, case_obj, category, request_obj):
    """Populate a filters form object of the type SvFiltersForm

    Accepts:
        store(adapter.MongoAdapter)
        institute_obj(dict)
        case_obj(dict)
        category(str)
        request_obj(Flask.requests obj)

    Returns:
        form(SvFiltersForm)
    """

    form = SvFiltersForm(request_obj.args)
    user_obj = store.user(current_user.email)

    if request_obj.method == "GET":
        form = SvFiltersForm(request_obj.args)
        variant_type = request_obj.args.get("variant_type", "clinical")
        form.variant_type.data = variant_type
        # set chromosome to all chromosomes
        form.chrom.data = request_obj.args.get("chrom", "")
        if variant_type == "clinical":
            form.gene_panels.data = case_default_panels(case_obj)

    else:  # POST
        form = populate_filters_form(
            store, institute_obj, case_obj, user_obj, category, request_obj.form
        )

    # populate filters dropdown
    available_filters = store.filters(institute_obj["_id"], category)
    form.filters.choices = [
        (filter.get("_id"), filter.get("display_name")) for filter in available_filters
    ]

    # populate available panel choices
    form.gene_panels.choices = gene_panel_choices(institute_obj, case_obj)

    # check if supplied gene symbols exist
    hgnc_symbols = []
    non_clinical_symbols = []
    not_found_symbols = []
    not_found_ids = []
    if (form.hgnc_symbols.data) and len(form.hgnc_symbols.data) > 0:
        is_clinical = form.data.get("variant_type", "clinical") == "clinical"
        clinical_symbols = store.clinical_symbols(case_obj) if is_clinical else None
        for hgnc_symbol in form.hgnc_symbols.data:
            if hgnc_symbol.isdigit():
                hgnc_gene = store.hgnc_gene(int(hgnc_symbol), case_obj["genome_build"])
                if hgnc_gene is None:
                    not_found_ids.append(hgnc_symbol)
                else:
                    hgnc_symbols.append(hgnc_gene["hgnc_symbol"])
            elif sum(1 for i in store.hgnc_genes(hgnc_symbol)) == 0:
                not_found_symbols.append(hgnc_symbol)
            elif is_clinical and (hgnc_symbol not in clinical_symbols):
                non_clinical_symbols.append(hgnc_symbol)
            else:
                hgnc_symbols.append(hgnc_symbol)

    if not_found_ids:
        flash("HGNC id not found: {}".format(", ".join(not_found_ids)), "warning")
    if not_found_symbols:
        flash("HGNC symbol not found: {}".format(", ".join(not_found_symbols)), "warning")
    if non_clinical_symbols:
        flash(
            "Gene not included in clinical list: {}".format(", ".join(non_clinical_symbols)),
            "warning",
        )
    form.hgnc_symbols.data = hgnc_symbols

    # handle HPO gene list separately
    if "hpo" in form.data["gene_panels"]:
        hpo_symbols = list(
            set(term_obj["hgnc_symbol"] for term_obj in case_obj["dynamic_gene_list"])
        )

        current_symbols = set(hgnc_symbols)
        current_symbols.update(hpo_symbols)
        form.hgnc_symbols.data = list(current_symbols)

    return form


def verified_excel_file(store, institute_list, temp_excel_dir):
    """Collect all verified variants in a list on institutes and save them to file
    Args:
        store(adapter.MongoAdapter)
        institute_list(list): a list of institute ids
        temp_excel_dir(os.Path): folder where the temp excel files are written to
    Returns:
        written_files(int): the number of files written to temp_excel_dir
    """
    document_lines = []
    written_files = 0
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    LOG.info("Creating verified variant document..")

    for cust in institute_list:
        verif_vars = store.verified(institute_id=cust)
        LOG.info("Found {} verified variants for customer {}".format(len(verif_vars), cust))

        if not verif_vars:
            continue
        unique_callers = set()
        for var_type, var_callers in CALLERS.items():
            for caller in var_callers:
                unique_callers.add(caller.get("id"))
        cust_verified = export_verified_variants(verif_vars, unique_callers)

        document_name = ".".join([cust, "_verified_variants", today]) + ".xlsx"
        workbook = Workbook(os.path.join(temp_excel_dir, document_name))
        Report_Sheet = workbook.add_worksheet()

        # Write the column header
        row = 0
        for col, field in enumerate(VERIFIED_VARIANTS_HEADER + list(unique_callers)):
            Report_Sheet.write(row, col, field)

        # Write variant lines, after header (start at line 1)
        for row, line in enumerate(cust_verified, 1):  # each line becomes a row in the document
            for col, field in enumerate(line):  # each field in line becomes a cell
                Report_Sheet.write(row, col, field)
        workbook.close()

        if os.path.exists(os.path.join(temp_excel_dir, document_name)):
            written_files += 1

    return written_files


def activate_case(store, institute_obj, case_obj, current_user):
    """Activate case when visited for the first time.

    Args:
        store(adapter.MongoAdapter)
        institute_obj(dict) a scout institutet object
        case_obj(dict) a scout case object
        current_user(UserMixin): a scout user
    """

    # update status of case if visited for the first time
    if case_obj["status"] == "inactive" and not current_user.is_admin:
        flash("You just activated this case!", "info")

        user_obj = store.user(current_user.email)
        case_link = url_for(
            "cases.case", institute_id=institute_obj["_id"], case_name=case_obj["display_name"]
        )
        store.update_status(institute_obj, case_obj, user_obj, "active", case_link)


def dismiss_variant_list(store, institute_obj, case_obj, link_page, variants_list, dismiss_reasons):
    """Dismiss a list of variants for a case

    Args:
        store(adapter.MongoAdapter)
        institute_obj(dict): an institute dictionary
        case_obj(dict): a case dictionary
        link_page(str): "variant.variant" for snvs, "variant.sv_variant" for SVs and so on
        variants_list(list): list of variant._ids (strings)
        dismiss_reasons(list): list of dismiss options
    """
    user_obj = store.user(current_user.email)
    for variant_id in variants_list:
        variant_obj = store.variant(variant_id)
        if variant_obj is None:
            continue
        # create variant link
        link = url_for(
            link_page,
            institute_id=institute_obj["_id"],
            case_name=case_obj["display_name"],
            variant_id=variant_id,
        )
        # dismiss variant
        store.update_dismiss_variant(
            institute_obj, case_obj, user_obj, link, variant_obj, dismiss_reasons
        )
