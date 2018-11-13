# -*- coding: utf-8 -*-
import io
import logging

from flask import Blueprint, request, redirect, abort, flash, current_app, url_for, jsonify, Response, session
from werkzeug.datastructures import Headers, MultiDict
from flask_login import current_user

from scout.constants import SEVERE_SO_TERMS
from scout.constants.acmg import ACMG_CRITERIA
from scout.constants import ACMG_MAP
from scout.server.extensions import store, mail, loqusdb
from scout.server.utils import templated, institute_and_case, public_endpoint
from scout.utils.acmg import get_acmg
from scout.parse.clinvar import set_submission_objects
from . import controllers
from .forms import FiltersForm, SvFiltersForm, StrFiltersForm

log = logging.getLogger(__name__)
variants_bp = Blueprint('variants', __name__, template_folder='templates')

@variants_bp.route('/<institute_id>/<case_name>/variants', methods=['GET','POST'])
@templated('variants/variants.html')
def variants(institute_id, case_name):
    """Display a list of SNV variants."""
    page = int(request.form.get('page', 1))

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_type = request.args.get('variant_type', 'clinical')

    # Update filter settings if Clinical Filter was requested

    default_panels = []
    for panel in case_obj['panels']:
        if panel.get('is_default'):
            default_panels.append(panel['panel_name'])

    request.form.get('gene_panels')
    if bool(request.form.get('clinical_filter')):
        clinical_filter = MultiDict({
            'variant_type': 'clinical',
            'region_annotations': ['exonic','splicing'],
            'functional_annotations': SEVERE_SO_TERMS,
            'clinsig': [4,5],
            'clinsig_confident_always_returned': True,
            'gnomad_frequency': str(institute_obj['frequency_cutoff']),
            'variant_type': 'clinical',
            'gene_panels': default_panels
             })

    if(request.method == "POST"):
        if bool(request.form.get('clinical_filter')):
            form = FiltersForm(clinical_filter)
            form.csrf_token = request.args.get('csrf_token')
        else:
            form = FiltersForm(request.form)
    else:
        form = FiltersForm(request.args)

    # populate available panel choices
    available_panels = case_obj.get('panels', []) + [
        {'panel_name': 'hpo', 'display_name': 'HPO'}]

    panel_choices = [(panel['panel_name'], panel['display_name'])
                     for panel in available_panels]

    form.gene_panels.choices = panel_choices

    # upload gene panel if symbol file exists
    if (request.files):
        file = request.files[form.symbol_file.name]

    if request.files and file and file.filename != '':
        log.debug("Upload file request files: {0}".format(request.files.to_dict()))
        try:
            stream = io.StringIO(file.stream.read().decode('utf-8'), newline=None)
        except UnicodeDecodeError as error:
            flash("Only text files are supported!", 'warning')
            return redirect(request.referrer)

        hgnc_symbols_set = set(form.hgnc_symbols.data)
        log.debug("Symbols prior to upload: {0}".format(hgnc_symbols_set))
        new_hgnc_symbols = controllers.upload_panel(store, institute_id, case_name, stream)
        hgnc_symbols_set.update(new_hgnc_symbols)
        form.hgnc_symbols.data = hgnc_symbols_set
        # reset gene panels
        form.gene_panels.data = ''

    # update status of case if vistited for the first time
    if case_obj['status'] == 'inactive' and not current_user.is_admin:
        flash('You just activated this case!', 'info')
        user_obj = store.user(current_user.email)
        case_link = url_for('cases.case', institute_id=institute_obj['_id'],
                            case_name=case_obj['display_name'])
        store.update_status(institute_obj, case_obj, user_obj, 'active', case_link)

    # check if supplied gene symbols exist
    hgnc_symbols = []
    non_clinical_symbols = []
    not_found_symbols = []
    not_found_ids = []
    if (form.hgnc_symbols.data) and len(form.hgnc_symbols.data) > 0:
        is_clinical = form.data.get('variant_type', 'clinical') == 'clinical'
        clinical_symbols = store.clinical_symbols(case_obj) if is_clinical else None
        for hgnc_symbol in form.hgnc_symbols.data:
            if hgnc_symbol.isdigit():
                hgnc_gene = store.hgnc_gene(int(hgnc_symbol))
                if hgnc_gene is None:
                    not_found_ids.append(hgnc_symbol)
                else:
                    hgnc_symbols.append(hgnc_gene['hgnc_symbol'])
            elif store.hgnc_genes(hgnc_symbol).count() == 0:
                  not_found_symbols.append(hgnc_symbol)
            elif is_clinical and (hgnc_symbol not in clinical_symbols):
                 non_clinical_symbols.append(hgnc_symbol)
            else:
                hgnc_symbols.append(hgnc_symbol)

    if (not_found_ids):
        flash("HGNC id not found: {}".format(", ".join(not_found_ids)), 'warning')
    if (not_found_symbols):
        flash("HGNC symbol not found: {}".format(", ".join(not_found_symbols)), 'warning')
    if (non_clinical_symbols):
        flash("Gene not included in clinical list: {}".format(", ".join(non_clinical_symbols)), 'warning')
    form.hgnc_symbols.data = hgnc_symbols

    # handle HPO gene list separately
    if form.data['gene_panels'] == ['hpo']:
        hpo_symbols = list(set(term_obj['hgnc_symbol'] for term_obj in
                               case_obj['dynamic_gene_list']))
        form.hgnc_symbols.data = hpo_symbols

    variants_query = store.variants(case_obj['_id'], query=form.data)
    data = {}

    if request.form.get('export'):
        document_header = controllers.variants_export_header(case_obj)
        export_lines = []
        if form.data['chrom'] == 'MT':
            # Return all MT variants
            export_lines = controllers.variant_export_lines(store, case_obj, variants_query)
        else:
            # Return max 500 variants
            export_lines = controllers.variant_export_lines(store, case_obj, variants_query.limit(500))

        def generate(header, lines):
            yield header + '\n'
            for line in lines:
                yield line + '\n'

        headers = Headers()
        headers.add('Content-Disposition','attachment', filename=str(case_obj['display_name'])+'-filtered_variants.csv')

        # return a csv with the exported variants
        return Response(generate(",".join(document_header), export_lines), mimetype='text/csv',
                        headers=headers)

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
        data['observations'] = controllers.observations(store, loqusdb,
            case_obj, data['variant'])
    data['cancer'] = request.args.get('cancer') == 'yes'
    return dict(institute=institute_obj, case=case_obj, **data)

