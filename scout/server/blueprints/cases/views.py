# -*- coding: utf-8 -*-
import datetime
import io
import logging
import os.path
import pathlib
import re
import shutil
import zipfile
from operator import itemgetter

import pymongo
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    Response,
    url_for,
)

from flask_login import current_user
from flask_weasyprint import HTML, render_pdf
from werkzeug.datastructures import Headers

from scout.constants import SAMPLE_SOURCE
from scout.server.extensions import mail, store
from scout.server.utils import institute_and_case, templated, user_institutes

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
    institute_objs = user_institutes(store, current_user)
    institutes_count = (
        (institute_obj, sum(1 for i in store.cases(collaborator=institute_obj["_id"])))
        for institute_obj in institute_objs
        if institute_obj
    )
    return dict(institutes=institutes_count)


@cases_bp.route("/<institute_id>/<case_name>")
@templated("cases/case.html")
def case(institute_id, case_name):
    """Display one case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    if not case_obj:
        flash("Case {} does not exist in database!".format(case_name))
        return redirect(request.referrer)

    data = controllers.case(store, institute_obj, case_obj)
    return dict(
        institute=institute_obj,
        case=case_obj,
        mme_nodes=current_app.mme_nodes,
        tissue_types=SAMPLE_SOURCE,
        **data,
    )


@cases_bp.route("/<institute_id>/<case_name>/sma", methods=["GET"])
@templated("cases/case_sma.html")
def sma(institute_id, case_name):
    """Visualize case SMA data - SMN CN calls"""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = controllers.case(store, institute_obj, case_obj)
    return dict(institute=institute_obj, case=case_obj, format="html", **data)


@cases_bp.route("/beacon_submit", methods=["POST"])
def beacon_submit():
    """Submit case variants to Beacon"""

    controllers.beacon_add(request.form)
    return redirect(request.referrer)


@cases_bp.route("/beacon_remove/<case_id>", methods=["GET"])
def beacon_remove(case_id):
    """Remove all variants from a case from Beacon"""

    controllers.beacon_remove(case_id)
    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/mme_matches", methods=["GET", "POST"])
@templated("cases/matchmaker.html")
def matchmaker_matches(institute_id, case_name):
    """Show all MatchMaker matches for a given case"""
    # check that only authorized users can access MME patients matches
    panel = 1
    if request.method == "POST":
        panel = request.form.get("pane_id")
    user_obj = store.user(current_user.email)
    if "mme_submitter" not in user_obj["roles"]:
        flash("unauthorized request", "warning")
        return redirect(request.referrer)
    # Required params for getting matches from MME server:
    mme_base_url = current_app.config.get("MME_URL")
    mme_token = current_app.config.get("MME_TOKEN")
    if not mme_base_url or not mme_token:
        flash(
            "An error occurred reading matchmaker connection parameters. Please check config file!",
            "danger",
        )
        return redirect(request.referrer)
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = controllers.mme_matches(case_obj, institute_obj, mme_base_url, mme_token)
    data["panel"] = panel
    if data and data.get("server_errors"):
        flash("MatchMaker server returned error:{}".format(data["server_errors"]), "danger")
        return redirect(request.referrer)
    if not data:
        data = {"institute": institute_obj, "case": case_obj, "panel": panel}
    return data


@cases_bp.route("/<institute_id>/<case_name>/mme_match/<target>", methods=["GET", "POST"])
def matchmaker_match(institute_id, case_name, target):
    """Starts an internal match or a match against one or all MME external nodes"""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)

    # check that only authorized users can run matches
    user_obj = store.user(current_user.email)
    if "mme_submitter" not in user_obj["roles"]:
        flash("unauthorized request", "warning")
        return redirect(request.referrer)

    # Required params for sending an add request to MME:
    mme_base_url = current_app.config.get("MME_URL")
    mme_accepts = current_app.config.get("MME_ACCEPTS")
    mme_token = current_app.config.get("MME_TOKEN")
    nodes = current_app.mme_nodes

    if not mme_base_url or not mme_token or not mme_accepts:
        flash(
            "An error occurred reading matchmaker connection parameters. Please check config file!",
            "danger",
        )
        return redirect(request.referrer)

    match_results = controllers.mme_match(
        case_obj, target, mme_base_url, mme_token, nodes, mme_accepts
    )
    ok_responses = 0
    for match_results in match_results:
        if match_results["status_code"] == 200:
            ok_responses += 1
    if ok_responses:
        flash("Match request sent. Look for eventual matches in 'Matches' page.", "info")
    else:
        flash("An error occurred while sending match request.", "danger")

    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/mme_add", methods=["POST"])
def matchmaker_add(institute_id, case_name):
    """Add or update a case in MatchMaker"""

    # check that only authorized users can add patients to MME
    user_obj = store.user(current_user.email)
    if "mme_submitter" not in user_obj["roles"]:
        flash("unauthorized request", "warning")
        return redirect(request.referrer)

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    causatives = False
    features = False
    if case_obj.get("suspects") and len(case_obj.get("suspects")) > 3:
        flash(
            "At the moment it is not possible to save to MatchMaker more than 3 pinned variants",
            "warning",
        )
        return redirect(request.referrer)
    if case_obj.get("suspects"):
        causatives = True
    if case_obj.get("phenotype_terms"):
        features = True

    mme_save_options = ["sex", "features", "disorders"]
    for index, item in enumerate(mme_save_options):
        if item in request.form:
            LOG.info("item {} is in request form".format(item))
            mme_save_options[index] = True
        else:
            mme_save_options[index] = False
    genomic_features = request.form.get("genomicfeatures")
    genes_only = True  # upload to matchmaker only gene names
    if genomic_features == "variants":
        genes_only = False  # upload to matchmaker both variants and gene names

    # If there are no genomic features nor HPO terms to share for this case, abort
    if (not case_obj.get("suspects") and not mme_save_options[1]) or (
        causatives is False and features is False
    ):
        flash(
            "In order to upload a case to MatchMaker you need to pin a variant or at least assign a phenotype (HPO term)",
            "danger",
        )
        return redirect(request.referrer)

    user_obj = store.user(current_user.email)

    # Required params for sending an add request to MME:
    mme_base_url = current_app.config.get("MME_URL")
    mme_accepts = current_app.config.get("MME_ACCEPTS")
    mme_token = current_app.config.get("MME_TOKEN")

    if not mme_base_url or not mme_accepts or not mme_token:
        flash(
            "An error occurred reading matchmaker connection parameters. Please check config file!",
            "danger",
        )
        return redirect(request.referrer)

    add_result = controllers.mme_add(
        store=store,
        user_obj=user_obj,
        case_obj=case_obj,
        add_gender=mme_save_options[0],
        add_features=mme_save_options[1],
        add_disorders=mme_save_options[2],
        genes_only=genes_only,
        mme_base_url=mme_base_url,
        mme_accepts=mme_accepts,
        mme_token=mme_token,
    )

    # flash MME responses (one for each patient posted)
    n_succes_response = 0
    n_inserted = 0
    n_updated = 0
    category = "warning"

    for resp in add_result["server_responses"]:
        message = resp.get("message")
        if resp.get("status_code") == 200:
            n_succes_response += 1
        else:
            flash(
                "an error occurred while adding patient to matchmaker: {}".format(message),
                "warning",
            )
        if message == "Patient was successfully updated.":
            n_updated += 1
        if message == "Patient was successfully inserted into database.":
            n_inserted += 1

    # if at least one patient was inserted or updated into matchmaker, save submission at the case level:
    if n_inserted or n_updated:
        category = "success"
        store.case_mme_update(case_obj=case_obj, user_obj=user_obj, mme_subm_obj=add_result)
    flash(
        "Number of new patients in matchmaker:{0}, number of updated records:{1}, number of failed requests:{2}".format(
            n_inserted, n_updated, len(add_result.get("server_responses")) - n_succes_response
        ),
        category,
    )

    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/mme_delete", methods=["POST"])
def matchmaker_delete(institute_id, case_name):
    """Remove a case from MatchMaker"""

    # check that only authorized users can delete patients from MME
    user_obj = store.user(current_user.email)
    if "mme_submitter" not in user_obj["roles"]:
        flash("unauthorized request", "warning")
        return redirect(request.referrer)

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    # Required params for sending a delete request to MME:
    mme_base_url = current_app.config.get("MME_URL")
    mme_token = current_app.config.get("MME_TOKEN")
    if not mme_base_url or not mme_token:
        flash(
            "An error occurred reading matchmaker connection parameters. Please check config file!",
            "danger",
        )
        return redirect(request.referrer)

    delete_result = controllers.mme_delete(case_obj, mme_base_url, mme_token)

    n_deleted = 0
    category = "warning"

    for resp in delete_result:
        if resp["status_code"] == 200:
            n_deleted += 1
        else:
            flash(resp["message"], category)
    if n_deleted:
        category = "success"
        # update case by removing mme submission
        # and create events for patients deletion from MME
        user_obj = store.user(current_user.email)
        store.case_mme_delete(case_obj=case_obj, user_obj=user_obj)
    flash(
        "Number of patients deleted from Matchmaker: {} out of {}".format(
            n_deleted, len(delete_result)
        ),
        category,
    )
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


@cases_bp.route("/<institute_id>/<case_name>/case_report", methods=["GET"])
@templated("cases/case_report.html")
def case_report(institute_id, case_name):
    """Visualize case report"""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = controllers.case_report_content(store, institute_obj, case_obj)
    return dict(institute=institute_obj, case=case_obj, format="html", **data)


@cases_bp.route("/<institute_id>/<case_name>/pdf_report", methods=["GET"])
def pdf_case_report(institute_id, case_name):
    """Download a pdf report for a case"""

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = controllers.case_report_content(store, institute_obj, case_obj)

    # add coverage report on the bottom of this report
    if current_app.config.get("SQLALCHEMY_DATABASE_URI"):
        data["coverage_report"] = controllers.coverage_report_contents(
            store, institute_obj, case_obj, request.url_root
        )

    # workaround to be able to print the case pedigree to pdf
    if case_obj.get("madeline_info") is not None:
        with open(os.path.join(cases_bp.static_folder, "madeline.svg"), "w") as temp_madeline:
            temp_madeline.write(case_obj["madeline_info"])

    html_report = render_template(
        "cases/case_report.html", institute=institute_obj, case=case_obj, format="pdf", **data
    )
    return render_pdf(
        HTML(string=html_report),
        download_filename=case_obj["display_name"]
        + "_"
        + datetime.datetime.now().strftime("%Y-%m-%d")
        + "_scout.pdf",
    )


@cases_bp.route("/<institute_id>/<case_name>/mt_report", methods=["GET"])
def mt_report(institute_id, case_name):
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)

    # create a temp folder to write excel files into
    temp_excel_dir = os.path.join(cases_bp.static_folder, "_".join([case_name, "mt_reports"]))
    os.makedirs(temp_excel_dir, exist_ok=True)

    # create mt excel files, one for each sample
    n_files = controllers.mt_excel_files(store, case_obj, temp_excel_dir)

    if n_files:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        # zip the files on the fly and serve the archive to the user
        data = io.BytesIO()
        with zipfile.ZipFile(data, mode="w") as z:
            for f_name in pathlib.Path(temp_excel_dir).iterdir():
                z.write(f_name, os.path.basename(f_name))
        data.seek(0)

        # remove temp folder with excel files in it
        shutil.rmtree(temp_excel_dir)

        return send_file(
            data,
            mimetype="application/zip",
            as_attachment=True,
            attachment_filename="_".join(["scout", case_name, "MT_report", today]) + ".zip",
            cache_timeout=0,
        )

    flash("No MT report excel file could be exported for this sample", "warning")
    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/diagnose", methods=["POST"])
def case_diagnosis(institute_id, case_name):
    """Add or remove a diagnosis for a case."""

    level = "phenotype" if "phenotype" in request.form else "gene"
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for(".case", institute_id=institute_id, case_name=case_name)

    omim_id = request.form["omim_term"].split("|")[0]

    if not "OMIM:" in omim_id:  # Could be an omim number provided by user
        omim_id = ":".join(["OMIM", omim_id])

    # Make sure omim term exists in database:
    omim_obj = store.disease_term(omim_id.strip())
    if level == "phenotype" and omim_obj is None:
        flash("Couldn't find any disease term with id: {}".format(omim_id), "warning")
        return redirect(request.referrer)

    remove = True if request.args.get("remove") == "yes" else False
    store.diagnose(
        institute_obj, case_obj, user_obj, link, level=level, omim_id=omim_id, remove=remove
    )
    return redirect(request.referrer)


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
            phenotype_term = request.form["hpo_term"]
            if phenotype_term.startswith("HP:") or len(phenotype_term) == 7:
                hpo_term = phenotype_term.split(" | ", 1)[0]
                store.add_phenotype(
                    institute_obj,
                    case_obj,
                    user_obj,
                    case_url,
                    hpo_term=hpo_term,
                    is_group=is_group,
                )
            else:
                # assume omim id
                store.add_phenotype(
                    institute_obj, case_obj, user_obj, case_url, omim_term=phenotype_term
                )
        except ValueError:
            return abort(400, ("unable to add phenotype: {}".format(phenotype_term)))
    return redirect(case_url)


def parse_raw_gene_ids(raw_symbols):
    """Parse raw gene symbols for hgnc_symbols from web form autocompletion.

    Arguments:
        raw_symbol_strings(list(string)) - formated "17284 | POT1 (hPot1, POT1)"

    Returns:
        hgnc_ids(set(int))
    """
    hgnc_ids = set()

    for raw_symbol in raw_symbols:
        LOG.debug("raw gene: {}".format(raw_symbol))
        # avoid empty lists
        if raw_symbol:
            # take the first nubmer before |, and remove any space.
            try:
                hgnc_ids.add(int(raw_symbol.split("|", 1)[0].replace(" ", "")))
            except ValueError:
                flash(
                    "Provided gene info could not be parsed! "
                    "Please allow autocompletion to finish.",
                    "warning",
                )

    LOG.debug("Parsed HGNC symbols {}".format(hgnc_ids))

    return hgnc_ids


def parse_raw_gene_symbols(raw_symbols_list):
    """Parse list of concatenated gene symbol list for hgnc_symbols from Phenomizer.

    Arguments:
        raw_symbols(list(string)) - e.g. ("POT1 | MUTYH", "POT1 | ATXN1 | ATXN7")

    Returns:
        hgnc_symbols(set(string)) - set of (unique) gene symbols without intervening chars
    """
    hgnc_symbols = set()

    for raw_symbols in raw_symbols_list:
        LOG.debug("raw gene: {}".format(raw_symbols))
        # avoid empty lists
        if raw_symbols:
            hgnc_symbols.update(
                raw_symbol.split(" ", 1)[0] for raw_symbol in raw_symbols.split("|")
            )
    LOG.debug("Parsed HGNC symbols {}".format(hgnc_symbols))

    return hgnc_symbols


@cases_bp.route("/<institute_id>/<case_name>/phenotypes/actions", methods=["POST"])
def phenotypes_actions(institute_id, case_name):
    """Perform actions on multiple phenotypes."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    case_url = url_for(".case", institute_id=institute_id, case_name=case_name)
    action = request.form["action"]
    hpo_ids = request.form.getlist("hpo_id")
    user_obj = store.user(current_user.email)

    if action == "PHENOMIZER":
        if len(hpo_ids) == 0:
            hpo_ids = [term["phenotype_id"] for term in case_obj.get("phenotype_terms", [])]

        username = current_app.config["PHENOMIZER_USERNAME"]
        password = current_app.config["PHENOMIZER_PASSWORD"]
        diseases = controllers.hpo_diseases(username, password, hpo_ids)
        return render_template(
            "cases/diseases.html", diseases=diseases, institute=institute_obj, case=case_obj
        )

    if action == "DELETE":
        for hpo_id in hpo_ids:
            # DELETE a phenotype from the list
            store.remove_phenotype(institute_obj, case_obj, user_obj, case_url, hpo_id)

    if action == "ADDGENE":
        hgnc_ids = parse_raw_gene_ids(request.form.getlist("genes"))
        store.update_dynamic_gene_list(case_obj, hgnc_ids=list(hgnc_ids), add_only=True)

    if action == "GENES":
        hgnc_symbols = parse_raw_gene_symbols(request.form.getlist("genes"))
        store.update_dynamic_gene_list(case_obj, hgnc_symbols=list(hgnc_symbols))

    if action == "GENERATE":
        if len(hpo_ids) == 0:
            hpo_ids = [term["phenotype_id"] for term in case_obj.get("phenotype_terms", [])]
        results = store.generate_hpo_gene_list(*hpo_ids)
        # determine how many HPO terms each gene must match
        hpo_count = int(request.form.get("min_match") or 1)
        hgnc_ids = [result[0] for result in results if result[1] >= hpo_count]
        store.update_dynamic_gene_list(case_obj, hgnc_ids=hgnc_ids, phenotype_ids=hpo_ids)

    return redirect(case_url)


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

    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/assign", methods=["POST"])
