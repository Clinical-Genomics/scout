# -*- coding: utf-8 -*-
import datetime
import itertools
import os.path

from bson.json_util import dumps
from flask import (abort, Blueprint, current_app, flash, redirect, request,
                   url_for, make_response, Response)
from flask_login import login_required, current_user
from flask_mail import Message
from housekeeper.store import api
import query_phenomizer

from scout.models import Case, Variant
from scout.models.case import STATUS as CASE_STATUSES
from scout.constants import SEVERE_SO_TERMS
from scout.extensions import mail, store, loqusdb, housekeeper
from scout.utils.helpers import templated, validate_user

from .forms import init_filters_form, process_filters_form, GeneListUpload
from .utils import genecov_links
from .constants import PHENOTYPE_GROUPS

core = Blueprint('core', __name__, template_folder='templates',
                 static_folder='static', static_url_path='/core/static')


@core.route('/institutes')
@templated('core/institutes.html')
@login_required
def institutes():
    """View all institutes that the current user belongs to."""
    institute_objs = current_user.institutes
    if len(institute_objs) == 1:
        # there no choice of institutes to make, redirect to only institute
        institute = institute_objs[0]
        return redirect(url_for('.cases', institute_id=institute.internal_id))
    else:
        return dict(institutes=institute_objs, Case=Case)


@core.route('/institutes/<institute_id>/settings', methods=['POST'])
@login_required
def institute_settings(institute_id):
    """Update institute settings."""
    inst_mod = validate_user(current_user, institute_id)
    inst_mod.coverage_cutoff = int(request.form['coverage_cutoff'])
    inst_mod.frequency_cutoff = float(request.form['frequency_cutoff'])
    inst_mod.save()
    return redirect(request.referrer)


@core.route('/<institute_id>')
@templated('core/cases.html')
@login_required
def cases(institute_id):
    """View all cases.

    The purpose of this page is to display all cases related to an institute.
    """
    query = request.args.get('query')
    skip_assigned = request.args.get('skip_assigned')
    institute = validate_user(current_user, institute_id)
    case_models = store.cases(collaborator=institute_id, query=query,
                              skip_assigned=skip_assigned)
    prio_cases = case_models.filter(status=CASE_STATUSES[0])
    case_groups = []
    for case_status in CASE_STATUSES[1:]:
        case_groups.append((case_status, case_models.filter(status=case_status)))

    missed_cutoff = datetime.datetime(2016, 2, 19)
    return dict(institute=institute, institute_id=institute_id,
                cases=case_groups, found_cases=len(case_models), query=query,
                skip_assigned=skip_assigned, severe_so_terms=SEVERE_SO_TERMS,
                missed_cutoff=missed_cutoff, prio_cases=prio_cases)


@core.route('/<institute_id>/<case_id>')
@templated('core/case.html')
@login_required
def case(institute_id, case_id):
    """View a specific case."""
    inst_mod = validate_user(current_user, institute_id)

    # fetch a single, specific case from the data store
    case_model = store.case(institute_id, case_id)
    if case_model is None:
        return abort(404, "Can't find a case '{}' for institute {}"
                          .format(case_id, institute_id))

    irrelevant_ids = ('cust000', inst_mod.display_name)
    collab_ids = [collab.display_name for collab in store.institutes() if
                  (collab.display_name not in irrelevant_ids) and
                  (collab.display_name not in case_model.collaborators)]

    case_comments = store.events(inst_mod, case=case_model, comments=True)
    case_events = store.events(inst_mod, case=case_model)

    # matching causatives
    causatives = (variant for variant in store.check_causatives(case_model)
                  if variant not in case_model.causatives)

    # archive date
    today = datetime.date.today()
    hk_run = api.runs(case_name=case_model.case_id,
                      run_date=case_model.analysis_date).first()
    if hk_run:
        archive_date = hk_run.will_cleanup_at.date()
        diff_days = (archive_date - today).days
        if diff_days < 0:
            # case already to be archived!
            status = 'past'
        elif diff_days <= 10:
            # case is soon to be archived (0-10 days)
            status = 'close'
        elif diff_days <= 30:
            # case is scheduled for archive (11-30 days)
            status = 'before'
        else:
            # case is not to be archived soon (>30 days)
            status = 'long'
        archive = {
            'date': archive_date,
            'status': status
        }
    else:
        archive = {}

    return dict(institute=inst_mod, case=case_model,
                statuses=Case.status.choices, case_comments=case_comments,
                case_events=case_events, institute_id=institute_id,
                case_id=case_id, collaborators=collab_ids,
                hpo_groups=PHENOTYPE_GROUPS,
                hpo_ids=request.args.getlist('hpo_id'),
                causatives=causatives, archive=archive)


