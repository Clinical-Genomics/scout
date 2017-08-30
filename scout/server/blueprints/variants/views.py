# -*- coding: utf-8 -*-
import io
import logging

from flask import Blueprint, request, redirect, abort, flash, current_app, url_for, jsonify
from flask_login import current_user

from scout.constants import SEVERE_SO_TERMS
from scout.constants.acmg import ACMG_CRITERIA
from scout.constants import ACMG_MAP
from scout.server.extensions import store, mail, loqusdb
from scout.server.utils import templated, institute_and_case, public_endpoint
from scout.utils.acmg import get_acmg
from . import controllers
from .forms import FiltersForm, SvFiltersForm

log = logging.getLogger(__name__)
variants_bp = Blueprint('variants', __name__, template_folder='templates')


@variants_bp.route('/<institute_id>/<case_name>/variants')
@templated('variants/variants.html')
def variants(institute_id, case_name):
    """Display a list of SNV variants."""
    page = int(request.args.get('page', 1))
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)

    form = FiltersForm(request.args)
    panel_choices = [(panel['panel_name'], panel['display_name'])
                     for panel in case_obj.get('panels', [])]
    form.gene_panels.choices = panel_choices

    # update status of case if vistited for the first time
    if case_obj['status'] == 'inactive' and not current_user.is_admin:
        flash('You just activated this case!', 'info')
        user_obj = store.user(current_user.email)
        case_link = url_for('cases.case', institute_id=institute_obj['_id'],
                            case_name=case_obj['display_name'])
        store.update_status(institute_obj, case_obj, user_obj, 'active', case_link)

    # check if supplied gene symbols exist
    hgnc_symbols = []
    for hgnc_symbol in form.hgnc_symbols.data:
        if hgnc_symbol.isdigit():
            hgnc_gene = store.hgnc_gene(int(hgnc_symbol))
            if hgnc_gene is None:
                flash("HGNC id not found: {}".format(hgnc_symbol), 'warning')
            else:
                hgnc_symbols.append(hgnc_gene['hgnc_symbol'])
        elif store.hgnc_genes(hgnc_symbol).count() == 0:
            flash("HGNC symbol not found: {}".format(hgnc_symbol), 'warning')
        else:
            hgnc_symbols.append(hgnc_symbol)
    form.hgnc_symbols.data = hgnc_symbols

    # handle HPO gene list separately
    if form.data['gene_panels'] == ['hpo']:
        hpo_symbols = list(set(term_obj['hgnc_symbol'] for term_obj in
                               case_obj['dynamic_gene_list']))
        form.hgnc_symbols.data = hpo_symbols

    variants_query = store.variants(case_obj['_id'], query=form.data)
    data = controllers.variants(store, institute_obj, case_obj, variants_query, page)

    return dict(institute=institute_obj, case=case_obj, form=form,
                severe_so_terms=SEVERE_SO_TERMS, page=page, **data)


@variants_bp.route('/<institute_id>/<case_name>/<variant_id>')
@templated('variants/variant.html')
def variant(institute_id, case_name, variant_id):
    """Display a specific SNV variant."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = controllers.variant(store, institute_obj, case_obj, variant_id)
    if data is None:
        return abort(404)
    if current_app.config.get('LOQUSDB_SETTINGS'):
        data['observations'] = controllers.observations(store, loqusdb, case_obj, data['variant'])
    data['cancer'] = request.args.get('cancer') == 'yes'
    return dict(institute=institute_obj, case=case_obj, **data)


@variants_bp.route('/<institute_id>/<case_name>/sv/variants')
@templated('variants/sv-variants.html')
def sv_variants(institute_id, case_name):
    """Display a list of structural variants."""
    page = int(request.args.get('page', 1))
    variant_type = request.args.get('variant_type', 'clinical')

    form = SvFiltersForm(request.args)

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    panel_choices = [(panel['panel_name'], panel['display_name'])
                     for panel in case_obj.get('panels', [])]
    form.gene_panels.choices = panel_choices
    query = form.data
    query['variant_type'] = variant_type
    variants_query = store.variants(case_obj['_id'], category='sv', query=form.data)
    data = controllers.sv_variants(store, institute_obj, case_obj, variants_query, page)
    return dict(institute=institute_obj, case=case_obj, variant_type=variant_type,
                form=form, severe_so_terms=SEVERE_SO_TERMS, page=page, **data)


@variants_bp.route('/<institute_id>/<case_name>/sv/variants/<variant_id>')
@templated('variants/sv-variant.html')
def sv_variant(institute_id, case_name, variant_id):
    """Display a specific structural variant."""
    data = controllers.sv_variant(store, institute_id, case_name, variant_id)
    return data


@variants_bp.route('/<institute_id>/<case_name>/<variant_id>/update', methods=['POST'])
def variant_update(institute_id, case_name, variant_id):
    """Update user-defined information about a variant: manual rank & ACMG."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    user_obj = store.user(current_user.email)
    link = request.referrer

    if request.form.get('manual_rank'):
        new_manual_rank = int(request.form['manual_rank'])
        store.update_manual_rank(institute_obj, case_obj, user_obj, link, variant_obj,
                                 new_manual_rank)
        flash("updated manual rank: {}".format(new_manual_rank), 'info')
    elif request.form.get('acmg_classification'):
        new_acmg = request.form['acmg_classification']
        acmg_classification = variant_obj.get('acmg_classification')
        if acmg_classification and (new_acmg == ACMG_MAP[acmg_classification]):
            new_acmg = None
        store.update_acmg(institute_obj, case_obj, user_obj, link, variant_obj, new_acmg)
        flash("updated ACMG classification: {}".format(new_acmg), 'info')
    return redirect(request.referrer)


