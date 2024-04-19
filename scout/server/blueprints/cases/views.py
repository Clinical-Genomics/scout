# -*- coding: utf-8 -*-
import datetime
import json
import logging
import os.path
import shutil
from io import BytesIO
from operator import itemgetter
from typing import Generator, Optional, Union

from cairosvg import svg2png
from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    url_for,
)
from flask_login import current_user

from scout.constants import DATE_DAY_FORMATTER
from scout.server.blueprints.variants.controllers import activate_case
from scout.server.extensions import beacon, phenopacketapi, store
from scout.server.utils import (
    html_to_pdf_file,
    institute_and_case,
    jsonconverter,
    templated,
    user_cases,
    user_institutes,
    zip_dir_to_obj,
)
from scout.utils.gene import parse_raw_gene_ids, parse_raw_gene_symbols

from . import controllers

LOG = logging.getLogger(__name__)

cases_bp = Blueprint(
    "cases",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/cases/static",
)


@cases_bp.route("/institutes")
@templated("cases/index.html")
def index():
    """Display a list of all user institutes."""

    institutes_cases_count = []

    institute_ids_nr_cases: dict[str, int] = {
        item["_id"]["institute"]: item["count"] for item in user_cases(store, current_user)
    }  # Don't include institutes without cases

    for institute_obj in sorted(user_institutes(store, current_user), key=lambda d: d["_id"]):
        institute_id = institute_obj["_id"]
        if institute_id not in institute_ids_nr_cases:  # Institute doesn't have any case
            institutes_cases_count.append((institute_obj, 0))
        else:
            institutes_cases_count.append((institute_obj, institute_ids_nr_cases[institute_id]))

    return dict(institutes=institutes_cases_count)


@cases_bp.route("/<institute_id>/<case_name>")
@cases_bp.route("/case/case_id/<case_id>")
@templated("cases/case.html")
def case(
    case_name: Optional[str] = None,
    institute_id: Optional[str] = None,
    case_id: Optional[str] = None,
):
    """Display one case.
    Institute and display_name pairs uniquely specify a case.
    So do case_id, but we still call institute_and_case again to fetch institute
    and reuse its user access verification.
    """

    if case_id:
        case_obj = store.case(case_id=case_id, projection={"display_name": 1, "owner": 1})

        if not case_obj:
            flash("Case {} does not exist in database!".format(case_id))
            return abort(404)

        case_name = case_obj.get("display_name")
        institute_id = case_obj.get("owner")

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    if not case_obj:
        flash("Case {} does not exist in database!".format(case_name))
        return redirect(request.referrer)

    data = controllers.case(store, institute_obj, case_obj)

    return dict(
        **data,
    )


@cases_bp.route("/<institute_id>/<case_name>/sma", methods=["GET"])
@templated("cases/case_sma.html")
def sma(institute_id, case_name):
    """Visualize case SMA data - SMN CN calls"""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = controllers.sma_case(store, institute_obj, case_obj)

    activate_case(store, institute_obj, case_obj, current_user)

    return dict(format="html", **data)


@cases_bp.route("/<institute_id>/<case_name>/bionano", methods=["GET"])
@templated("cases/case_bionano.html")
def bionano(institute_id, case_name):
    """Visualize case BioNano data - FSHD calls"""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = controllers.bionano_case(store, institute_obj, case_obj)

    activate_case(store, institute_obj, case_obj, current_user)

    return dict(format="html", **data)


@cases_bp.route("/beacon_add_variants/<institute_id>/<case_name>", methods=["POST"])
def beacon_add_variants(institute_id, case_name):
    """Submit case variants to Beacon"""
    _, case_obj = institute_and_case(
        store, institute_id, case_name
    )  # This function checks if user has permissions to access the case
    beacon.add_variants(store, case_obj, request.form)
    return redirect(request.referrer)


@cases_bp.route("/beacon_remove_variants/<institute_id>/<case_name>", methods=["GET"])
def beacon_remove_variants(institute_id, case_name):
    """Remove all variants from a case from Beacon"""
    _, case_obj = institute_and_case(
        store, institute_id, case_name
    )  # This function checks if user has permissions to access the case
    beacon.remove_variants(store, institute_id, case_obj)
    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/mme_matches", methods=["GET", "POST"])
@templated("cases/matchmaker.html")
def matchmaker_matches(institute_id, case_name):
    """Show all MatchMaker matches for a given case"""

    data = controllers.matchmaker_matches(request, institute_id, case_name)
    return data


