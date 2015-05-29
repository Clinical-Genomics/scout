# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from flask import (abort, Blueprint, current_app, flash, redirect, request,
                   url_for, make_response)
from flask.ext.login import login_required, current_user
from flask.ext.mail import Message
import query_phenomizer

from scout.models import Case, Variant
from scout.extensions import mail, store
from scout.helpers import templated

from .forms import (init_filters_form, SO_TERMS, process_filters_form,
                    GeneListUpload)
from .utils import validate_user

core = Blueprint('core', __name__, template_folder='templates')


@core.route('/institutes')
@templated('institutes.html')
@login_required
def institutes():
  """View all institutes that the current user belongs to."""
  if len(current_user.institutes) == 1:
    # there no choice of institutes to make, redirect to only institute
    institute = current_user.institutes[0]
    return redirect(url_for('.cases', institute_id=institute.display_name))

  else:
    return dict(institutes=current_user.institutes)


@core.route('/<institute_id>')
@templated('cases.html')
@login_required
def cases(institute_id):
  """View all cases.

  The purpose of this page is to display all cases related to an institute.
  """
  institute = validate_user(current_user, institute_id)
  return dict(institute=institute, institute_id=institute_id)


@core.route('/<institute_id>/<case_id>')
@templated('case.html')
@login_required
def case(institute_id, case_id):
  """View a specific case."""
  institute = validate_user(current_user, institute_id)

  # fetch a single, specific case from the data store
  case_model = store.case(institute_id, case_id)

  case_comments = store.events(institute, case=case_model, comments=True)
  case_events = store.events(institute, case=case_model)

  return dict(institute=institute, case=case_model, statuses=Case.status.choices,
              case_comments=case_comments, case_events=case_events,
              institute_id=institute_id, case_id=case_id)


@core.route('/<institute_id>/<case_id>/assign', methods=['POST'])
def assign_self(institute_id, case_id):
  institute = validate_user(current_user, institute_id)
  case_model = store.case(institute_id, case_id)

  link = url_for('.case', institute_id=institute_id, case_id=case_id)
  store.assign(institute, case_model, current_user, link)

  return redirect(url_for('.case', institute_id=institute_id, case_id=case_id))


@core.route('/<institute_id>/<case_id>/unassign', methods=['POST'])
def remove_assignee(institute_id, case_id):
  institute = validate_user(current_user, institute_id)
  case_model = store.case(institute_id, case_id)

  link = url_for('.case', institute_id=institute_id, case_id=case_id)
  store.unassign(institute, case_model, current_user, link)

  return redirect(url_for('.case', institute_id=institute_id, case_id=case_id))


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
             case_id=case_model.id, name=current_user.name)

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

  return redirect(url_for('.case', institute_id=institute_id, case_id=case_id))


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

  if phenotype_id:
    # DELETE a phenotype from the list
    store.remove_phenotype(institute, case_model, current_user, case_url, phenotype_id)

  else:
    # POST a new phenotype to the list
    hpo_term = request.form['hpo_term']
    store.add_phenotype(institute, case_model, current_user, case_url, hpo_term)

  # fetch genes to update dynamic gene list
  genes = hpo_genes(case_model.phenotype_terms)
  store.update_dynamic_gene_list(case_model, genes)

  return redirect(case_url)