@core.route('/<institute_id>/<case_id>/panels/<panel_id>')
@templated('core/gene-panel.html')
@login_required
def gene_panel(institute_id, case_id, panel_id):
    """Show the list of genes associated with a gene panel."""
    institute_model = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)

    # coverage link for gene
    covlink_kwargs = genecov_links(case_model.individuals)

    for panel in case_model.gene_panels:
        if panel.panel_name == panel_id:
            gene_panel = panel
    return dict(institute=institute_model, case=case_model,
                panel=gene_panel, covlink_kwargs=covlink_kwargs)


@core.route('/<institute_id>/<case_id>/assign', methods=['POST'])
def assign_self(institute_id, case_id):
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)

    link = url_for('.case', institute_id=institute_id, case_id=case_id)
    store.assign(institute, case_model, current_user, link)

    return redirect(url_for('.case', institute_id=institute_id,
                            case_id=case_id))


@core.route('/<institute_id>/<case_id>/unassign', methods=['POST'])
def remove_assignee(institute_id, case_id):
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)

    link = url_for('.case', institute_id=institute_id, case_id=case_id)
    store.unassign(institute, case_model, current_user, link)

    return redirect(url_for('.case', institute_id=institute_id,
                            case_id=case_id))


@core.route('/<institute_id>/<case_id>/open_research', methods=['POST'])
def open_research(institute_id, case_id):
    """Open the research list for a case."""
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)

    # send email to trigger manual load of research variants
    main_recipient = current_app.config['RESEARCH_MODE_RECIPIENT']

    # this should send a JSON document to the SuSy API in the future
    html = """
        <p>{institute}: {case} ({case_id})</p>
        <p>Requested by: {name}</p>
    """.format(institute=institute.display_name, case=case_model.display_name,
               case_id=case_model.id, name=current_user.name.encode('utf-8'))

    # compose and send the email message
    msg = Message(subject=("SCOUT: open research mode for {}"
                           .format(case_model.display_name)),
                  html=html,
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[main_recipient],
                  # cc the sender of the email for confirmation
                  cc=[current_user.email])
    mail.send(msg)

    link = url_for('.case', institute_id=institute_id, case_id=case_id)
    store.open_research(institute, case_model, current_user, link)

    return redirect(url_for('.case', institute_id=institute_id,
                            case_id=case_id))


@core.route('/<institute_id>/<case_id>/phenotype_terms', methods=['POST'])
@core.route('/<institute_id>/<case_id>/phenotype_terms/<phenotype_id>',
            methods=['POST'])
def case_phenotype(institute_id, case_id, phenotype_id=None):
    """Add a new HPO term to the case.

    TODO: validate ID and fetch phenotype description before adding to case.
    """
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)
    case_url = url_for('.case', institute_id=institute_id, case_id=case_id)
    is_group = request.args.get('is_group') == 'yes'

    if phenotype_id:
        # DELETE a phenotype from the list
        store.remove_phenotype(institute, case_model, current_user,
                               case_url, phenotype_id,
                               is_group=is_group)
    else:
        try:
            # POST a new phenotype to the list
            phenotype_term = request.form['hpo_term']
            if phenotype_term.startswith('HP:') or len(phenotype_term) == 7:
                hpo_term = phenotype_term.split(' | ', 1)[0]
                store.add_phenotype(institute, case_model, current_user,
                                    case_url, hpo_term=hpo_term,
                                    is_group=is_group)
            else:
                # assume omim id
                store.add_phenotype(institute, case_model,
                                    current_user, case_url,
                                    omim_term=phenotype_term)
        except ValueError:
            return abort(400, ("unable to add phenotype term: {}"
                               .format(phenotype_term)))
    return redirect(case_url)