@cases_bp.route("/<institute_id>/<case_name>/mme_match/<target>", methods=["GET", "POST"])
def matchmaker_match(institute_id, case_name, target):
    """Starts an internal match or a match against one or all MME external nodes"""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    match_results = controllers.matchmaker_match(request, target, institute_id, case_name)
    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/mme_add", methods=["POST"])
def matchmaker_add(institute_id, case_name):
    """Add or update a case in MatchMaker"""
    # Call matchmaker_delete controller to add a patient to MatchMaker
    controllers.matchmaker_add(request, institute_id, case_name)
    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/mme_delete", methods=["POST"])
def matchmaker_delete(institute_id, case_name):
    """Remove a case from MatchMaker"""
    # Call matchmaker_delete controller to delete a patient from MatchMaker
    controllers.matchmaker_delete(request, institute_id, case_name)
    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/individuals", methods=["POST"])
def update_individual(institute_id, case_name):
    """Update individual data (age and/or Tissue type) for a case"""

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    ind_id = request.form.get("update_ind")
    age = request.form.get("_".join(["age", ind_id]))
    tissue = request.form.get("_".join(["tissue", ind_id]))
    controllers.update_individuals(
        store=store,
        institute_obj=institute_obj,
        case_obj=case_obj,
        user_obj=user_obj,
        ind=ind_id,
        age=age,
        tissue=tissue,
    )
    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/samples", methods=["POST"])
def update_cancer_sample(institute_id, case_name):
    """Update cancer sample-associated data: tumor purity, tissue type, tumor type"""

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    ind_id = request.form.get("update_ind")

    tumor_type = request.form.get(".".join(["tumor_type", ind_id]))
    tissue_type = request.form.get(".".join(["tissue_type", ind_id]))
    tumor_purity = request.form.get(".".join(["tumor_purity", ind_id]))

    controllers.update_cancer_samples(
        store=store,
        institute_obj=institute_obj,
        case_obj=case_obj,
        user_obj=user_obj,
        ind=ind_id,
        tissue=tissue_type,
        tumor_type=tumor_type,
        tumor_purity=tumor_purity,
    )
    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/synopsis", methods=["POST"])
def case_synopsis(institute_id, case_name):
    """Update (PUT) synopsis of a specific case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    new_synopsis = request.form.get("synopsis")
    controllers.update_synopsis(store, institute_obj, case_obj, user_obj, new_synopsis)
    return redirect(request.referrer)


@cases_bp.route("/api/v1/<institute_id>/<case_name>/case_report", methods=["GET"])
def api_case_report(institute_id, case_name):
    """API endpoint that returns case report json data"""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = controllers.case_report_content(
        store=store, institute_obj=institute_obj, case_obj=case_obj
    )
    return json.dumps({"data": data}, default=jsonconverter)


@cases_bp.route("/<institute_id>/<case_name>/case_report", methods=["GET"])
@templated("cases/case_report.html")
def case_report(institute_id, case_name):
    """Visualize case report."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = controllers.case_report_content(
        store=store, institute_obj=institute_obj, case_obj=case_obj
    )
    return dict(format="html", **data)


@cases_bp.route("/<institute_id>/<case_name>/pdf_report", methods=["GET"])
def pdf_case_report(institute_id, case_name):
    """Download a pdf report for a case"""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = controllers.case_report_content(
        store=store, institute_obj=institute_obj, case_obj=case_obj
    )
    # add coverage report on the bottom of this report
    if (
        current_app.config.get("SQLALCHEMY_DATABASE_URI")
        and case_obj.get("track", "rare") != "cancer"
    ):
        data["coverage_report"] = controllers.coverage_report_contents(
            request.url_root, institute_obj, case_obj
        )

    # Workaround to be able to print the case pedigree to pdf
    if case_obj.get("madeline_info") and case_obj.get("madeline_info") != "":
        try:
            write_to = os.path.join(cases_bp.static_folder, "madeline.png")
            svg2png(
                bytestring=case_obj["madeline_info"],
                write_to=write_to,
            )  # Transform to png, since PDFkit can't render svg images
            data["case"]["madeline_path"] = write_to
        except Exception as ex:
            LOG.error(
                f"Could not convert SVG pedigree figure {case_obj['madeline_info']} to PNG: {ex}"
            )

    html_report = render_template("cases/case_report.html", format="pdf", **data)

    bytes_file = html_to_pdf_file(
        html_string=html_report, orientation="portrait", dpi=300, zoom=0.6
    )
    file_name = "_".join(
        [
            case_obj["display_name"],
            datetime.datetime.now().strftime(DATE_DAY_FORMATTER),
            "scout_report.pdf",
        ]
    )
    return send_file(
        bytes_file,
        download_name=file_name,
        mimetype="application/pdf",
        as_attachment=True,
    )