@variants_bp.route('/<institute_id>/<case_name>/str/variants')
@templated('variants/str-variants.html')
def str_variants(institute_id, case_name):
    """Display a list of STR variants."""
    page = int(request.args.get('page', 1))
    variant_type = request.args.get('variant_type', 'clinical')

    form = StrFiltersForm(request.args)

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)

    query = form.data
    query['variant_type'] = variant_type

    variants_query = store.variants(case_obj['_id'], category='str',
        query=query)
    data = controllers.str_variants(store, institute_obj, case_obj,
        variants_query, page)
    return dict(institute=institute_obj, case=case_obj,
        variant_type = variant_type, form=form, page=page, **data)

@variants_bp.route('/<institute_id>/<case_name>/sv/variants',
                   methods=['GET','POST'])
@templated('variants/sv-variants.html')
def sv_variants(institute_id, case_name):
    """Display a list of structural variants."""
    page = int(request.form.get('page', 1))

    variant_type = request.args.get('variant_type', 'clinical')

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)

    form = SvFiltersForm(request.form)

    default_panels = []
    for panel in case_obj['panels']:
        if panel['is_default']:
            default_panels.append(panel['panel_name'])

    request.form.get('gene_panels')
    if bool(request.form.get('clinical_filter')):
        clinical_filter = MultiDict({
            'variant_type': 'clinical',
            'region_annotations': ['exonic','splicing'],
            'functional_annotations': SEVERE_SO_TERMS,
            'thousand_genomes_frequency': str(institute_obj['frequency_cutoff']),
            'variant_type': 'clinical',
            'clingen_ngi': 10,
            'swegen': 10,
            'size': 100,
            'gene_panels': default_panels
             })

    if(request.method == "POST"):
        if bool(request.form.get('clinical_filter')):
            form = SvFiltersForm(clinical_filter)
            form.csrf_token = request.args.get('csrf_token')
        else:
            form = SvFiltersForm(request.form)
    else:
        form = SvFiltersForm(request.args)

    available_panels = case_obj.get('panels', []) + [
        {'panel_name': 'hpo', 'display_name': 'HPO'}]

    panel_choices = [(panel['panel_name'], panel['display_name'])
                     for panel in available_panels]
    form.gene_panels.choices = panel_choices

    if form.data['gene_panels'] == ['hpo']:
        hpo_symbols = list(set(term_obj['hgnc_symbol'] for term_obj in
                               case_obj['dynamic_gene_list']))
        form.hgnc_symbols.data = hpo_symbols

    # update status of case if vistited for the first time
    if case_obj['status'] == 'inactive' and not current_user.is_admin:
        flash('You just activated this case!', 'info')
        user_obj = store.user(current_user.email)
        case_link = url_for('cases.case', institute_id=institute_obj['_id'],
                            case_name=case_obj['display_name'])
        store.update_status(institute_obj, case_obj, user_obj, 'active', case_link)

    variants_query = store.variants(case_obj['_id'], category='sv',
                                    query=form.data)
    data = {}
    # if variants should be exported
    if request.form.get('export'):
        document_header = controllers.variants_export_header(case_obj)
        export_lines = []
        # Return max 500 variants
        export_lines = controllers.variant_export_lines(store, case_obj, variants_query.limit(500))

        def generate(header, lines):
            yield header + '\n'
            for line in lines:
                yield line + '\n'

        headers = Headers()
        headers.add('Content-Disposition','attachment', filename=str(case_obj['display_name'])+'-filtered_sv-variants.csv')
        return Response(generate(",".join(document_header), export_lines), mimetype='text/csv', headers=headers) # return a csv with the exported variants

    else:
        data = controllers.sv_variants(store, institute_obj, case_obj,
                                       variants_query, page)

    return dict(institute=institute_obj, case=case_obj, variant_type=variant_type,
                form=form, severe_so_terms=SEVERE_SO_TERMS, page=page, **data)