@variants_bp.route('/<institute_id>/<case_name>/<variant_id>/sanger', methods=['POST'])
def sanger(institute_id, case_name, variant_id):
    """Send Sanger email for confirming a variant."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    user_obj = store.user(current_user.email)
    try:
        controllers.sanger(store, mail, institute_obj, case_obj, user_obj,
                           variant_obj, current_app.config['MAIL_USERNAME'])
    except controllers.MissingSangerRecipientError:
        flash('No sanger recipients added to institute.', 'danger')
    return redirect(request.referrer)


@variants_bp.route('/<institute_id>/<case_name>/cancer/variants')
@templated('variants/cancer-variants.html')
def cancer_variants(institute_id, case_name):
    """Show cancer variants overview."""
    data = controllers.cancer_variants(store, request.args, institute_id, case_name)
    return data


@variants_bp.route('/<institute_id>/<case_name>/<variant_id>/acmg', methods=['GET', 'POST'])
@templated('variants/acmg.html')
def variant_acmg(institute_id, case_name, variant_id):
    """ACMG classification form."""
    if request.method == 'GET':
        data = controllers.variant_acmg(store, institute_id, case_name, variant_id)
        return data
    else:
        criteria = []
        criteria_terms = request.form.getlist('criteria')
        for term in criteria_terms:
            criteria.append(dict(
                term=term,
                comment=request.form.get("comment-{}".format(term)),
                links=[request.form.get("link-{}".format(term))],
            ))
        acmg = controllers.variant_acmg_post(store, institute_id, case_name, variant_id,
                                             current_user.email, criteria)
        flash("classified as: {}".format(acmg), 'info')
        return redirect(url_for('.variant', institute_id=institute_id, case_name=case_name,
                                variant_id=variant_id))


@variants_bp.route('/evaluations/<evaluation_id>', methods=['GET', 'POST'])
@templated('variants/acmg.html')
def evaluation(evaluation_id):
    """Show or delete an ACMG evaluation."""
    evaluation_obj = store.get_evaluation(evaluation_id)
    controllers.evaluation(store, evaluation_obj)
    if request.method == 'POST':
        link = url_for('.variant', institute_id=evaluation_obj['institute']['_id'],
                       case_name=evaluation_obj['case']['display_name'],
                       variant_id=evaluation_obj['variant_specific'])
        store.delete_evaluation(evaluation_obj)
        return redirect(link)
    return dict(evaluation=evaluation_obj, institute=evaluation_obj['institute'],
                case=evaluation_obj['case'], variant=evaluation_obj['variant'],
                CRITERIA=ACMG_CRITERIA)


@variants_bp.route('/api/v1/acmg')
@public_endpoint
def acmg():
    """Calculate an ACMG classification from submitted criteria."""
    criteria = request.args.getlist('criterion')
    classification = get_acmg(criteria)
    return jsonify(dict(classification=classification))


@variants_bp.route('/<institute_id>/<case_name>/upload', methods=['POST'])
def upload_panel(institute_id, case_name):
    """Parse gene panel file and fill in HGNC symbols for filter."""
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'warning')
        return redirect(request.referrer)

    try:
        stream = io.StringIO(file.stream.read().decode('utf-8'), newline=None)
    except UnicodeDecodeError as error:
        flash("Only text files are supported!", 'warning')
        return redirect(request.referrer)

    form = FiltersForm(request.args)
    hgnc_symbols = set(form.hgnc_symbols.data)
    new_hgnc_symbols = controllers.upload_panel(store, institute_id, case_name, stream)
    hgnc_symbols.update(new_hgnc_symbols)
    form.hgnc_symbols.data = ','.join(hgnc_symbols)
    # reset gene panels
    form.gene_panels.data = ''
    return redirect(url_for('.variants', institute_id=institute_id, case_name=case_name,
                            **form.data))