@cases_bp.route("/<institute_id>/<case_name>/mt_report", methods=["GET"])
def mt_report(institute_id, case_name):
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)

    # create a temp folder to write excel files into
    temp_excel_dir = os.path.join(
        cases_bp.static_folder, "_".join([case_obj["display_name"], "mt_reports"])
    )
    os.makedirs(temp_excel_dir, exist_ok=True)

    if controllers.mt_excel_files(store, case_obj, temp_excel_dir):
        data = zip_dir_to_obj(temp_excel_dir)

        shutil.rmtree(temp_excel_dir)

        today = datetime.datetime.now().strftime(DATE_DAY_FORMATTER)
        return send_file(
            data,
            mimetype="application/zip",
            as_attachment=True,
            download_name="_".join(["scout", case_name, "MT_report", today]) + ".zip",
            max_age=0,
        )

    shutil.rmtree(temp_excel_dir)

    flash("No MT report excel file could be exported for this sample", "warning")
    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/diagnose", methods=["POST"])
def case_diagnosis(institute_id, case_name):
    """Add or remove a diagnosis for a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for(".case", institute_id=institute_id, case_name=case_name)

    disease_id = request.form["disease_term"].split("|")[0]
    affected_inds = request.form.getlist("affected_inds")  # Individual-level phenotypes

    store.diagnose(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        disease_id=disease_id.strip(),
        affected_inds=affected_inds,
        remove=True if request.args.get("remove") == "yes" else False,
    )
    return redirect("#".join([link, "disease_assign"]))


@cases_bp.route("/<institute_id>/<case_name>/phenotypes", methods=["POST"])
@cases_bp.route("/<institute_id>/<case_name>/phenotypes/<phenotype_id>", methods=["POST"])
def phenotypes(institute_id, case_name, phenotype_id=None):
    """Handle phenotypes."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    case_url = url_for(".case", institute_id=institute_id, case_name=case_name)
    is_group = request.args.get("is_group") == "yes"
    user_obj = store.user(current_user.email)

    if phenotype_id:
        # DELETE a phenotype item/group from case
        store.remove_phenotype(
            institute_obj, case_obj, user_obj, case_url, phenotype_id, is_group=is_group
        )
    else:
        try:
            # add a new phenotype item/group to the case
            hpo_term = None
            omim_term = None

            phenotype_term = request.form["hpo_term"]
            phenotype_inds = request.form.getlist("phenotype_inds")  # Individual-level phenotypes

            if phenotype_term.startswith("HP:") or len(phenotype_term) == 7:
                hpo_term = phenotype_term.split(" | ", 1)[0]
            else:
                omim_term = phenotype_term

            store.add_phenotype(
                institute=institute_obj,
                case=case_obj,
                user=user_obj,
                link=case_url,
                hpo_term=hpo_term,
                omim_term=omim_term,
                is_group=is_group,
                phenotype_inds=phenotype_inds,
            )
        except ValueError:
            flash(
                f"Unable to add phenotype for the given terms:{phenotype_term}",
                "warning",
            )
            return redirect(case_url)

    return redirect("#".join([case_url, "phenotypes_panel"]))


@cases_bp.route("/<institute_id>/<case_name>/phenotype_export", methods=["POST"])
def phenotype_export(institute_id, case_name):
    """Export phenopacket JSON for affected individual."""
    _, case_obj = institute_and_case(store, institute_id, case_name)
    case_url = url_for(".case", institute_id=institute_id, case_name=case_name)

    phenopacket_json = phenopacketapi.phenopacket_from_case(case_obj)

    if not phenopacket_json:
        return redirect("#".join([case_url, "phenotypes_panel"]))

    file_name = "_".join(
        [
            case_obj["display_name"],
            datetime.datetime.now().strftime(DATE_DAY_FORMATTER),
            "scout_phenopacket.json",
        ]
    )
    json_file = BytesIO(bytes(phenopacket_json, "utf-8"))

    return send_file(
        json_file,
        mimetype="application/json",
        as_attachment=True,
        download_name=file_name,
    )