@variants_bp.route('/<institute_id>/<case_name>/sv/variants/<variant_id>')
@templated('variants/sv-variant.html')
def sv_variant(institute_id, case_name, variant_id):
    """Display a specific structural variant."""
    data = controllers.sv_variant(store, institute_id, case_name, variant_id)
    return data

@variants_bp.route('/<institute_id>/<case_name>/str/variants/<variant_id>')
@templated('variants/str-variant.html')
def str_variant(institute_id, case_name, variant_id):
    """Display a specific STR variant."""
    data = controllers.str_variant(store, institute_id, case_name, variant_id)
    return data

@variants_bp.route('/<institute_id>/<case_name>/<variant_id>/update', methods=['POST'])
def variant_update(institute_id, case_name, variant_id):
    """Update user-defined information about a variant: manual rank & ACMG."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    user_obj = store.user(current_user.email)
    link = request.referrer

    manual_rank = request.form.get('manual_rank')
    if manual_rank:
        new_manual_rank = int(manual_rank) if manual_rank != '-1' else None
        store.update_manual_rank(institute_obj, case_obj, user_obj, link, variant_obj,
                                 new_manual_rank)
        if new_manual_rank:
            flash("updated variant tag: {}".format(new_manual_rank), 'info')
        else:
            flash("reset variant tag: {}".format(variant_obj.get('manual_rank', 'NA')), 'info')
    elif request.form.get('acmg_classification'):
        new_acmg = request.form['acmg_classification']
        acmg_classification = variant_obj.get('acmg_classification')
        if isinstance(acmg_classification, int) and (new_acmg == ACMG_MAP[acmg_classification]):
            new_acmg = None
        store.update_acmg(institute_obj, case_obj, user_obj, link, variant_obj, new_acmg)
        flash("updated ACMG classification: {}".format(new_acmg), 'info')

    new_dismiss = request.form.getlist('dismiss_variant')
    if request.form.getlist('dismiss_variant'):
        store.update_dismiss_variant(institute_obj, case_obj, user_obj, link, variant_obj,
                                     new_dismiss)
        if new_dismiss:
            flash("Dismissed variant: {}".format(new_dismiss), 'info')

    if variant_obj.get('dismiss_variant') and not new_dismiss:
        if 'dismiss' in request.form:
            store.update_dismiss_variant(institute_obj, case_obj, user_obj, link, variant_obj,
                                     new_dismiss)
            flash("Reset variant dismissal: {}".format(variant_obj.get('dismiss_variant')), 'info')
        else:
            log.debug("DO NOT reset variant dismissal: {}".format(variant_obj.get('dismiss_variant')), 'info')

    mosaic_tags = request.form.getlist('mosaic_tags')
    if mosaic_tags:
        store.update_mosaic_tags(institute_obj, case_obj, user_obj, link, variant_obj,
                                     mosaic_tags)
        if new_dismiss:
            flash("Added mosaic tags: {}".format(mosaic_tags), 'info')

    if variant_obj.get('mosaic_tags') and not mosaic_tags:
        if 'mosaic' in request.form:
            store.update_mosaic_tags(institute_obj, case_obj, user_obj, link, variant_obj,
                                     mosaic_tags)
            flash("Reset mosaic tags: {}".format(variant_obj.get('mosaic_tags')), 'info')

    return redirect(request.referrer)


@variants_bp.route('/<institute_id>/<case_name>/<variant_id>/<variant_category>/<order>', methods=['POST'])
def verify(institute_id, case_name, variant_id, variant_category, order):
    """Start procedure to validate variant using other techniques."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    user_obj = store.user(current_user.email)

    try:
        controllers.variant_verification(store=store, mail=mail, institute_obj=institute_obj, case_obj=case_obj, user_obj=user_obj,
                           variant_obj=variant_obj, sender=current_app.config['MAIL_USERNAME'], variant_url=request.referrer, order=order, url_builder=url_for)
    except controllers.MissingVerificationRecipientError:
        flash('No verification recipients added to institute.', 'danger')

    return redirect(request.referrer)