@cases_bp.route("/<institute_id>/<case_name>/<user_id>/<inactivate>/assign", methods=["POST"])
def assign(institute_id, case_name, user_id=None, inactivate=False):
    """Assign and unassign a user from a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    link = url_for(".case", institute_id=institute_id, case_name=case_name)
    if user_id:
        user_obj = store.user(user_id)
    else:
        user_obj = store.user(current_user.email)
    if request.form.get("action") == "DELETE":
        store.unassign(institute_obj, case_obj, user_obj, link, inactivate)
    else:
        store.assign(institute_obj, case_obj, user_obj, link)
    return redirect(request.referrer)


@cases_bp.route("/api/v1/<institute_id>/cases")
def caselist(institute_id):
    """Search for cases for autocompletion"""
    query = request.args.get("query")
    if query is None:
        return abort(500)
    display_names = sorted(
        [
            case["display_name"]
            for case in store.cases(owner=institute_id, name_query="case:" + query)
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


@cases_bp.route("/api/v1/omim-terms")
def omimterms():
    query = request.args.get("query")
    if query is None:
        return abort(500)
    terms = store.query_omim(query=query)
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
        "variant.variant", institute_id=institute_id, case_name=case_name, variant_id=variant_id
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
        "variant.variant", institute_id=institute_id, case_name=case_name, variant_id=variant_id
    )
    store.validate(institute_obj, case_obj, user_obj, link, variant_obj, validate_type)
    return redirect(request.referrer or link)


@cases_bp.route(
    "/<institute_id>/<case_name>/<variant_id>/<partial_causative>/causative", methods=["POST"]
)
def mark_causative(institute_id, case_name, variant_id, partial_causative=False):
    """Mark a variant as confirmed causative."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    user_obj = store.user(current_user.email)
    link = url_for(
        "variant.variant", institute_id=institute_id, case_name=case_name, variant_id=variant_id
    )
    if request.form["action"] == "ADD":
        if "partial_causative" in request.form:
            omim_terms = request.form.getlist("omim_select")
            hpo_terms = request.form.getlist("hpo_select")
            store.mark_partial_causative(
                institute_obj, case_obj, user_obj, link, variant_obj, omim_terms, hpo_terms
            )
        else:
            store.mark_causative(institute_obj, case_obj, user_obj, link, variant_obj)
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