@core.route('/<institute_id>/<case_id>/phenotypes', methods=['POST'])
def phenotypes_gendel(institute_id, case_id):
    """Update the list of genes based on phenotype terms."""
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)
    case_url = url_for('.case', institute_id=institute_id, case_id=case_id)
    action = request.form['action']
    hpo_ids = request.form.getlist('hpo_id')
    if action == 'DELETE':
        for hpo_id in hpo_ids:
            # DELETE a phenotype from the list
            store.remove_phenotype(institute, case_model, current_user,
                                   case_url, hpo_id)
    elif action == 'GENERATE':
        if len(hpo_ids) == 0:
            hpo_ids = [term.phenotype_id for term in
                       case_model.phenotype_terms]
        update_hpolist(case_model, hpo_ids=hpo_ids)
        case_url = url_for('.case', institute_id=institute_id,
                           case_id=case_id, hpo_id=hpo_ids)

    return redirect(case_url)


def update_hpolist(case_model, hpo_ids):
    # fetch genes to update dynamic gene list
    try:
        username = current_app.config['PHENOMIZER_USERNAME']
        password = current_app.config['PHENOMIZER_PASSWORD']
        gene_ids = [{'gene_id': gene_id} for gene_id in
                    hpo_genes(username, password, hpo_ids)]
    except KeyError:
        gene_ids = []
    store.update_dynamic_gene_list(case_model, gene_ids)


def sampleid_map(case_model):
    # map internal + external sample ids
    sample_map = {"alt_{}".format(sample.individual_id): sample.display_name
                  for sample in case_model.individuals}
    group_id = "alt_{}".format(case_model.case_id)
    sample_map[group_id] = case_model.display_name
    return sample_map


def hpo_genes(username, password, hpo_ids):
    """Return the list of HGNC symbols that match annotated HPO terms.

    Args:
        username (str): username to use for phenomizer connection
        password (str): password to use for phenomizer connection

    Returns:
        query_result: a list of dictionaries on the form
        {
            'p_value': float,
            'gene_id': str,
            'omim_id': int,
            'orphanet_id': int,
            'decipher_id': int,
            'any_id': int,
            'mode_of_inheritance': str,
            'description': str,
            'raw_line': str
        }
    """
    # skip querying Phenomizer unless at least one HPO terms exists
    try:
        results = query_phenomizer.query(username, password, hpo_ids)
        nested_genes = [result['gene_id'].split(', ') for result in results
                        if result['gene_id'] and result['p_value'] is not None]
        return list(set(itertools.chain.from_iterable(nested_genes)))
    except SystemExit:
        return None


@core.route('/<institute_id>/<case_id>/coverage_report', methods=['GET'])
def coverage_report(institute_id, case_id):
    """Serve coverage report for a case directly from the database."""
    validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)

    response = make_response(case_model.coverage_report)
    response.headers['Content-Type'] = 'application/pdf'
    filename = "{}.coverage.pdf".format(case_model.display_name)
    response.headers['Content-Disposition'] = ("inline; filename={}.pdf"
                                               .format(filename))
    return response


def read_lines(iterable):
    """Handle both CR line endings and normal endings."""
    new_lines = ((nested_line for nested_line in
                  line.rstrip().replace('\r', '\n').split('\n'))
                 for line in iterable if not line.startswith('#'))

    # flatten nested lists
    return (item for sublist in new_lines for item in sublist)


@core.route('/upload-gene-list', methods=['POST'])
@login_required
def upload_gene_list():
    """Upload HGNC symbols to dynamically generate a gene list."""
    gene_list = request.files.get('gene_list')
    if gene_list:
        # file found
        hgnc_symbols = read_lines(gene_list)
    else:
        hgnc_symbols = []

    referrer_url = request.referrer.partition('?')[0]
    new_url = "{}?hgnc_symbols={}".format(referrer_url, ','.join(hgnc_symbols))

    # redirect to variants list without old filters
    return redirect(new_url)


@core.route('/<institute_id>/<case_id>/<variant_type>',
            methods=['GET', 'POST'])