@cases_bp.route("/<institute_id>/<case_name>/phenotype_import", methods=["POST"])
def phenotype_import(institute_id, case_name):
    """Import phenopacket JSON for affected individual."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    case_url = url_for(".case", institute_id=institute_id, case_name=case_name)
    phenopacket = None

    phenopacket_file = request.files["phenopacket_file"]
    phenopacket_hash = request.form.get("phenopacket_hash")

    if not phenopacket_file and not phenopacket_hash:
        flash("Please provide a phenotype file (json or hash format)", "warning")
        return redirect("#".join([case_url, "phenotypes_panel"]))

    try:
        if phenopacket_file:
            phenopacket = phenopacketapi.file_import(phenopacket_file)

        if phenopacket_hash:
            phenopacket = phenopacketapi.get_hash(phenopacket_hash)

        phenopacketapi.add_phenopacket_to_case(
            store, institute_obj, case_obj, user_obj, case_url, phenopacket
        )
        return redirect("#".join([case_url, "phenotypes_panel"]))

    except Exception as ex:
        flash(f"An error occurred while retrieving Phenopacket info: {ex}", "warning")
        return redirect(case_url)


@cases_bp.route("/<institute_id>/<case_name>/phenotypes/actions", methods=["POST"])
def phenotypes_actions(institute_id, case_name):
    """Perform actions on multiple phenotypes."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    case_url = url_for(".case", institute_id=institute_id, case_name=case_name)
    action = request.form["action"]
    hpo_ids = request.form.getlist("hpo_id")
    user_obj = store.user(current_user.email)

    if action == "PHENOMIZER":
        diseases = controllers.phenomizer_diseases(hpo_ids, case_obj)
        if diseases:
            return render_template(
                "cases/diseases.html",
                diseases=diseases,
                institute=institute_obj,
                case=case_obj,
            )

    if action == "DELETE":
        for hpo_id in hpo_ids:
            # DELETE a phenotype from the list
            store.remove_phenotype(institute_obj, case_obj, user_obj, case_url, hpo_id)

    if action == "ADDGENE":
        try:
            hgnc_ids = parse_raw_gene_ids(request.form.getlist("genes"))
        except ValueError:
            flash(
                "Provided gene info could not be parsed!. Please allow autocompletion to finish.",
                "warning",
            )
        store.update_dynamic_gene_list(case_obj, hgnc_ids=list(hgnc_ids), add_only=True)

    if action == "REMOVEGENES":  # Remove one or more genes from the dynamic gene list
        case_dynamic_genes = [dyn_gene["hgnc_id"] for dyn_gene in case_obj.get("dynamic_gene_list")]
        genes_to_remove = [int(gene_id) for gene_id in request.form.getlist("dynamicGene")]
        store.update_dynamic_gene_list(
            case_obj,
            hgnc_ids=list(set(case_dynamic_genes) - set(genes_to_remove)),
            delete_only=True,
        )

    if action == "GENES":
        hgnc_symbols = parse_raw_gene_symbols(request.form.getlist("genes"))
        store.update_dynamic_gene_list(case_obj, hgnc_symbols=list(hgnc_symbols))

    if action == "GENERATE":
        results = store.generate_hpo_gene_list(*hpo_ids)
        # determine how many HPO terms each gene must match
        hpo_count = int(request.form.get("min_match") or 1)
        hgnc_ids = [result[0] for result in results if result[1] >= hpo_count]
        store.update_dynamic_gene_list(case_obj, hgnc_ids=hgnc_ids, phenotype_ids=hpo_ids)

    return redirect("#".join([case_url, "phenotypes_panel"]))


@cases_bp.route("/<institute_id>/<case_name>/events", methods=["POST"])
@cases_bp.route("/<institute_id>/<case_name>/events/<event_id>", methods=["POST"])
def events(institute_id, case_name, event_id=None):
    """Handle events."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    link = request.form.get("link")
    content = request.form.get("content")
    variant_id = request.args.get("variant_id")
    user_obj = store.user(current_user.email)
    if event_id:
        if "remove" in request.form:
            # delete the event
            store.delete_event(event_id)
        elif "edit" in request.form:
            # edit comment
            store.update_comment(
                comment_id=event_id,
                new_content=request.form.get("updatedContent"),
                level=request.form.get("level", "specific"),
            )
    else:
        if variant_id:
            # create a variant comment
            variant_obj = store.variant(variant_id)
            level = request.form.get("level", "specific")
            store.comment(
                institute_obj,
                case_obj,
                user_obj,
                link,
                variant=variant_obj,
                content=content,
                comment_level=level,
            )
        else:
            # create a case comment
            store.comment(institute_obj, case_obj, user_obj, link, content=content)

    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/status", methods=["POST"])
def status(institute_id, case_name):
    """Update status of a specific case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)

    status = request.form.get("status", case_obj["status"])
    link = url_for(".case", institute_id=institute_id, case_name=case_name)

    if status == "archived":
        store.archive_case(institute_obj, case_obj, user_obj, link)
    else:
        store.update_status(institute_obj, case_obj, user_obj, status, link)

    tags = request.form.getlist("tags")
    if tags or case_obj.get("tags") and tags != case_obj.get("tags"):
        store.tag_case(institute_obj, case_obj, user_obj, tags, link)

    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/assign", methods=["POST"])