@variants_bp.route('/<institute_id>/<case_name>/<variant_id>/clinvar', methods=['POST', 'GET'])
@templated('variants/clinvar.html')
def clinvar(institute_id, case_name, variant_id):
    """Build a clinVar submission form for a variant."""
    data = controllers.clinvar_export(store, institute_id, case_name, variant_id)
    if request.method == 'GET':
        return data
    else: #POST
        form_dict = request.form.to_dict()
        submission_objects = set_submission_objects(form_dict) # A tuple of submission objects (variants and casedata objects)

        # Add submission data to an open clinvar submission object,
        # or create a new if no open submission is found in database
        open_submission = store.get_open_clinvar_submission(current_user.email, institute_id)
        updated_submission = store.add_to_submission(open_submission['_id'], submission_objects)

        # Redirect to clinvar submissions handling page, and pass it the updated_submission_object
        return redirect(url_for('cases.clinvar_submissions', institute_id=institute_id))


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
    file = form.symbol_file.data

    if file.filename == '':
        flash('No selected file', 'warning')
        return redirect(request.referrer)

    try:
        stream = io.StringIO(file.stream.read().decode('utf-8'), newline=None)
    except UnicodeDecodeError as error:
        flash("Only text files are supported!", 'warning')
        return redirect(request.referrer)

    category = request.args.get('category')

    if(category == 'sv'):
        form = SvFiltersForm(request.args)
    else:
        form = FiltersForm(request.args)

    hgnc_symbols = set(form.hgnc_symbols.data)
    new_hgnc_symbols = controllers.upload_panel(store, institute_id, case_name, stream)
    hgnc_symbols.update(new_hgnc_symbols)
    form.hgnc_symbols.data = ','.join(hgnc_symbols)
    # reset gene panels
    form.gene_panels.data = ''
    # HTTP redirect code 307 asks that the browser preserves the method of request (POST).
    if(category == 'sv'):
        return redirect(url_for('.sv_variants', institute_id=institute_id, case_name=case_name,
                            **form.data), code=307)
    else:
        return redirect(url_for('.variants', institute_id=institute_id, case_name=case_name,
                            **form.data), code=307)
