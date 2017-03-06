# -*- coding: utf-8 -*-
import os.path

from bson.json_util import dumps
from flask import (abort, Blueprint, current_app, flash, redirect, request,
                   url_for, make_response, Response, render_template)
from flask_login import login_required, current_user
from flask_mail import Message
from housekeeper.store import api
import query_phenomizer

from scout.models import Case, Institute, Variant, HgncGene
from scout.constants import SEVERE_SO_TERMS
from scout.extensions import mail, store, loqusdb, housekeeper
from scout.utils.helpers import templated, validate_user

from .forms import init_filters_form, process_filters_form, GeneListUpload
from .utils import genecov_links
from .constants import PHENOTYPE_GROUPS
from . import controller

core = Blueprint('core', __name__, template_folder='templates',
                 static_folder='static', static_url_path='/core/static')


@core.route('/institutes')
@templated('core/institutes.html')
@login_required
def institutes():
    """View all institutes that the current user belongs to."""
    if current_user.has_role('admin'):
        # show all institutes for admins
        institute_objs = Institute.objects
    else:
        institute_objs = current_user.institutes
    if len(institute_objs) == 1:
        # there no choice of institutes to make, redirect to only institute
        institute = institute_objs[0]
        return redirect(url_for('.cases', institute_id=institute.internal_id))
    else:
        return dict(institutes=controller.institutes(store, institute_objs))


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
    all_cases = store.cases(collaborator=institute_id, name_query=query,
                            skip_assigned=skip_assigned)
    data = controller.cases(all_cases)
    return dict(institute=institute, institute_id=institute_id, query=query,
                skip_assigned=skip_assigned, severe_so_terms=SEVERE_SO_TERMS,
                **data)


@core.route('/<institute_id>/<case_id>')
@templated('core/case.html')
@login_required
def case(institute_id, case_id):
    """View a specific case."""
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)

    irrelevant_ids = ('cust000', inst_mod.internal_id)
    collab_ids = [collab.internal_id for collab in store.institutes() if
                  (collab.internal_id not in irrelevant_ids) and
                  (collab.internal_id not in case_model.collaborators)]

    case_comments = store.events(inst_mod, case=case_model, comments=True)
    case_events = store.events(inst_mod, case=case_model)

    # matching causatives
    causatives = (variant for variant in store.check_causatives(case_model)
                  if variant not in case_model.causatives)

    # # archive date
    # today = datetime.date.today()
    # hk_run = api.runs(case_name=case_model.case_id,
    #                   run_date=case_model.analysis_date).first()
    # if hk_run:
    #     archive_date = hk_run.will_cleanup_at.date()
    #     diff_days = (archive_date - today).days
    #     if diff_days < 0:
    #         # case already to be archived!
    #         status = 'past'
    #     elif diff_days <= 10:
    #         # case is soon to be archived (0-10 days)
    #         status = 'close'
    #     elif diff_days <= 30:
    #         # case is scheduled for archive (11-30 days)
    #         status = 'before'
    #     else:
    #         # case is not to be archived soon (>30 days)
    #         status = 'long'
    #     archive = {
    #         'date': archive_date,
    #         'status': status
    #     }
    # else:
    #     archive = {}

    return dict(institute=inst_mod, case=case_model,
                statuses=Case.status.choices, case_comments=case_comments,
                case_events=case_events, institute_id=institute_id,
                case_id=case_id, collaborators=collab_ids,
                hpo_groups=PHENOTYPE_GROUPS,
                hpo_ids=request.args.getlist('hpo_id'),
                causatives=causatives)


@core.route('/<institute_id>/<case_id>/panels/<panel_id>')
@templated('core/gene-panel.html')
@login_required
def gene_panel(institute_id, case_id, panel_id):
    """Show the list of genes associated with a gene panel."""
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    # coverage link for gene
    covlink_kwargs = genecov_links(case_model.individuals)

    for panel in case_model.gene_panels:
        if panel.panel_name == panel_id:
            gene_panel = panel
    return dict(institute=inst_mod, case=case_model,
                panel=gene_panel, covlink_kwargs=covlink_kwargs)


