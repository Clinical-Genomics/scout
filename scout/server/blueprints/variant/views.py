import logging

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from markupsafe import Markup

from scout.constants import ACMG_CRITERIA, ACMG_MAP
from scout.server.blueprints.variant.controllers import check_reset_variant_classification
from scout.server.blueprints.variant.controllers import evaluation as evaluation_controller
from scout.server.blueprints.variant.controllers import observations, str_variant_reviewer
from scout.server.blueprints.variant.controllers import variant as variant_controller
from scout.server.blueprints.variant.controllers import variant_acmg as acmg_controller
from scout.server.blueprints.variant.controllers import variant_acmg_post
from scout.server.blueprints.variant.verification_controllers import (
    MissingVerificationRecipientError,
    variant_verification,
)
from scout.server.extensions import loqusdb, store
from scout.server.utils import institute_and_case, public_endpoint, templated
from scout.utils.acmg import get_acmg
from scout.utils.ensembl_rest_clients import EnsemblRestApiClient

LOG = logging.getLogger(__name__)

variant_bp = Blueprint(
    "variant",
    __name__,
    template_folder="templates",
    static_folder="static",
)


@variant_bp.route("/update_tracks", methods=["POST"])
def update_tracks_settings():
    """Update custom track settings for a user according to form choices"""
    user_obj = store.user(email=current_user.email)
    selected_tracks = request.form.getlist("user_tracks") or []
    # update user in database with custom tracks info
    user_obj["igv_tracks"] = selected_tracks
    store.update_user(user_obj)
    return redirect(request.referrer)


@variant_bp.route("/document_id/<variant_id>")
def variant_by_id(variant_id):
    """Display variant given by its document id. This includes its unique case name.
    The view template is selected based on the variant category."""
    data = variant_controller(
        store=store,
        variant_id=variant_id,
    )
    if data is None:
        flash("An error occurred while retrieving variant object", "danger")
        return redirect(url_for("public.index"))

    if current_app.config.get("LOQUSDB_SETTINGS"):
        LOG.debug("Fetching loqusdb information for %s", variant_id)
        data["observations"] = observations(store, loqusdb, data["variant"])

    if data["variant"].get("category") == "sv":
        return render_template("variant/sv-variant.html", **data)

    if data["variant"].get("category") == "cancer":
        return render_template("variant/cancer-variant.html", **data)

    return render_template("variant/variant.html", **data)


@variant_bp.route("/<institute_id>/<case_name>/<variant_id>")
@templated("variant/variant.html")
def variant(variant_id, institute_id=None, case_name=None):
    """Display a specific SNV variant."""
    LOG.debug("Variants view requesting data for variant %s", variant_id)

    data = variant_controller(
        store=store,
        variant_id=variant_id,
        institute_id=institute_id,
        case_name=case_name,
    )
    if data is None:
        flash("An error occurred while retrieving variant object", "danger")
        return redirect(
            url_for("variants.variants", institute_id=institute_id, case_name=case_name)
        )

    if current_app.config.get("LOQUSDB_SETTINGS"):
        LOG.debug("Fetching loqusdb information for %s", variant_id)
        data["observations"] = observations(store, loqusdb, data["variant"])

    return data


@variant_bp.route("/<institute_id>/<case_name>/cancer/<variant_id>")
@templated("variant/cancer-variant.html")
def cancer_variant(institute_id, case_name, variant_id):
    """Display a specific SNV variant."""
    LOG.debug("Variants view requesting data for variant %s", variant_id)

    data = variant_controller(
        store=store, variant_id=variant_id, institute_id=institute_id, case_name=case_name
    )
    if data is None:
        flash("An error occurred while retrieving variant object", "danger")
        return redirect(
            url_for(
                "variants.cancer_variants",
                institute_id=institute_id,
                case_name=case_name,
            )
        )

    if current_app.config.get("LOQUSDB_SETTINGS"):
        LOG.debug("Fetching loqusdb information for %s", variant_id)
        data["observations"] = observations(store, loqusdb, data["variant"])

    return data


@variant_bp.route("/<institute_id>/<case_name>/sv/variants/<variant_id>")
@templated("variant/sv-variant.html")
def sv_variant(institute_id, case_name, variant_id):
    """Display a specific structural variant."""
    data = variant_controller(
        store=store,
        variant_id=variant_id,
        institute_id=institute_id,
        case_name=case_name,
    )

    if data is None:
        flash("An error occurred while retrieving variant object", "danger")
        return redirect(
            url_for("variants.sv_variants", institute_id=institute_id, case_name=case_name)
        )

    if current_app.config.get("LOQUSDB_SETTINGS"):
        LOG.debug("Fetching loqusdb information for %s", variant_id)
        data["observations"] = observations(store, loqusdb, data["variant"])

    return data


