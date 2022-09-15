import logging
from datetime import datetime

from scout.constants.clinvar import VARIANT_FIELDS
from scout.models.clinvar import clinvar_casedata, clinvar_variant
from scout.server.extensions import store

from .form import CaseDataForm, SNVariantForm, SVariantForm

LOG = logging.getLogger(__name__)


def _get_var_tx_hgvs(variant_obj):
    """Retrieve all transcripts / hgvs for a given variant
    Args:
        variant_obj(scout.models.Variant)
    Returns:
        list. example: ["NM_000277 | c.1241A>G", ...]
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
        variant_obj(dict) scout.models.Variant
        case_obj(dict) scout.models.Case
    """
    var_form.local_id.data = variant_obj["_id"]
    var_form.linking_id.data = variant_obj["_id"]
    var_form.chromosome.data = variant_obj.get("chromosome")
    var_form.ref.data = variant_obj.get("reference")
    var_form.alt.data = variant_obj.get("alternative")
    var_form.gene_symbols.data = ",".join(variant_obj.get("hgnc_symbols", []))
    var_form.last_evaluated.data = datetime.now()
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
        variant_obj(dict) scout.models.Variant
        case_obj(dict) scout.models.Case

    Returns:
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
        variant_obj(dict) scout.models.Variant
        case_obj(dict) scout.models.Case

    Returns:
        var_form(scout.server.blueprints.clinvar.form.SVariantForm)
    """
    var_form = SVariantForm()
    _set_var_form_common_fields(var_form, variant_obj, case_obj)
    var_form.ref_copy_number.data = 2
    return var_form


def _populate_variant_form(variant_obj, case_obj):
    """Populate the Flaskform associated to a variant

    Args:
        variant_obj(dict) scout.models.Variant
        case_obj(dict) scout.models.Case

    Return:
        var_form(scout.server.blueprints.clinvar.form.SVariantForm or
                 scout.server.blueprints.clinvar.form.SNVariantForm )

    """
    if variant_obj["category"] in ["snv", "cancer"]:
        var_form = _get_snv_var_form(variant_obj, case_obj)
        var_form.category.data = "snv"

    elif variant_obj["category"] in ["sv", "cancer_sv"]:
        var_form = _get_sv_var_form(variant_obj, case_obj)
        var_form.category.data = "sv"

    return var_form


def _populate_case_data_form(variant_obj, case_obj):
    """Loop over the individuals of the case and populate a CaseDataForm for each one of them

    Args:
        variant_obj(dict) scout.models.Variant
        case_obj(dict) scout.models.Case

    Returns:
        cdata_form_list(list) list of scout.server.blueprints.clinvar.form.CaseDataForm

    """
    cdata_form_list = []  # A list of CaseData forms, one for each case individual/sample
    for ind in case_obj.get("individuals", []):
        affected = ind.get("phenotype") == 2
        ind_form = CaseDataForm()
        ind_form.affected_status.data = "yes" if affected else "no"
        ind_form.include_ind.data = affected
        ind_form.individual_id.data = ind.get("display_name")
        ind_form.linking_id.data = variant_obj["_id"]
        cdata_form_list.append(ind_form)
    return cdata_form_list


def set_clinvar_form(var_id, data):
    """Adds form key/values to the form used in ClinVar create submission page

    Args:
        var_id(str): variant _id
        data(dict): data to show in clinvar_create.html template
    """
    var_obj = store.variant(var_id)
    if not var_obj:
        return
    var_form = _populate_variant_form(var_obj, data["case"])  # variant-associated form
    cdata_forms = _populate_case_data_form(var_obj, data["case"])  # CaseData form
    variant_data = {
        "var_id": var_id,
        "var_obj": var_obj,
        "var_form": var_form,
        "cdata_forms": cdata_forms,
    }
    data["variant_data"] = variant_data


def parse_variant_form_fields(form):
    """Parses input values provided by the user in the ClinVar add_one form
       and creates a Variant ClinVar dictionary to be saved in database (clinvar collection)

    Args:
        form(werkzeug.datastructures.ImmutableMultiDic): form submitted by a user

    Returns:
        clinvar_var(dict): scout.models.clinvar.clinvar_variant
    """
    clinvar_var = {"csv_type": "variant"}
    # Set values in clinvar_var
    for key in clinvar_variant:
        if key in form:
            clinvar_var[key] = form[key]
        elif form.get("dbsnp_id"):
            clinvar_var["variations_ids"] = form["dbsnp_id"]
        else:
            LOG.error(key)

    LOG.warning(clinvar_var)

    return clinvar_var


def parse_casedata_form_fields(form):
    """Parses input values provided by the user in the ClinVar add_one form
      and creates a Variant ClinVar dictionary to be saved in database (clinvar collection)

    Args:
        form(werkzeug.datastructures.ImmutableMultiDic): form submitted by a user

    Returns:
        clinvar_cd(dict): scout.models.clinvar.clinvar_casedata
    """
    clinvar_cd = {"csv_type": "casedata"}