@core.route('/<institute_id>/<case_id>/assign', methods=['POST'])
def assign_self(institute_id, case_id):
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    link = url_for('.case', institute_id=institute_id, case_id=case_id)
    store.assign(inst_mod, case_model, current_user, link)

    return redirect(url_for('.case', institute_id=institute_id,
                            case_id=case_id))


@core.route('/<institute_id>/<case_id>/unassign', methods=['POST'])
def remove_assignee(institute_id, case_id):
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    link = url_for('.case', institute_id=institute_id, case_id=case_id)
    store.unassign(inst_mod, case_model, current_user, link)

    return redirect(url_for('.case', institute_id=institute_id,
                            case_id=case_id))


@core.route('/<institute_id>/<case_id>/open_research', methods=['POST'])
def open_research(institute_id, case_id):
    """Open the research list for a case."""
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    link = url_for('.case', institute_id=institute_id, case_id=case_id)
    store.open_research(inst_mod, case_model, current_user, link)
    return redirect(url_for('.case', institute_id=institute_id, case_id=case_id))


@core.route('/<institute_id>/<case_id>/phenotype_terms', methods=['POST'])
@core.route('/<institute_id>/<case_id>/phenotype_terms/<phenotype_id>',
            methods=['POST'])
def case_phenotype(institute_id, case_id, phenotype_id=None):
    """Add a new HPO term to the case.

    TODO: validate ID and fetch phenotype description before adding to case.
    """
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    case_url = url_for('.case', institute_id=institute_id, case_id=case_id)
    is_group = request.args.get('is_group') == 'yes'

    if phenotype_id:
        # DELETE a phenotype from the list
        store.remove_phenotype(inst_mod, case_model, current_user,
                               case_url, phenotype_id,
                               is_group=is_group)
    else:
        try:
            # POST a new phenotype to the list
            phenotype_term = request.form['hpo_term']
            if phenotype_term.startswith('HP:') or len(phenotype_term) == 7:
                hpo_term = phenotype_term.split(' | ', 1)[0]
                store.add_phenotype(inst_mod, case_model, current_user,
                                    case_url, hpo_term=hpo_term,
                                    is_group=is_group)
            else:
                # assume omim id
                store.add_phenotype(inst_mod, case_model,
                                    current_user, case_url,
                                    omim_term=phenotype_term)
        except ValueError:
            return abort(400, ("unable to add phenotype term: {}"
                               .format(phenotype_term)))
    return redirect(case_url)


@core.route('/<institute_id>/<case_id>/phenotypes', methods=['POST'])
def phenotypes_gendel(institute_id, case_id):
    """Update the list of genes based on phenotype terms."""
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    case_url = url_for('.case', institute_id=institute_id, case_id=case_id)
    action = request.form['action']
    hpo_ids = request.form.getlist('hpo_id')
    if action == 'DELETE':
        for hpo_id in hpo_ids:
            # DELETE a phenotype from the list
            store.remove_phenotype(inst_mod, case_model, current_user,
                                   case_url, hpo_id)
    elif action == 'PHENOMIZER':
        if len(hpo_ids) == 0:
            hpo_ids = [term.phenotype_id for term in
                       case_model.phenotype_terms]

        username = current_app.config['PHENOMIZER_USERNAME']
        password = current_app.config['PHENOMIZER_PASSWORD']
        diseases = hpo_diseases(username, password, hpo_ids)
        return render_template('core/diseases.html', diseases=diseases,
                               institute=inst_mod, case=case_model)

    elif action == 'GENES':
        hgnc_symbols = set()
        for raw_symbols in request.form.getlist('genes'):
            # avoid empty lists
            if raw_symbols:
                hgnc_symbols.update(raw_symbols.split('|'))
        gene_dicts = [{'gene_id': hgnc_symbol} for hgnc_symbol in hgnc_symbols]
        store.update_dynamic_gene_list(case_model, gene_dicts)

    elif action == 'GENERATE':
        if len(hpo_ids) == 0:
            hpo_ids = [term.phenotype_id for term in
                       case_model.phenotype_terms]
        results = store.generate_hpo_gene_list(*hpo_ids)
        # determine how many HPO terms each gene must match
        hpo_count = int(request.form.get('min_match') or len(hpo_ids))
        gene_ids = [result[0] for result in results if result[1] >= hpo_count]
        hgnc_genes = (HgncGene.objects(hgnc_id__in=gene_ids)
                              .only('hgnc_symbol').select_related())
        hgnc_symbols = [{'gene_id': gene.hgnc_symbol} for gene in hgnc_genes]
        store.update_dynamic_gene_list(case_model, hgnc_symbols)

    return redirect(case_url)