@templated('core/variants.html')
@login_required
def variants(institute_id, case_id, variant_type):
    """View all variants for a single case."""
    per_page = 50
    current_gene_lists = [gene_list for gene_list
                          in request.args.getlist('gene_lists') if gene_list]

    # fetch all variants for a specific case
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)

    if case_model is None:
        abort(404)

    skip = int(request.args.get('skip', 0))

    # update case status if currently inactive
    if (case_model.status == 'inactive' and not
            current_app.config.get('LOGIN_DISABLED')):
        link = url_for('.case', institute_id=institute_id, case_id=case_id)
        store.update_status(institute, case_model, current_user, 'active',
                            link)

    # form submitted as GET
    form = init_filters_form(request.args)
    # dynamically add choices to gene lists selection
    if variant_type == 'research':
        if not case_model.is_research:
            # research mode not activated
            return abort(403)

    gene_list_names = [(item.panel_name, (item.display_name or item.panel_name))
                       for item in case_model.gene_panels]
    form.gene_lists.choices = gene_list_names

    # make sure HGNC symbols are correctly handled
    if request.args.get('hgnc_symbols'):
        raw_hgncids = [hgnc_id.strip().upper() for hgnc_id in
                       request.args.get('hgnc_symbols').split(',') if hgnc_id]
        hgnc_ids = []
        for hgnc_alias in raw_hgncids:
            real_id = store.to_hgnc(hgnc_alias)
            if real_id:
                hgnc_ids.append(real_id)
                if hgnc_alias != real_id:
                    flash("alias: {} -> {}".format(hgnc_alias, real_id), "info")
            else:
                flash("couldn't find HGNC id: {}".format(hgnc_alias), "error")
    else:
        hgnc_ids = []
    form.hgnc_symbols.data = hgnc_ids

    # preprocess some of the results before submitting query to adapter
    process_filters_form(form)

    # add variant type to query
    query = dict(**form.data)
    query['clinsig'] = (int(query['clinsig']) if query['clinsig'].isdigit()
                        else None)
    query['variant_type'] = variant_type

    # handle HPO gene list separately
    if query['gene_lists'] == ['hpo']:
        query['hgnc_symbols'] = case_model.hpo_gene_ids
    else:
        # get HGNC symbols from selected gene panels
        gene_symbols = set(query['hgnc_symbols'])
        for panel_id in query['gene_lists']:
            panel_obj = store.gene_panel(panel_id)
            gene_symbols.update(panel_obj.gene_symbols)
        query['hgnc_symbols'] = list(gene_symbols)

    # fetch list of variants
    all_variants, count = store.variants(case_model.case_id, query=query,
                                         nr_of_variants=per_page, skip=skip)

    query_dict = {key: request.args.getlist(key) for key in request.args.keys()}
    return dict(variants=all_variants,
                variants_count=count,
                case=case_model,
                case_id=case_id,
                institute=institute,
                institute_id=institute_id,
                current_batch=(skip + per_page),
                per_page=per_page,
                form=form,
                severe_so_terms=SEVERE_SO_TERMS,
                current_gene_lists=current_gene_lists,
                variant_type=variant_type,
                upload_form=GeneListUpload(),
                query_dict=query_dict)


@core.route('/<institute_id>/<case_id>/variants/<variant_id>')
@templated('core/variant.html')
@login_required
def variant(institute_id, case_id, variant_id):
    """View a single variant in a single case."""
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)
    variant_model = store.variant(variant_id, case_model.default_panels)
    if variant_model is None:
        return abort(404, 'variant not found')

    comments = store.events(institute, case=case_model,
                            variant_id=variant_model.variant_id,
                            comments=True)
    events = store.events(institute, case=case_model,
                          variant_id=variant_model.variant_id)

    individuals = {individual.individual_id: individual
                   for individual in case_model.individuals}

    # coverage link for gene
    coverage_links = genecov_links(case_model.individuals,
                                   variant_model.genes)

    prev_variant = store.previous_variant(document_id=variant_id)
    next_variant = store.next_variant(document_id=variant_id)

    local_freq = loqusdb.get_variant({'_id': variant_model.composite_id})
    local_total = loqusdb.case_count()

    causatives = store.other_causatives(case_model, variant_model)

    # overlapping SVs
    overlapping_svs = store.overlapping(variant_model)

    return dict(institute=institute, institute_id=institute_id,
                case=case_model, case_id=case_id,
                variant=variant_model, variant_id=variant_id,
                comments=comments, events=events,
                prev_variant=prev_variant, next_variant=next_variant,
                manual_rank_options=Variant.manual_rank.choices,
                individuals=individuals, coverage_links=coverage_links,
                local_freq=local_freq, local_total=local_total,
                causatives=causatives, overlapping_svs=overlapping_svs)


@core.route('/<institute_id>/<case_id>/<variant_id>/pin', methods=['POST'])
def pin_variant(institute_id, case_id, variant_id):
    """Pin or unpin a variant from the list of suspects."""
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)
    variant_model = store.variant(document_id=variant_id)
    link = url_for('.variant', institute_id=institute_id, case_id=case_id,
                   variant_id=variant_id)
    store.pin_variant(institute, case_model, current_user, link, variant_model)
    return redirect(request.args.get('next') or request.referrer or link)