@cases_bp.route("/<institute_id>/<case_name>/<user_id>/<inactivate>/assign", methods=["POST"])
def assign(institute_id, case_name, user_id=None, inactivate=False):
    """Assign and unassign a user from a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    link = url_for(".case", institute_id=institute_id, case_name=case_name)
    if user_id:
        user_obj = store.user(user_id=user_id)
    else:
        user_obj = store.user(email=current_user.email)
    if request.form.get("action") == "DELETE":
        store.unassign(institute_obj, case_obj, user_obj, link, inactivate)
    else:
        store.assign(institute_obj, case_obj, user_obj, link)
    return redirect(request.referrer)


@cases_bp.route("/api/v1/cases", defaults={"institute_id": None})
@cases_bp.route("/api/v1/<institute_id>/cases")
def caselist(institute_id):
    """Search for cases for autocompletion"""
    query = request.args.get("query")
    if query is None:
        return abort(500)

    matching_cases = store.cases(owner=institute_id, name_query="case:" + query)
    display_names = []
    if institute_id:  # called from case page, where institute_id is provided
        display_names = sorted([case["display_name"] for case in matching_cases])
    else:  # called from gene panel page, where institute_id is NOT provided
        user_institutes_ids = [inst["_id"] for inst in user_institutes(store, current_user)]
        display_names = sorted(
            [
                " - ".join([case["owner"], case["display_name"]])
                for case in matching_cases
                if case["owner"] in user_institutes_ids
            ]
        )
    json_terms = [{"name": "{}".format(display_name)} for display_name in display_names]

    return jsonify(json_terms)


@cases_bp.route("/api/v1/hpo-terms")
def hpoterms():
    """Search for HPO terms."""
    query = request.args.get("query")
    if query is None:
        return abort(500)
    terms = sorted(store.hpo_terms(query=query), key=itemgetter("hpo_number"))
    json_terms = [
        {"name": "{} | {}".format(term["_id"], term["description"]), "id": term["_id"]}
        for term in terms[:7]
    ]

    return jsonify(json_terms)


@cases_bp.route("/api/v1/disease-terms")
def diseaseterms():
    query = request.args.get("query")
    source = request.args.get("source") or None
    if query is None:
        return abort(500)
    terms = store.query_disease(query=query, source=source)
    json_terms = [
        {"name": "{} | {}".format(term["_id"], term["description"]), "id": term["_id"]}
        for term in terms[:7]
    ]
    return jsonify(json_terms)


@cases_bp.route("/<institute_id>/<case_name>/<variant_id>/pin", methods=["POST"])
def pin_variant(institute_id, case_name, variant_id):
    """Pin and unpin variants to/from the list of suspects."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    user_obj = store.user(current_user.email)
    link = url_for(
        "variant.variant",
        institute_id=institute_id,
        case_name=case_name,
        variant_id=variant_id,
    )
    if request.form["action"] == "ADD":
        store.pin_variant(institute_obj, case_obj, user_obj, link, variant_obj)
    elif request.form["action"] == "DELETE":
        store.unpin_variant(institute_obj, case_obj, user_obj, link, variant_obj)
    return redirect(request.referrer or link)