def hpo_genes(phenotype_terms):
  """Return the list of HGNC symbols that match annotated HPO terms.

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
  hpo_terms = [phenotype_term.phenotype_id for phenotype_term in phenotype_terms]

  # skip querying Phenomizer unless at least one HPO terms exists
  if hpo_terms:
    try:
      results = query_phenomizer.query(hpo_terms)
      return [result for result in results if result['p_value'] is not None]
    except SystemExit:
      return None
  else:
    return None


@core.route('/<institute_id>/<case_id>/coverage_report', methods=['GET'])
def coverage_report(institute_id, case_id):
  """Serve coverage report for a case directly from the database."""
  institute = validate_user(current_user, institute_id)
  case_model = store.case(institute_id, case_id)

  response = make_response(case_model.coverage_report)
  response.headers['Content-Type'] = 'application/pdf'
  filename = "{}.coverage.pdf".format(case_model.display_name)
  response.headers['Content-Disposition'] = "inline; filename={}.pdf".format(filename)
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


@core.route('/<institute_id>/<case_id>/<variant_type>', methods=['GET', 'POST'])
@templated('variants.html')
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
  if case_model.status == 'inactive':
    link = url_for('.case', institute_id=institute_id, case_id=case_id)
    store.update_status(institute, case_model, current_user, 'active', link)

  # form submitted as GET
  form = init_filters_form(request.args)
  # dynamically add choices to gene lists selection
  if variant_type == 'research':
    if case_model.is_research:
      gene_lists = case_model.all_gene_lists
    else:
      # research mode not activated
      return abort(403)
  else:
    gene_lists = case_model.clinical_gene_lists

  gene_list_names = [(item.list_id, item.display_name) for item in gene_lists]
  form.gene_lists.choices = gene_list_names
  # make sure HGNC symbols are correctly handled
  form.hgnc_symbols.data = [gene for gene in
                            request.args.getlist('hgnc_symbols') if gene]

  # preprocess some of the results before submitting query to adapter
  process_filters_form(form)

  # add variant type to query
  query = dict(**form.data)
  query['variant_type'] = variant_type

  # fetch list of variants
  variant_models = store.variants(case_model.case_id, query=query,
                                  nr_of_variants=per_page, skip=skip)

  return dict(variants=variant_models,
              case=case_model,
              case_id=case_id,
              institute=institute,
              institute_id=institute_id,
              current_batch=(skip + per_page),
              form=form,
              severe_so_terms=SO_TERMS[:11] + ('incomplete_terminal_codon_variant',
                                               'stop_retained_variant'),
              current_gene_lists=current_gene_lists,
              variant_type=variant_type,
              upload_form=GeneListUpload())


@core.route('/<institute_id>/<case_id>/variants/<variant_id>')
@templated('variant.html')
@login_required
def variant(institute_id, case_id, variant_id):
  """View a single variant in a single case."""
  institute = validate_user(current_user, institute_id)
  case_model = store.case(institute_id, case_id)
  variant_model = store.variant(document_id=variant_id)

  comments = store.events(institute, case=case_model,
                          variant_id=variant_model.variant_id,
                          comments=True)
  events = store.events(institute, case=case_model, variant_id=variant_model.variant_id)

  prev_variant = store.previous_variant(document_id=variant_id)
  next_variant = store.next_variant(document_id=variant_id)

  return dict(institute=institute, institute_id=institute_id,
              case=case_model, case_id=case_id,
              variant=variant_model, variant_id=variant_id,
              comments=comments, events=events,
              prev_variant=prev_variant, next_variant=next_variant,
              manual_rank_options=Variant.manual_rank.choices)


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
  store.unpin_variant(institute, case_model, current_user, link, variant_model)
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

  store.mark_causative(institute, case_model, current_user, link, variant_model)

  # send the user back to the case the was marked as solved
  return redirect(case_url)


@core.route('/<institute_id>/<case_id>/unmark_causative', methods=['POST'])
def unmark_causative(institute_id, case_id):
  """Remove a variant as confirmed causative for a case."""
  # very basic security check
  institute = validate_user(current_user, institute_id)
  case_model = store.case(institute_id, case_id)
  case_url = url_for('.case', institute_id=institute_id, case_id=case_id)

  # skip the host part of the URL to make it more flexible
  link = request.referrer.replace(request.host_url, '/')
  variant_model = case_model.causative
  store.unmark_causative(institute, case_model, current_user, link, variant_model)

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

  recipients = institute.sanger_recipients
  if len(recipients) == 0:
    flash('No sanger recipients added to the institute.')
    return abort(403)

  # build variant page URL
  variant_url = url_for('.variant', institute_id=institute_id,
                        case_id=case_id, variant_id=variant_id)

  hgnc_symbol = ', '.join(variant_model.hgnc_symbols)
  functions = ["<li>{}</li>".format(function) for function in
               variant_model.protein_changes]
  gtcalls = ["<li>{}: {}</li>".format(individual.display_name,
                                      individual.genotype_call)
             for individual in variant_model.samples]

  html = """
    <p>Case {case_id}: <a href='{url}'>{variant_id}</a></p>
    <p>HGNC symbol: {hgnc_symbol}</p>
    <p>Database: {database_id}</p>
    <p>Chr position: {chromosome_position}</p>
    <p>Amino acid change(s): <br> <ul>{functions}</ul></p><br>
    <p>GT-call: <br> <ul>{gtcalls}</ul></p><br>
    <p>Ordered by: {name}</p>
  """.format(
    case_id=case_id,
    url=variant_url,
    variant_id=variant_id,
    hgnc_symbol=hgnc_symbol,
    database_id='coming soon',
    chromosome_position=variant_model.display_name,
    functions=''.join(functions),
    gtcalls=''.join(gtcalls),
    name=current_user.name
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

  link = url_for('.case', institute_id=institute_id, case_id=case_id)
  store.order_sanger(institute, case_model, current_user, link, variant_model)

  return redirect(variant_url)