@cases_bp.route("/<institute_id>/<case_name>/delivery-report")
def delivery_report(institute_id, case_name):
    """Display delivery report."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    if case_obj.get("delivery_report") is None:
        return abort(404)

    date_str = request.args.get("date")
    if date_str is not None:
        delivery_report = None
        for analysis_data in case_obj.get("analyses", []):
            if str(analysis_data["date"].date()) == date_str:
                delivery_report = analysis_data["delivery_report"]
        if delivery_report is None:
            return abort(404)
    else:
        delivery_report = case_obj["delivery_report"]

    report_format = request.args.get("format", "html")
    if report_format == "pdf":
        try:  # file could not be available
            html_file = open(delivery_report, "r")
            source_code = html_file.read()
            # remove image, since it is problematic to render it in the PDF version
            source_code = re.sub(
                '<img class=.*?alt="SWEDAC logo">', "", source_code, flags=re.DOTALL
            )
            return render_pdf(
                HTML(string=source_code),
                download_filename=case_obj["display_name"]
                + "_"
                + datetime.datetime.now().strftime("%Y-%m-%d")
                + "_scout_delivery.pdf",
            )
        except Exception as ex:
            flash(
                "An error occurred while downloading delivery report {} -- {}".format(
                    delivery_report, ex
                ),
                "warning",
            )

    out_dir = os.path.dirname(delivery_report)
    filename = os.path.basename(delivery_report)

    return send_from_directory(out_dir, filename)


@cases_bp.route("/<institute_id>/<case_name>/cnv-report")
def cnv_report(institute_id, case_name):
    """Display CNV report."""
    data = controllers.multiqc(store, institute_id, case_name)
    if data["case"].get("cnv_report") is None:
        return abort(404)
    out_dir = os.path.abspath(os.path.dirname(data["case"]["cnv_report"]))
    filename = os.path.basename(data["case"]["cnv_report"])
    return send_from_directory(out_dir, filename)


@cases_bp.route("/<institute_id>/<case_name>/coverage-qc-report")
def coverage_qc_report(institute_id, case_name):
    """Display coverage and qc report."""
    _, case_obj = institute_and_case(store, institute_id, case_name)
    data = controllers.multiqc(store, institute_id, case_name)
    if data["case"].get("coverage_qc_report") is None:
        return abort(404)

    coverage_qc_report = data["case"]["coverage_qc_report"]
    report_format = request.args.get("format", "html")
    if report_format == "pdf":
        try:  # file could not be available
            html_file = open(coverage_qc_report, "r")
            source_code = html_file.read()
            return render_pdf(
                HTML(string=source_code),
                download_filename=case_obj["display_name"]
                + "_"
                + datetime.datetime.now().strftime("%Y-%m-%d")
                + "_coverage_qc_report.pdf",
            )
        except Exception as ex:
            flash(
                "An error occurred while downloading delivery report {} -- {}".format(
                    coverage_qc_report, ex
                ),
                "warning",
            )

    out_dir = os.path.dirname(coverage_qc_report)
    filename = os.path.basename(coverage_qc_report)

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


@cases_bp.route("/<institute_id>/<case_name>/rerun", methods=["POST"])
def rerun(institute_id, case_name):
    """Request a case to be rerun."""
    sender = current_app.config.get("MAIL_USERNAME")
    recipient = current_app.config.get("TICKET_SYSTEM_EMAIL")

    controllers.rerun(store, mail, current_user, institute_id, case_name, sender, recipient)
    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/research", methods=["POST"])
def research(institute_id, case_name):
    """Open the research list for a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for(".case", institute_id=institute_id, case_name=case_name)
    store.open_research(institute_obj, case_obj, user_obj, link)
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
    return redirect(request.referrer)


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

    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/<case_group>/remove_case_group", methods=["GET"])
