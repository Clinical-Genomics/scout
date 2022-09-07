import logging
from datetime import datetime

from scout.constants import CLINVAR_INHERITANCE_MODELS, CLNSIG_TERMS
from scout.server.extensions import store

from .form import SNVariantForm, SVariantForm

LOG = logging.getLogger(__name__)

ASSERTION_METHOD = "ACMG Guidelines, 2015"
ASSERTION_METHOD_CIT = "PMID:25741868"
SV_TYPES = [
    "Insertion",
    "Deletion",
    "Duplication",
    "Tandem duplication",
    "copy number loss",
    "copy number gain",
    "Inversion",
    "Translocation",
    "Complex",
]


def _get_var_tx_hgvs(variant_obj):
    """Retrieve all transcripts / hgvs for a given variant
    Args:
        variant_obj(scout.models.Variant)
    Returns:
        tx_hgvs_list(list) example: ["NM_000277 | c.1241A>G", ...]
    """
    tx_hgvs_list = []
    for gene in variant_obj.get("genes", []):
        for tx in gene.get("transcripts", []):
            if tx.get("refseq_id") and tx.get("coding_sequence_name"):
                for refseq in tx.get("refseq_identifiers"):
                    tx_hgvs_list.append(" | ".join([refseq, tx["coding_sequence_name"]]))

    return [(item, item) for item in tx_hgvs_list]


def _set_var_form_common_fields(var_form, variant_obj, case_obj):
    """Sets up fields for a variant form that are shared by SNVs and SVs

    Args:
        var_form(SNVariantForm or SVariantForm)
        variant_obj(scout.models.Variant)
    """
    var_form.local_id.data = variant_obj["_id"]
    var_form.linking_id.data = variant_obj["_id"]
    var_form.chromosome.data = variant_obj.get("chromosome")
    var_form.ref.data = variant_obj.get("reference")
    var_form.alt.data = variant_obj.get("alternative")
    var_form.gene_symbols.data = ",".join(variant_obj.get("hgnc_symbols", []))
    var_form.inheritance_models.choices = [(model, model) for model in CLINVAR_INHERITANCE_MODELS]
    var_form.clinsig.choices = [(term, term) for term in CLNSIG_TERMS]
    var_form.eval_date.data = datetime.now()
    var_form.assertion_method.data = ASSERTION_METHOD
    var_form.assertion_method_cit.data = ASSERTION_METHOD_CIT
    var_form.hpo_terms.choices = [
        (" - ".join([hpo.get("phenotype_id"), hpo.get("feature")]), hpo.get("phenotype_id"))
        for hpo in case_obj.get("phenotype_terms", [])
    ]
    var_form.omim_terms.choices = [
        (" - ".join([omim.get("disease_id"), omim.get("description")]), omim.get("disease_id"))
        for omim in case_obj.get("diagnosis_phenotypes", [])
    ]


def _get_snv_var_form(variant_obj, case_obj):
    """Sets up values for a SNV variant form
    Args:
        var_form(scout.server.blueprints.clinvar.form.SNVariantForm)
    """
    var_form = SNVariantForm()
    _set_var_form_common_fields(var_form, variant_obj, case_obj)
    var_form.tx_hgvs.choices = _get_var_tx_hgvs(variant_obj)
    var_form.dbsnp_id.data = variant_obj.get("dbsnp_id", "").split(";")[0]
    var_form.start.data = variant_obj.get("position")
    var_form.stop.data = variant_obj.get("position")
    return var_form


def _get_sv_var_form(variant_obj, case_obj):
    """Sets up values for a SV variant form

    Args:
        var_form(scout.server.blueprints.clinvar.form.SVariantForm)
    """
    var_form = SVariantForm()
    _set_var_form_common_fields(var_form, variant_obj, case_obj)
    var_form.sv_type.choices = [(type, type) for type in SV_TYPES]
    var_form.ref_copy_number.data = 2
    return var_form


def populate_variant_form(variant_obj, case_obj):
    """Populate the Flaskform associated to a variant"""
    if variant_obj["category"] in ["snv", "cancer"]:
        var_form = _get_snv_var_form(variant_obj, case_obj)
        var_form.category.data = "snv"

    elif variant_obj["category"] in ["sv", "cancer_sv"]:
        var_form = _get_sv_var_form(variant_obj, case_obj)
        var_form.category.data = "sv"

    return var_form


def set_clinvar_form(var_list, data):
    """Adds form key/values to the form used in ClinVar create submission page

    Args:
        var_list(list): list of variant _ids
        data(dict): data to show in clinvar_create.html template
    """
    data["variant_data"] = []  # {var_id: _id, var_obj: variant_obj, var_form: FlaskForm }
    # Loop over each variant present in var_list and create form fields for it
    for var_id in var_list:

        var_obj = store.variant(var_id)
        if not var_obj:
            continue

        var_form = populate_variant_form(var_obj, data["case"])
        var_form_item = {"var_id": var_id, "var_obj": var_obj, "var_form": var_form}
        data["variant_data"].append(var_form_item)