@cases_bp.route("/<institute_id>/<case_name>/<variant_id>/validate", methods=["POST"])
def mark_validation(institute_id, case_name, variant_id):
    """Mark a variant as sanger validated."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    user_obj = store.user(current_user.email)
    validate_type = request.form["type"] or None
    link = url_for(
        "variant.variant",
        institute_id=institute_id,
        case_name=case_name,
        variant_id=variant_id,
    )
    store.validate(institute_obj, case_obj, user_obj, link, variant_obj, validate_type)
    return redirect(request.referrer or link)


@cases_bp.route(
    "/<institute_id>/<case_name>/<variant_id>/<partial_causative>/causative",
    methods=["POST"],
)
def mark_causative(institute_id, case_name, variant_id, partial_causative=False):
    """Mark a variant as confirmed causative."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    user_obj = store.user(current_user.email)
    link = url_for(
        "variant.variant",
        institute_id=institute_id,
        case_name=case_name,
        variant_id=variant_id,
    )
    if request.form["action"] == "ADD":
        if "partial_causative" in request.form:
            omim_terms = request.form.getlist("omim_select")
            hpo_terms = request.form.getlist("hpo_select")
            store.mark_partial_causative(
                institute_obj,
                case_obj,
                user_obj,
                link,
                variant_obj,
                omim_terms,
                hpo_terms,
            )
        else:
            store.mark_causative(institute_obj, case_obj, user_obj, link, variant_obj)
        if "tags" in request.form:
            tags = request.form.getlist("tags")
            store.tag_case(institute_obj, case_obj, user_obj, tags, link)
    elif request.form["action"] == "DELETE":
        if partial_causative == "True":
            store.unmark_partial_causative(institute_obj, case_obj, user_obj, link, variant_obj)
        else:
            store.unmark_causative(institute_obj, case_obj, user_obj, link, variant_obj)

    # send the user back to the case that was marked as solved
    case_url = url_for(".case", institute_id=institute_id, case_name=case_name)
    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/check-case", methods=["POST"])
def check_case(institute_id, case_name):
    """Mark a case that is has been checked.
    This means to set case['needs_check'] to False
    """
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"needs_check": False}}
    )
    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/report/<report_type>")
def custom_report(institute_id, case_name, report_type):
    """Display/download a custom report for a case"""

    report_path = None
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    date_str = request.args.get("date")  # Provided only when downloading old delivery reports
    if date_str is None:
        report_path = case_obj.get(report_type)
    else:
        for analysis_data in case_obj.get("analyses", []):
            if str(analysis_data["date"].date()) == date_str:
                report_path = analysis_data["delivery_report"]

    if report_path is None:
        return abort(404)

    out_dir = os.path.abspath(os.path.dirname(report_path))
    filename = os.path.basename(report_path)

    if request.args.get("report_format") == "pdf":
        try:
            with open(os.path.abspath(report_path), "r") as html_file:
                source_code = html_file.read()

                if filename.endswith(".yaml") or filename.endswith(".yml"):
                    source_code = "<html><code><pre>" + source_code + "</pre></code></html>"

                bytes_file = html_to_pdf_file(source_code, "landscape", 300)
                file_name = "_".join(
                    [
                        case_obj["display_name"],
                        datetime.datetime.now().strftime(DATE_DAY_FORMATTER),
                        ".".join([report_type, "pdf"]),
                    ]
                )
                return send_file(
                    bytes_file,
                    download_name=file_name,
                    mimetype="application/pdf",
                    as_attachment=True,
                )
        except Exception as ex:
            flash(
                "An error occurred while converting report to PDF: {} -- {}".format(
                    report_type, ex
                ),
                "warning",
            )
            LOG.error(ex)

    return send_from_directory(out_dir, filename)


@cases_bp.route("/<institute_id>/<case_name>/share", methods=["POST"])
def share(institute_id, case_name):
    """Share a case with a different institute."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    collaborator_id = request.form["collaborator"]
    revoke_access = "revoke" in request.form
    link = url_for(".case", institute_id=institute_id, case_name=case_name)

    try:
        if revoke_access:
            store.unshare(institute_obj, case_obj, collaborator_id, user_obj, link)
        else:
            store.share(institute_obj, case_obj, collaborator_id, user_obj, link)
    except ValueError as ex:
        flash(str(ex), "warning")

    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/update_rerun_status")
def update_rerun_status(institute_id, case_name):
    """Update rerun status for a case by setting rerun_requested to True or False"""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for("cases.case", institute_id=institute_id, case_name=case_name)

    store.update_rerun_status(institute_obj, case_obj, user_obj, link)
    return redirect(link)


@cases_bp.route("/<institute_id>/<case_name>/monitor", methods=["POST"])
def rerun_monitor(institute_id, case_name):
    """Request a case to be monitored for future reruns."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for(".case", institute_id=institute_id, case_name=case_name)
    if request.form.get("rerun_monitoring") == "monitor":
        store.monitor(institute_obj, case_obj, user_obj, link)
    else:
        store.unmonitor(institute_obj, case_obj, user_obj, link)

    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/reanalysis", methods=["POST"])