def remove_case_group(institute_id, case_name, case_group):
    """Unbind a case group from a case. Remove the group if it is no longer in use."""
    controllers.remove_case_group(store, current_user, institute_id, case_name, case_group)

    return redirect(request.referrer)


@cases_bp.route("/<case_group>/case_group_update_label", methods=["POST"])
def case_group_update_label(case_group):
    """Unbind a case group from a case. Remove the group if it is no longer in use."""
    label = request.form.get("label", "unlabeled")

    controllers.case_group_update_label(store, case_group, label)

    return redirect(request.referrer)


@cases_bp.route("/<institute_id>/<case_name>/download-hpo-genes", methods=["GET"])
def download_hpo_genes(institute_id, case_name):
    """Download the genes contained in a case dynamic gene list"""

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    # Create export object consisting of dynamic phenotypes with associated genes as a dictionary
    phenotype_terms_with_genes = controllers.phenotypes_genes(store, case_obj)
    html_content = ""
    for term_id, term in phenotype_terms_with_genes.items():
        html_content += f"<hr><strong>{term_id} - {term.get('description')}</strong><br><br>{term.get('genes')}<br>"
    return render_pdf(
        HTML(string=html_content),
        download_filename=case_obj["display_name"]
        + "_"
        + datetime.datetime.now().strftime("%Y-%m-%d")
        + "_dynamic_phenotypes.pdf",
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
    attachment_filename = ".".join(
        [display_name, case_obj["display_name"], case_obj["_id"], "vcf2cytosure.cgh"]
    )
    LOG.debug("Attempt to deliver file {0} from dir {1}".format(attachment_filename, outdir))
    return send_from_directory(
        outdir, filename, attachment_filename=attachment_filename, as_attachment=True
    )


@cases_bp.route("/<institute_id>/<case_name>/multiqc")
def multiqc(institute_id, case_name):
    """Load multiqc report for the case."""
    data = controllers.multiqc(store, institute_id, case_name)
    if data["case"].get("multiqc") is None:
        return abort(404)
    out_dir = os.path.abspath(os.path.dirname(data["case"]["multiqc"]))
    filename = os.path.basename(data["case"]["multiqc"])
    return send_from_directory(out_dir, filename)


@cases_bp.route(
    "/<institute_id>/<case_name>/<individual>/upd_regions_images/<image>", methods=["GET", "POST"]
)
def host_upd_regions_image(institute_id, case_name, individual, image):
    """Generate UPD REGIONS image file paths"""
    LOG.debug("REGIONS")
    return host_image_aux(institute_id, case_name, individual, image, "upd_regions")


@cases_bp.route(
    "/<institute_id>/<case_name>/<individual>/upd_sites_images/<image>", methods=["GET", "POST"]
)
def host_upd_sites_image(institute_id, case_name, individual, image):
    """Generate UPD image file paths"""
    return host_image_aux(institute_id, case_name, individual, image, "upd_sites")


@cases_bp.route(
    "/<institute_id>/<case_name>/<individual>/coverage_images/<image>", methods=["GET", "POST"]
)
def host_coverage_image(institute_id, case_name, individual, image):
    """Generate Coverage image file paths"""
    return host_image_aux(institute_id, case_name, individual, image, "coverage")


@cases_bp.route(
    "/<institute_id>/<case_name>/<individual>/autozygous_images/<image>", methods=["GET", "POST"]
)
def host_autozygous_image(institute_id, case_name, individual, image):
    """Generate Coverage image file paths"""
    return host_image_aux(institute_id, case_name, individual, image, "autozygous")


@cases_bp.route(
    "/<institute_id>/<case_name>/<individual>/ideograms/<image>", methods=["GET", "POST"]
)
def host_chr_image(institute_id, case_name, individual, image):
    """Generate CHR image file paths. Points to servers 'public/static'"""
    public_folder = "/public/static/ideograms/"
    img_path = public_folder + image
    LOG.debug("ideaogram: {}".format(img_path))
    return send_from_directory(img_path, image)


def host_image_aux(institute_id, case_name, individual, image, key):
    """Auxilary function for generate absolute file paths"""
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


def _generate_csv(header, lines):
    """Download a text file composed of any header and lines"""
    yield header + "\n"
    for line in lines:  # lines have already quoted fields
        yield line + "\n"