@variant_bp.route("/<institute_id>/<case_name>/str/variant/<variant_id>", methods=["GET"])
@templated("variant/str-variant-reviewer.html")
def reviewer_aln(institute_id, case_name, variant_id):
    """Display STR variant alignment using the REViewer service."""
    if request.args.get("variant_type", "clinical") == "research":
        variant_type = "research"
    else:
        variant_type = "clinical"

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = str_variant_reviewer(store, case_obj, variant_id)

    return dict(
        institute=institute_obj,
        case=case_obj,
        variant_type=variant_type,
        format="html",
        **data,
    )


@variant_bp.route("/<institute_id>/<case_name>/<variant_id>/acmg", methods=["GET", "POST"])
@templated("variant/acmg.html")
def variant_acmg(institute_id, case_name, variant_id):
    """ACMG classification form."""
    if request.method == "GET":
        data = acmg_controller(store, institute_id, case_name, variant_id)
        return data

    criteria = []
    criteria_terms = request.form.getlist("criteria")
    for term in criteria_terms:
        criteria.append(
            dict(
                term=term,
                comment=request.form.get("comment-{}".format(term)),
                links=[request.form.get("link-{}".format(term))],
                modifier=request.form.get("modifier-{}".format(term)),
            )
        )
    acmg = variant_acmg_post(
        store, institute_id, case_name, variant_id, current_user.email, criteria
    )
    flash("classified as: {}".format(acmg), "info")
    return redirect(
        url_for(
            ".variant",
            institute_id=institute_id,
            case_name=case_name,
            variant_id=variant_id,
        )
    )