def reanalysis(institute_id, case_name):
    """Toggle a rerun by making a call to RERUNNER service."""

    edited_metadata = json.loads(request.form.get("sample_metadata"))
    try:
        controllers.call_rerunner(store, institute_id, case_name, edited_metadata)

    except Exception as err:
        msg = f"Error processing request: {err.__class__.__name__} - {str(err)}"
        LOG.error(msg)
        flash(msg, "danger")

    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/research", methods=["POST"])
def research(institute_id, case_name):
    """Open the research list for a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for(".case", institute_id=institute_id, case_name=case_name)
    store.open_research(institute_obj, case_obj, user_obj, link)
    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/reset_research", methods=["GET"])
def reset_research(institute_id, case_name):
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for(".case", institute_id=institute_id, case_name=case_name)
    store.reset_research(institute_obj, case_obj, user_obj, link)
    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/cohorts", methods=["POST"])
def cohorts(institute_id, case_name):
    """Add/remove institute tags."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for(".case", institute_id=institute_id, case_name=case_name)
    cohort_tag = request.form["cohort_tag"]
    if request.args.get("remove") == "yes":
        store.remove_cohort(institute_obj, case_obj, user_obj, link, cohort_tag)
    else:
        store.add_cohort(institute_obj, case_obj, user_obj, link, cohort_tag)
    return redirect("#".join([request.referrer, "cohorts"]))


@cases_bp.route("/<institute_id>/<case_name>/default-panels", methods=["POST"])
def default_panels(institute_id, case_name):
    """Update default panels for a case."""
    panel_ids = request.form.getlist("panel_ids")
    controllers.update_default_panels(store, current_user, institute_id, case_name, panel_ids)
    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/update-clinical-filter-hpo", methods=["POST"])
def update_clinical_filter_hpo(institute_id, case_name):
    """Update default panels for a case."""
    hpo_clinical_filter = request.form.get("hpo_clinical_filter")
    controllers.update_clinical_filter_hpo(
        store, current_user, institute_id, case_name, hpo_clinical_filter
    )
    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/add_case_group", methods=["GET", "POST"])
def add_case_group(institute_id, case_name):
    """Add a new case group for an institute and bind it in selected case.

    GET request (with no group_id) requests init of a new group
    POST request adds other_case_name to the group
    """
    group_id = request.form.get("group_id", None)
    if request.method == "POST":
        case_name = request.form.get("other_case_name")

    controllers.add_case_group(store, current_user, institute_id, case_name, group_id)

    return redirect(request.referrer + "#case_groups")


@cases_bp.route("/<institute_id>/<case_name>/<case_group>/remove_case_group", methods=["GET"])
def remove_case_group(institute_id, case_name, case_group):
    """Unbind a case group from a case. Remove the group if it is no longer in use."""
    controllers.remove_case_group(store, current_user, institute_id, case_name, case_group)

    return redirect(request.referrer + "#case_groups")


@cases_bp.route("/<case_group>/case_group_update_label", methods=["POST"])
def case_group_update_label(case_group):
    """Unbind a case group from a case. Remove the group if it is no longer in use."""
    label = request.form.get("label", "unlabeled")

    controllers.case_group_update_label(store, case_group, label)

    return redirect(request.referrer + "#case_groups")


@cases_bp.route("/<institute_id>/<case_name>/download-hpo-genes/<category>", methods=["GET"])
def download_hpo_genes(institute_id, case_name, category):
    """Download the genes contained in a case dynamic gene list

    Args:
        institute_id(str):  id for current institute
        case_name(str):     name for current case
        category(str):      variant category - "clinical" or "research"
                            "research" retrieves all gene symbols for each HPO term on the dynamic phenotype panel
                            "clinical" limits dynamic phenotype panel retrieval to genes present on case clinical genes
    """

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    # Create export object consisting of dynamic phenotypes with associated genes as a dictionary
    is_clinical = category != "research"
    phenotype_terms_with_genes = controllers.phenotypes_genes(store, case_obj, is_clinical)
    html_content = ""
    for term_id, term in phenotype_terms_with_genes.items():
        html_content += f"<hr><strong>{term_id} - {term.get('description')}</strong><br><br><font style='font-size:16px;'><i>{term.get('genes')}</i></font><br><br>"

    bytes_file = html_to_pdf_file(html_content, "portrait", 300)
    file_name = "_".join(
        [
            case_obj["display_name"],
            datetime.datetime.now().strftime(DATE_DAY_FORMATTER),
            category,
            "dynamic_phenotypes.pdf",
        ]
    )
    return send_file(
        bytes_file,
        download_name=file_name,
        mimetype="application/pdf",
        as_attachment=True,
    )