@core.route('/<institute_id>/<case_id>/<variant_id>/unpin', methods=['POST'])
def unpin_variant(institute_id, case_id, variant_id):
    """Pin or unpin a variant from the list of suspects."""
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)
    variant_model = store.variant(document_id=variant_id)
    link = url_for('.variant', institute_id=institute_id, case_id=case_id,
                   variant_id=variant_id)
    store.unpin_variant(institute, case_model, current_user, link,
                        variant_model)
    return redirect(request.args.get('next') or request.referrer or link)


@core.route('/<institute_id>/<case_id>/<variant_id>/mark_causative',
            methods=['POST'])
def mark_causative(institute_id, case_id, variant_id):
    """Mark a variant as confirmed causative."""
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)
    variant_model = store.variant(document_id=variant_id)
    link = url_for('.variant', institute_id=institute_id,
                   case_id=case_id, variant_id=variant_id)
    case_url = url_for('.case', institute_id=institute_id, case_id=case_id)

    store.mark_causative(institute, case_model, current_user, link,
                         variant_model)

    # send the user back to the case the was marked as solved
    return redirect(case_url)


@core.route('/<institute_id>/<case_id>/<variant_id>/unmark_causative',
            methods=['POST'])
def unmark_causative(institute_id, case_id, variant_id):
    """Remove a variant as confirmed causative for a case."""
    # very basic security check
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)
    case_url = url_for('.case', institute_id=institute_id, case_id=case_id)

    # skip the host part of the URL to make it more flexible
    link = request.referrer.replace(request.host_url, '/')
    variant_model = store.variant(document_id=variant_id)
    store.unmark_causative(institute, case_model, current_user, link,
                           variant_model)

    # send the user back to the case the was marked as solved
    return redirect(request.referrer or case_url)


@core.route('/<institute_id>/<case_id>/<variant_id>/email-sanger',
            methods=['POST'])
@login_required
def email_sanger(institute_id, case_id, variant_id):
    # very basic security check
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)
    variant_model = store.variant(document_id=variant_id)

    if variant_model not in case_model.suspects:
        case_model.suspects.append(variant_model)
        case_model.save()

    recipients = institute.sanger_recipients
    if len(recipients) == 0:
        flash('No sanger recipients added to the institute.')
        return abort(403)

    # build variant page URL
    rel_url = url_for('.variant', institute_id=institute_id,
                      case_id=case_id, variant_id=variant_id)
    variant_url = os.path.join(request.host_url, rel_url)
    gene_lists_str = ', '.join(variant_model.gene_lists)

    hgnc_symbol = ', '.join(variant_model.hgnc_symbols)
    functions = ["<li>{}</li>".format(function) for function in
                 variant_model.protein_changes]
    gtcalls = ["<li>{}: {}</li>".format(individual.display_name,
                                        individual.genotype_call)
               for individual in variant_model.samples]

    html = """
      <p>Case {case_id}: {variant_id}</p>
      <p>Scout link: {url}</p>
      <p>HGNC symbol: {hgnc_symbol}</p>
      <p>Database: {databases}</p>
      <p>Chr position: {chromosome_position}</p>
      <p>Amino acid change(s): <br> <ul>{functions}</ul></p><br>
      <p>GT-call: <br> <ul>{gtcalls}</ul></p><br>
      <p>Ordered by: {name}</p>
    """.format(
      case_id=case_id,
      url=variant_url,
      variant_id=variant_model.display_name,
      hgnc_symbol=hgnc_symbol,
      databases=gene_lists_str,
      chromosome_position=variant_model.display_name,
      functions=''.join(functions),
      gtcalls=''.join(gtcalls),
      name=current_user.name.encode('utf-8')
    )

    kwargs = dict(
      subject="SCOUT: Sanger sequencing of %s" % hgnc_symbol,
      html=html,
      sender=current_app.config['MAIL_USERNAME'],
      recipients=recipients,
      # cc the sender of the email for confirmation
      cc=[current_user.email]
    )

    # compose and send the email message
    msg = Message(**kwargs)
    mail.send(msg)

    store.order_sanger(institute, case_model, current_user, variant_url,
                       variant_model)

    return redirect(variant_url)


@core.route('/<institute_id>/<case_id>/complete', methods=['POST'])
def mark_checked(institute_id, case_id):
    """Mark a case as complete in term of the analysis."""
    # fetch all variants for a specific case
    institute_model = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)

    unmark = 'unmark' in request.form
    store.mark_checked(institute_model, case_model, current_user,
                       request.referrer, unmark=unmark)

    return redirect(request.referrer)