@variant_bp.route("/<institute_id>/<case_name>/<variant_id>/update", methods=["POST"])
def variant_update(institute_id, case_name, variant_id):
    """Update user-defined information about a variant: manual rank & ACMG."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    user_obj = store.user(current_user.email)
    link = request.referrer

    manual_rank = (
        Markup.escape(request.form.get("manual_rank")) if request.form.get("manual_rank") else None
    )
    cancer_tier = (
        Markup.escape(request.form.get("cancer_tier")) if request.form.get("cancer_tier") else None
    )

    if manual_rank:
        try:
            new_manual_rank = int(manual_rank) if manual_rank != "-1" else None
        except ValueError:
            LOG.warning("Attempt to update manual rank with invalid value {}".format(manual_rank))
            manual_rank = "-1"
            new_manual_rank = -1

        store.update_manual_rank(
            institute_obj, case_obj, user_obj, link, variant_obj, new_manual_rank
        )
        if new_manual_rank:
            flash("Variant tag was updated", "info")
        else:
            flash("Variant tag was reset", "info")
    elif cancer_tier:
        try:
            new_cancer_tier = cancer_tier if cancer_tier != "-1" else None
        except ValueError:
            LOG.warning("Attempt to update cancer tier with invalid value {}".format(cancer_tier))
            cancer_tier = "-1"
            new_cancer_tier = "-1"

        store.update_cancer_tier(
            institute_obj, case_obj, user_obj, link, variant_obj, new_cancer_tier
        )
        if new_cancer_tier:
            flash("Variant tag was updated", "info")
        else:
            flash("Variant tag was reset", "info")
    elif request.form.get("acmg_classification"):
        new_acmg = request.form["acmg_classification"]
        acmg_classification = variant_obj.get("acmg_classification")
        # If there already is a classification and the same one is sent again this means that
        # We want to remove the classification
        if isinstance(acmg_classification, int) and (new_acmg == ACMG_MAP[acmg_classification]):
            new_acmg = None

        store.submit_evaluation(
            variant_obj=variant_obj,
            user_obj=user_obj,
            institute_obj=institute_obj,
            case_obj=case_obj,
            link=link,
            classification=new_acmg,
        )
        flash("updated ACMG classification: {}".format(new_acmg), "info")

    new_dismiss = request.form.getlist("dismiss_variant")
    if new_dismiss:
        store.update_dismiss_variant(
            institute_obj, case_obj, user_obj, link, variant_obj, new_dismiss
        )
        flash("Dismissed variant: {}".format(new_dismiss), "info")

    variant_dismiss = variant_obj.get("dismiss_variant")
    if variant_dismiss and not new_dismiss:
        if "dismiss" in request.form:
            store.update_dismiss_variant(
                institute_obj, case_obj, user_obj, link, variant_obj, new_dismiss
            )
            flash(
                "Reset variant dismissal: {}".format(variant_obj.get("dismiss_variant")),
                "info",
            )
        else:
            LOG.debug(
                "DO NOT reset variant dismissal: {}".format(",".join(variant_dismiss), "info")
            )

    mosaic_tags = request.form.getlist("mosaic_tags")
    if mosaic_tags:
        store.update_mosaic_tags(institute_obj, case_obj, user_obj, link, variant_obj, mosaic_tags)
        flash("Added mosaic tags: {}".format(mosaic_tags), "info")

    variant_mosaic = variant_obj.get("mosaic_tags")
    if variant_mosaic and not mosaic_tags:
        if "mosaic" in request.form:
            store.update_mosaic_tags(
                institute_obj, case_obj, user_obj, link, variant_obj, mosaic_tags
            )
            flash("Reset mosaic tags: {}".format(",".join(variant_mosaic), "info"))

    return redirect(request.referrer)


@variant_bp.route("/evaluations/<evaluation_id>", methods=["GET", "POST"])
@templated("variant/acmg.html")
def evaluation(evaluation_id):
    """Show or delete an ACMG evaluation."""

    evaluation_obj = store.get_evaluation(evaluation_id)
    if evaluation_obj is None:
        flash("Evaluation was not found in database", "warning")
        return redirect(request.referrer)
    evaluation_controller(store, evaluation_obj)
    if request.method == "POST":
        link = url_for(
            ".variant",
            institute_id=evaluation_obj["institute"]["_id"],
            case_name=evaluation_obj["case"]["display_name"],
            variant_id=evaluation_obj["variant_specific"],
        )
        store.delete_evaluation(evaluation_obj)

        if check_reset_variant_classification(store, evaluation_obj, link):
            flash("Cleared ACMG classification.", "info")

        return redirect(link)
    return dict(
        evaluation=evaluation_obj,
        institute=evaluation_obj["institute"],
        case=evaluation_obj["case"],
        variant=evaluation_obj["variant"],
        CRITERIA=ACMG_CRITERIA,
    )


@variant_bp.route("/api/v1/acmg")
@public_endpoint
def acmg():
    """Calculate an ACMG classification from submitted criteria."""
    criteria = request.args.getlist("criterion")
    classification = get_acmg(criteria)
    return jsonify(dict(classification=classification))


@variant_bp.route(
    "/<institute_id>/<case_name>/<variant_id>/<order>",
    methods=["POST"],
)
def verify(institute_id, case_name, variant_id, order):
    """Start procedure to validate variant using other techniques."""
    comment = request.form.get("verification_comment")

    try:
        variant_verification(
            store=store,
            institute_id=institute_id,
            case_name=case_name,
            comment=comment,
            variant_id=variant_id,
            sender=current_app.config.get("MAIL_USERNAME"),
            variant_url=request.referrer,
            order=order,
            url_builder=url_for,
        )
    except MissingVerificationRecipientError:
        flash("No verification recipients added to institute.", "danger")

    return redirect(request.referrer)


@variant_bp.route("/marrvel/<build>/<variant_id>", methods=["GET"])
def marrvel_link(build, variant_id):
    """Redirect to MARRVEL when user clicks on the relative button on variant page"""
    variant_obj = store.variant(document_id=variant_id)
    build = "38" if "38" in str(build) else "37"

    url_template = "http://marrvel.org/human/variant/{}:{} {}>{}"
    chrom = variant_obj["chromosome"]
    start = variant_obj["position"]
    ref = variant_obj["reference"]
    alt = variant_obj["alternative"]

    if build == "38":  # liftover is necessary before returning link
        client = EnsemblRestApiClient()
        mapped_coords = client.liftover(
            build,
            chrom,
            start,
        )
        if mapped_coords:
            chrom = mapped_coords[0]["mapped"].get("seq_region_name")
            start = mapped_coords[0]["mapped"].get("start")
        else:
            flash(
                "MARRVEL requires variant coordinates in genome build 37, but variant liftover failed",
                "warning",
            )
            return redirect(request.referrer)

    return redirect(url_template.format(chrom, start, ref, alt), code=302)