@cases_bp.route("/<institute_id>/<case_name>/<individual_id>/cgh")
def vcf2cytosure(institute_id, case_name, individual_id):
    """Download vcf2cytosure file for individual."""

    (display_name, vcf2cytosure) = controllers.vcf2cytosure(
        store, institute_id, case_name, individual_id
    )
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    outdir = os.path.abspath(os.path.dirname(vcf2cytosure))
    filename = os.path.basename(vcf2cytosure)
    download_name = ".".join(
        [display_name, case_obj["display_name"], case_obj["_id"], "vcf2cytosure.cgh"]
    )
    LOG.debug("Attempt to deliver file {0} from dir {1}".format(download_name, outdir))
    return send_from_directory(outdir, filename, download_name=download_name, as_attachment=True)


@cases_bp.route(
    "/<institute_id>/<case_name>/<individual>/upd_regions_images/<image>",
    methods=["GET", "POST"],
)
def host_upd_regions_image(institute_id, case_name, individual, image):
    """Generate UPD REGIONS image file paths"""
    return host_image_aux(institute_id, case_name, individual, image, "upd_regions")


@cases_bp.route(
    "/<institute_id>/<case_name>/<individual>/upd_sites_images/<image>",
    methods=["GET", "POST"],
)
def host_upd_sites_image(institute_id, case_name, individual, image):
    """Generate UPD image file paths"""
    return host_image_aux(institute_id, case_name, individual, image, "upd_sites")


@cases_bp.route(
    "/<institute_id>/<case_name>/<individual>/coverage_images/<image>",
    methods=["GET", "POST"],
)
def host_coverage_image(institute_id, case_name, individual, image):
    """Generate Coverage image file paths"""
    return host_image_aux(institute_id, case_name, individual, image, "coverage")


@cases_bp.route(
    "/<institute_id>/<case_name>/<individual>/autozygous_images/<image>",
    methods=["GET", "POST"],
)
def host_autozygous_image(institute_id, case_name, individual, image):
    """Generate Coverage image file paths"""
    return host_image_aux(institute_id, case_name, individual, image, "autozygous")


@cases_bp.route(
    "/<institute_id>/<case_name>/<individual>/ideograms/<image>",
    methods=["GET", "POST"],
)
def host_chr_image(institute_id, case_name, individual, image):
    """Generate CHR image file paths. Points to servers 'public/static'"""
    public_folder = "/public/static/ideograms/"
    img_path = public_folder + image
    LOG.debug("ideaogram: {}".format(img_path))
    return send_from_directory(img_path, image)


def host_image_aux(institute_id, case_name, individual, image, key):
    """Auxiliary function for generate absolute file paths"""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    # Find path
    for ind in case_obj["individuals"]:
        if ind["individual_id"] == individual:
            # LOG.debug("ind host_image_aux: {}".format(ind))
            try:
                # path contains both dir structure and a file prefix
                path = ind["chromograph_images"][key]
                abs_path = os.path.abspath(path)
                img_path = abs_path + image.split("-")[-1]  # get suffix
                return send_file(img_path)
            except Exception as err:
                # redirect to missing file icon upon error
                LOG.warning("send_file() exception: {}".format(err))
                return redirect("/public/static/file-earmark-x.svg")


@cases_bp.route("/<institute_id>/<case_name>/custom_images")
def host_custom_image_aux(institute_id: str, case_name: str) -> Optional[Response]:
    """Adds absolute path to a custom image path and returns the image."""

    def custom_images_paths(d: Union[dict, list]) -> Generator:
        """returns all paths saved under custom images for a case - both case images and variant images."""
        for v in d.values():
            if isinstance(v, dict):
                yield from custom_images_paths(v)
            elif isinstance(v, list):
                for image in v:
                    yield image.get("path")

    _, case_obj = institute_and_case(store, institute_id, case_name)
    custom_images_values: list = list(custom_images_paths(case_obj.get("custom_images", {})))
    if request.args.get("image_path") in custom_images_values:
        abs_path: str = os.path.abspath(request.args.get("image_path"))
        return send_file(abs_path)


def _generate_csv(header, lines):
    """Download a text file composed of any header and lines"""
    yield header + "\n"
    for line in lines:  # lines have already quoted fields
        yield line + "\n"