@core.route('/<institute_id>/<case_id>/<variant_id>/validate', methods=['POST'])
def mark_validation(institute_id, case_id, variant_id):
    """Mark a variant as sanger validated."""
    institute_model = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)
    variant_model = store.variant(document_id=variant_id)
    validate_type = request.form['type'] or None
    variant_link = url_for('.variant', institute_id=institute_id,
                           case_id=case_id, variant_id=variant_id)
    store.validate(institute_model, case_model, current_user, variant_link,
                   variant_model, validate_type)
    return redirect(request.referrer)


@core.route('/pileup/range')
def pileup_range():
    """Build a proper call to the pileup viewer for a given range."""
    positions = dict(contig=request.args['chrom'], start=request.args['start'],
                     stop=request.args['end'])
    # replace first instance of separator (can be part of case id)
    institute_id, case_id = request.args['group'].split('-', 1)
    validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)
    link = url_for('pileup.viewer', bam=case_model.bam_files,
                   bai=case_model.bai_files, sample=case_model.sample_names,
                   vcf=case_model.vcf_file, **positions)
    return redirect(link)


@core.route('/<institute_id>/<case_id>/share', methods=['POST'])
def share_case(institute_id, case_id):
    """Share a case with a different institute."""
    institute_model = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)

    collaborator_id = request.form['collaborator']
    revoke_access = 'revoke' in request.form
    link = url_for('.case', institute_id=institute_id, case_id=case_id)

    if revoke_access:
        store.unshare(institute_model, case_model, collaborator_id,
                      current_user, link)
    else:
        store.share(institute_model, case_model, collaborator_id,
                    current_user, link)

    return redirect(request.referrer)


@core.route('/<institute_id>/<case_id>/rerun', methods=['POST'])
def request_rerun(institute_id, case_id):
    """Request a case to be rerun."""
    institute_model = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)

    link = url_for('.case', institute_id=institute_id, case_id=case_id)
    store.request_rerun(institute_model, case_model, current_user, link)

    # send email to trigger manual load of research variants
    main_recipient = current_app.config['RESEARCH_MODE_RECIPIENT']

    # this should send a JSON document to the SuSy API in the future
    html = """
        <p>{institute}: {case} ({case_id})</p>
        <p>Re-run requested by: {name}</p>
    """.format(institute=institute_model.display_name,
               case=case_model.display_name, case_id=case_model.id,
               name=current_user.name.encode('utf-8'))

    # compose and send the email message
    msg = Message(subject=("SCOUT: request re-run for {}"
                           .format(case_model.display_name)),
                  html=html,
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[main_recipient],
                  # cc the sender of the email for confirmation
                  cc=[current_user.email])
    mail.send(msg)

    return redirect(request.referrer)


@core.route('/<institute_id>/<case_id>/diagnose', methods=['POST'])
def case_diagnosis(institute_id, case_id):
    """Pin or unpin a variant from the list of suspects."""
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)
    link = url_for('.case', institute_id=institute_id, case_id=case_id)
    level = 'phenotype' if 'phenotype' in request.form else 'gene'
    omim_id = request.form['omim_id']
    remove = True if 'remove' in request.args else False
    store.diagnose(institute, case_model, current_user, link, level=level,
                   omim_id=omim_id, remove=remove)
    return redirect(request.args.get('next') or request.referrer or link)


@core.route('/api/v1/hpo-terms')
def hpoterms():
    """Search for HPO terms."""
    query = request.args.get('query')
    if query is None:
        return abort(500)
    terms = store.hpo_terms(query=query).limit(8)
    json_terms = [{'name': '{} | {}'.format(term.hpo_id, term.description),
                   'id': term.hpo_id} for term in terms]
    return Response(dumps(json_terms),
                    mimetype='application/json; charset=utf-8')


@core.route('/api/v1/<institute_id>/cases/<case_id>/postpone', methods=['POST'])
def postpone(institute_id, case_id):
    """Postpone the clean up (archive) date of a case."""
    validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)
    hk_run = api.runs(case_name=case_model.case_id,
                      run_date=case_model.analyzed_at).first()
    api.postpone(hk_run)
    new_date = hk_run.will_cleanup_at.date()
    flash("updated archive date to: {}".format(new_date), 'info')
    housekeeper.manager.commit()
    return redirect(request.referrer)