def sampleid_map(case_model):
    # map internal + external sample ids
    sample_map = {"alt_{}".format(sample.individual_id): sample.display_name
                  for sample in case_model.individuals}
    group_id = "alt_{}".format(case_model.case_id)
    sample_map[group_id] = case_model.display_name
    return sample_map


def hpo_diseases(username, password, hpo_ids, p_value_treshold=1):
    """Return the list of HGNC symbols that match annotated HPO terms.

    Args:
        username (str): username to use for phenomizer connection
        password (str): password to use for phenomizer connection

    Returns:
        query_result: a generator of dictionaries on the form
        {
            'p_value': float,
            'disease_source': str,
            'disease_nr': int,
            'gene_symbols': list(str),
            'description': str,
            'raw_line': str
        }
    """
    # skip querying Phenomizer unless at least one HPO terms exists
    try:
        results = query_phenomizer.query(username, password, *hpo_ids)
        diseases = [result for result in results
                    if result['p_value'] <= p_value_treshold]
        return diseases
    except SystemExit:
        return None


@core.route('/<institute_id>/<case_id>/coverage_report', methods=['GET'])
def coverage_report(institute_id, case_id):
    """Serve coverage report for a case directly from the database."""
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
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
    current_gene_lists = [gene_panel for gene_panel
                          in request.args.getlist('gene_panels') if gene_panel]

    # fetch all variants for a specific case
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)

    if case_model is None:
        abort(404)

    skip = int(request.args.get('skip', 0))

    # update case status if currently inactive
    is_admin = current_user.has_role('admin')
    login_off = current_app.config.get('LOGIN_DISABLED')
    case_inactive = case_model.status == 'inactive'
    if (case_inactive and not (is_admin or login_off)):
        link = url_for('.case', institute_id=institute_id, case_id=case_id)
        store.update_status(inst_mod, case_model, current_user, 'active', link)

    # form submitted as GET
    form = init_filters_form(request.args)
    # dynamically add choices to gene lists selection
    if variant_type == 'research':
        if not case_model.is_research:
            # research mode not activated
            return abort(403)

    gene_panel_names = [(item.panel_name, (item.display_name or item.panel_name))
                        for item in case_model.gene_panels]
    form.gene_panels.choices = gene_panel_names

    # make sure HGNC symbols are correctly handled
    if request.args.get('hgnc_symbols'):
        raw_symbols = [symbol.strip().upper() for symbol in
                       request.args.get('hgnc_symbols').split(',') if symbol]
        hgnc_symbols = []
        for hgnc_alias in raw_symbols:
            real_symbol = store.to_hgnc(hgnc_alias)
            if real_symbol:
                hgnc_symbols.append(real_symbol)
                if hgnc_alias != real_symbol:
                    flash("alias: {} -> {}".format(hgnc_alias, real_symbol), "info")
            else:
                flash("couldn't find gene: {}".format(hgnc_alias), "danger")
    else:
        hgnc_symbols = []
    form.hgnc_symbols.data = hgnc_symbols

    # preprocess some of the results before submitting query to adapter
    process_filters_form(form)

    # add variant type to query
    query = dict(**form.data)
    query['clinsig'] = (int(query['clinsig']) if query['clinsig'].isdigit()
                        else None)
    query['variant_type'] = variant_type

    # handle HPO gene list separately
    if query['gene_panels'] == ['hpo']:
        query['hgnc_symbols'] = query['hgnc_symbols'] + case_model.hpo_gene_ids

    # fetch list of variants
    all_variants, count = store.variants(case_model.case_id, query=query,
                                         nr_of_variants=per_page, skip=skip)

    query_dict = {key: request.args.getlist(key) for key in request.args.keys()}
    if 'skip' in query_dict:
        del query_dict['skip']
    return dict(variants=all_variants,
                variants_count=count,
                case=case_model,
                case_id=case_id,
                institute=inst_mod,
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
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    variant_model = store.variant(variant_id, case_model.default_panels)
    if variant_model is None:
        return abort(404, 'variant not found')

    comments = store.events(inst_mod, case=case_model,
                            variant_id=variant_model.variant_id,
                            comments=True)
    events = store.events(inst_mod, case=case_model,
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

    return dict(institute=inst_mod, institute_id=institute_id,
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
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    variant_model = store.variant(document_id=variant_id)
    link = url_for('.variant', institute_id=institute_id, case_id=case_id,
                   variant_id=variant_id)
    store.pin_variant(inst_mod, case_model, current_user, link, variant_model)
    return redirect(request.args.get('next') or request.referrer or link)


@core.route('/<institute_id>/<case_id>/<variant_id>/unpin', methods=['POST'])
def unpin_variant(institute_id, case_id, variant_id):
    """Pin or unpin a variant from the list of suspects."""
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    variant_model = store.variant(document_id=variant_id)
    link = url_for('.variant', institute_id=institute_id, case_id=case_id,
                   variant_id=variant_id)
    store.unpin_variant(inst_mod, case_model, current_user, link,
                        variant_model)
    return redirect(request.args.get('next') or request.referrer or link)


@core.route('/<institute_id>/<case_id>/<variant_id>/mark_causative',
            methods=['POST'])
def mark_causative(institute_id, case_id, variant_id):
    """Mark a variant as confirmed causative."""
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    variant_model = store.variant(document_id=variant_id)
    link = url_for('.variant', institute_id=institute_id,
                   case_id=case_id, variant_id=variant_id)
    case_url = url_for('.case', institute_id=institute_id, case_id=case_id)

    store.mark_causative(inst_mod, case_model, current_user, link,
                         variant_model)

    # send the user back to the case the was marked as solved
    return redirect(case_url)


@core.route('/<institute_id>/<case_id>/<variant_id>/unmark_causative',
            methods=['POST'])
def unmark_causative(institute_id, case_id, variant_id):
    """Remove a variant as confirmed causative for a case."""
    # very basic security check
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    case_url = url_for('.case', institute_id=institute_id, case_id=case_id)

    # skip the host part of the URL to make it more flexible
    link = request.referrer.replace(request.host_url, '/')
    variant_model = store.variant(document_id=variant_id)
    store.unmark_causative(inst_mod, case_model, current_user, link,
                           variant_model)

    # send the user back to the case the was marked as solved
    return redirect(request.referrer or case_url)


@core.route('/<institute_id>/<case_id>/<variant_id>/email-sanger',
            methods=['POST'])
@login_required
def email_sanger(institute_id, case_id, variant_id):
    # very basic security check
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    variant_model = store.variant(document_id=variant_id)

    if variant_model not in case_model.suspects:
        case_model.suspects.append(variant_model)
        case_model.save()

    recipients = inst_mod.sanger_recipients
    if len(recipients) == 0:
        flash('No sanger recipients added to the institute.', 'info')
        return abort(403)

    # build variant page URL
    rel_url = url_for('.variant', institute_id=institute_id,
                      case_id=case_id, variant_id=variant_id)
    variant_url = os.path.join(request.host_url, rel_url)
    hgnc_symbol = ', '.join(variant_model.hgnc_symbols)
    gtcalls = ["<li>{}: {}</li>".format(individual.display_name,
                                        individual.genotype_call)
               for individual in variant_model.samples]
    tx_changes = ["<li>{}</li>".format(transcript.stringify(gene.common.hgnc_symbol))
                  for gene, transcript in variant_model.refseq_transcripts]

    html = """
      <ul">
        <li>
          <strong>Case {case_id}</strong>: <a href="{url}">{variant_id}</a>
        </li>
        <li><strong>HGNC symbols</strong>: {hgnc_symbol}</li>
        <li><strong>Gene panels</strong>: {panels}</li>
        <li><strong>GT call</strong></li>
        {gtcalls}
        <li><strong>Amino acid changes</strong></li>
        {tx_changes}
        <li><strong>Ordered by</strong>: {name}</li>
      </ul>
    """.format(case_id=case_id,
               url=variant_url,
               variant_id=variant_model.display_name,
               hgnc_symbol=hgnc_symbol,
               panels=', '.format(variant_model.panels),
               gtcalls=''.join(gtcalls),
               tx_changes=''.join(tx_changes),
               name=current_user.name.encode('utf-8'))

    kwargs = dict(subject="SCOUT: Sanger sequencing of %s" % hgnc_symbol,
                  html=html,
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=recipients,
                  # cc the sender of the email for confirmation
                  cc=[current_user.email])

    # compose and send the email message
    msg = Message(**kwargs)
    mail.send(msg)

    store.order_sanger(inst_mod, case_model, current_user, variant_url,
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
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    variant_model = store.variant(document_id=variant_id)
    validate_type = request.form['type'] or None
    variant_link = url_for('.variant', institute_id=institute_id,
                           case_id=case_id, variant_id=variant_id)
    store.validate(inst_mod, case_model, current_user, variant_link,
                   variant_model, validate_type)
    return redirect(request.referrer)


@core.route('/pileup/range')
def pileup_range():
    """Build a proper call to the pileup viewer for a given range."""
    positions = dict(contig=request.args['chrom'], start=request.args['start'],
                     stop=request.args['end'])
    # replace first instance of separator (can be part of case id)
    institute_id, case_id = request.args['group'].split('-', 1)
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    link = url_for('pileup.viewer', bam=case_model.bam_files,
                   bai=case_model.bai_files, sample=case_model.sample_names,
                   vcf=case_model.vcf_file, **positions)
    return redirect(link)


@core.route('/<institute_id>/<case_id>/share', methods=['POST'])
def share_case(institute_id, case_id):
    """Share a case with a different institute."""
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    collaborator_id = request.form['collaborator']
    revoke_access = 'revoke' in request.form
    link = url_for('.case', institute_id=institute_id, case_id=case_id)

    if revoke_access:
        store.unshare(inst_mod, case_model, collaborator_id, current_user, link)
    else:
        store.share(inst_mod, case_model, collaborator_id, current_user, link)

    return redirect(request.referrer)


@core.route('/<institute_id>/<case_id>/rerun', methods=['POST'])
def request_rerun(institute_id, case_id):
    """Request a case to be rerun."""
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    link = url_for('.case', institute_id=institute_id, case_id=case_id)
    store.request_rerun(inst_mod, case_model, current_user, link)

    # send email to trigger manual load of research variants
    main_recipient = current_app.config['RESEARCH_MODE_RECIPIENT']

    # this should send a JSON document to the SuSy API in the future
    html = """
        <p>{institute}: {case} ({case_id})</p>
        <p>Re-run requested by: {name}</p>
    """.format(institute=inst_mod.display_name,
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
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    link = url_for('.case', institute_id=institute_id, case_id=case_id)
    level = 'phenotype' if 'phenotype' in request.form else 'gene'
    omim_id = request.form['omim_id']
    remove = True if 'remove' in request.args else False
    store.diagnose(inst_mod, case_model, current_user, link, level=level,
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
    inst_mod, case_model = validate_user(current_user, institute_id, case_id)
    hk_run = api.runs(case_name=case_model.case_id,
                      run_date=case_model.analyzed_at).first()
    api.postpone(hk_run)
    new_date = hk_run.will_cleanup_at.date()
    flash("updated archive date to: {}".format(new_date), 'info')
    housekeeper.manager.commit()
    return redirect(request.referrer)
