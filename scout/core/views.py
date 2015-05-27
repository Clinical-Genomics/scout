# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import (abort, Blueprint, current_app, flash, redirect, request,
                   url_for)
from flask.ext.login import login_required, current_user
from flask.ext.mail import Message

from scout.models import Case, Event, PhenotypeTerm, Variant
from scout.extensions import mail, store
from scout.helpers import templated, get_document_or_404

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

  The purpose of this page is to display all cases related to an
  institute. It should also give an idea of which
  """
  # very basic security check
  institute = validate_user(current_user, institute_id)

  # fetch cases from the data store
  return dict(institute=institute, institute_id=institute_id)


@core.route('/<institute_id>/<case_id>')
@templated('case.html')
@login_required
def case(institute_id, case_id):
  """View one specific case."""
  # very basic security check
  institute = validate_user(current_user, institute_id)
  case_model = get_document_or_404(Case, owner=institute_id, display_name=case_id)

  case_comments = store.comments(case_model)

  # fetch a single, specific case from the data store
  return dict(institute=institute, case=case_model, statuses=Case.status.choices,
              case_comments=case_comments, institute_id=institute_id, case_id=case_id)


@core.route('/<institute_id>/<case_id>/assign', methods=['POST'])
def assign_self(institute_id, case_id):
  # very basic security check
  validate_user(current_user, institute_id)
  case = get_document_or_404(Case, owner=institute_id, display_name=case_id)

  # assign logged in user and persist changes
  case.assignee = current_user.to_dbref()

  # create event
  event = Event(
    link=url_for('.case', institute_id=institute_id, case_id=case_id),
    author=current_user.to_dbref(),
    verb='was assigned to',
    subject=case.display_name
  )
  case.events.append(event)

  # persist changes
  case.save()

  return redirect(url_for('.case', institute_id=institute_id, case_id=case_id))


@core.route('/<institute_id>/<case_id>/unassign', methods=['POST'])
def remove_assignee(institute_id, case_id):
  # very basic security check
  validate_user(current_user, institute_id)
  case = get_document_or_404(Case, owner=institute_id, display_name=case_id)

  # unassign user and persist changes
  case.assignee = None

  # create event
  event = Event(
    link=url_for('.case', institute_id=institute_id, case_id=case_id),
    author=current_user.to_dbref(),
    verb='was unassigned from',
    subject=case.display_name
  )
  case.events.append(event)

  case.save()

  return redirect(url_for('.case', institute_id=institute_id, case_id=case_id))


@core.route('/<institute_id>/<case_id>/open_research', methods=['POST'])
def open_research(institute_id, case_id):
  """Open the research list for a case.

  TODO: this should ping the admins to make necessary checks.
  """
  # very basic security check
  institute = validate_user(current_user, institute_id)
  case_model = get_document_or_404(Case, owner=institute_id, display_name=case_id)

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

  # create event
  event = Event(link=url_for('.case', institute_id=institute_id,
                             case_id=case_id),
                author=current_user.to_dbref(),
                verb='opened research mode for',
                subject=case_model.display_name)
  case_model.events.append(event)

  case_model.save()

  return redirect(url_for('.case', institute_id=institute_id, case_id=case_id))


@core.route('/<institute_id>/<case_id>/phenotype_terms', methods=['POST'])
@core.route('/<institute_id>/<case_id>/phenotype_terms/<int:phenotype_id>',
            methods=['POST'])
def case_phenotype(institute_id, case_id, phenotype_id=None):
  """Add a new HPO term to the case.

  TODO: validate ID and fetch phenotype description before adding to case.
  """
  validate_user(current_user, institute_id)
  case = get_document_or_404(Case, owner=institute_id, display_name=case_id)
  case_url = url_for('.case', institute_id=institute_id, case_id=case_id)

  if phenotype_id:
    # DELETE a phenotype from the list
    action_verb = 'removed'
    hpo_term = case.phenotype_terms.pop(phenotype_id - 1).hpo_id

  else:
    # POST a new phenotype to the list
    action_verb = 'added'
    hpo_term = request.form['hpo_term']
    phenotype_term = PhenotypeTerm(hpo_id=hpo_term)
    if phenotype_term not in case.phenotype_terms:
      # append the new HPO term (ID)
      case.phenotype_terms.append(phenotype_term)

  # create event
  event = Event(link=case_url, author=current_user.to_dbref(),
                verb="{verb} HPO term '{term}' for"
                     .format(verb=action_verb, term=hpo_term),
                subject=case.display_name)
  case.events.append(event)

  case.save()
  return redirect(case_url)


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
@templated('variants.html')
@login_required
def variants(institute_id, case_id, variant_type):
  """View all variants for a single case."""
  per_page = 50
  current_gene_lists = [gene_list for gene_list
                        in request.args.getlist('gene_lists') if gene_list]

  # fetch all variants for a specific case
  # very basic security check
  institute = validate_user(current_user, institute_id)
  case_model = get_document_or_404(Case, owner=institute_id, display_name=case_id)
  skip = int(request.args.get('skip', 0))

  # update case status if currently inactive
  if case_model.status == 'inactive':
    case_model.status = 'active'
    case_link = url_for('.case', institute_id=institute_id, case_id=case_id)
    store.update_status(institute, case_model, current_user, 'active', case_link)

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

  # fetch list of variants
  variants = store.variants(case_model.case_id, query=form.data,
                            nr_of_variants=per_page, skip=skip)

  return dict(variants=variants,
              case=case_model,
              case_id=case_id,
              institute=institute,
              institute_id=institute_id,
              current_batch=(skip + per_page),
              form=form,
              severe_so_terms=SO_TERMS[:14],
              current_gene_lists=current_gene_lists,
              variant_type=variant_type,
              upload_form=GeneListUpload())


@core.route('/<institute_id>/<case_id>/<variant_type>/hpo_redirect')
@login_required
def hpo_gene_list_redirect(institute_id, case_id, variant_type):
  # redirect user to variants list after querying HPO
  validate_user(current_user, institute_id)
  case_model = get_document_or_404(Case, owner=institute_id, display_name=case_id)

  return redirect(url_for('.variants', institute_id=institute_id,
                          case_id=case_id,
                          variant_type=variant_type,
                          hgnc_symbols=case_model.hpo_gene_ids))


@core.route('/<institute_id>/<case_id>/variants/<variant_id>')
@templated('variant.html')
@login_required
def variant(institute_id, case_id, variant_id):
  """View a single variant in a single case."""
  # very basic security check
  institute = validate_user(current_user, institute_id)
  case = get_document_or_404(Case, owner=institute_id, display_name=case_id)
  variant = store.variant(document_id=variant_id)

  prev_variant = store.previous_variant(document_id=variant_id)
  next_variant = store.next_variant(document_id=variant_id)

  return dict(
    institute=institute,
    institute_id=institute_id,
    case=case,
    case_id=case_id,
    variant_id=variant_id,
    variant=variant,
    prev_variant=prev_variant,
    next_variant=next_variant,
    manual_rank_options=Variant.manual_rank.choices
  )


@core.route('/<institute_id>/<case_id>/<variant_id>/pin', methods=['POST'])
def pin_variant(institute_id, case_id, variant_id):
  """Pin or unpin a variant from the list of suspects."""
  # very basic security check
  validate_user(current_user, institute_id)
  case = get_document_or_404(Case, owner=institute_id, display_name=case_id)
  variant = store.variant(document_id=variant_id)
  variant_url = url_for('.variant', institute_id=institute_id,
                        case_id=case_id, variant_id=variant_id)

  # add variant to list of pinned variants in the case model
  case.suspects.append(variant)
  verb = 'added'

  # add event
  case.events.append(Event(
    link=variant_url,
    author=current_user.to_dbref(),
    verb="{} a variant suspect: ".format(verb),
    subject=variant_id,
  ))

  # persist changes
  case.save()

  return redirect(request.args.get('next') or request.referrer or variant_url)


@core.route('/<institute_id>/<case_id>/<variant_id>/unpin', methods=['POST'])
def unpin_variant(institute_id, case_id, variant_id):
  """Pin or unpin a variant from the list of suspects."""
  # very basic security check
  validate_user(current_user, institute_id)
  case = get_document_or_404(Case, owner=institute_id, display_name=case_id)
  variant = store.variant(document_id=variant_id)
  variant_url = url_for('.variant', institute_id=institute_id,
                        case_id=case_id, variant_id=variant_id)

  # remove an already existing pinned variant
  case.suspects.remove(variant)
  verb = 'removed'

  # add event
  case.events.append(Event(
    link=variant_url,
    author=current_user.to_dbref(),
    verb="{} a variant suspect: ".format(verb),
    subject=variant_id,
  ))

  # persist changes
  case.save()

  return redirect(request.args.get('next') or request.referrer or variant_url)


@core.route('/<institute_id>/<case_id>/<variant_id>/mark_causative',
            methods=['POST'])
def mark_causative(institute_id, case_id, variant_id):
  """Mark a variant as confirmed causative."""
  # very basic security check
  validate_user(current_user, institute_id)
  case_model = get_document_or_404(Case, owner=institute_id, display_name=case_id)
  variant_model = store.variant(document_id=variant_id)
  variant_url = url_for('.variant', institute_id=institute_id,
                        case_id=case_id, variant_id=variant_id)
  case_url = url_for('.case', institute_id=institute_id, case_id=case_id)

  # mark the variant as causative in the case model
  case_model.causative = variant_model

  # add event
  event = Event(link=variant_url,
                author=current_user.to_dbref(),
                verb=("marked a causative variant for case {}:"
                      .format(case_model.display_name)),
                subject=variant_id)
  case_model.events.append(event)
  variant_model.events.append(event)

  # mark the case as solved
  case_model.status = 'solved'

  # persist changes
  case_model.save()
  variant_model.save()

  # send the user back to the case the was marked as solved
  return redirect(case_url)


@core.route('/<institute_id>/<case_id>/unmark_causative', methods=['POST'])
def unmark_causative(institute_id, case_id):
  """Remove a variant as confirmed causative for a case."""
  # very basic security check
  validate_user(current_user, institute_id)
  case_model = get_document_or_404(Case, owner=institute_id, display_name=case_id)
  case_url = url_for('.case', institute_id=institute_id, case_id=case_id)

  # skip the host part of the URL to make it more flexible
  variant_url = request.referrer.replace(request.host_url, '/')
  variant_model = case_model.causative

  # add event
  event = Event(link=variant_url,
                author=current_user.to_dbref(),
                verb=("Removed the causative variant for case {}:"
                      .format(case_model.display_name)),
                subject=case_model.causative.document_id)
  case_model.events.append(event)
  variant_model.events.append(event)

  # remove the variant as causative in the case model
  case_model.causative = None

  # mark the case as active again
  case_model.status = 'active'

  # persist changes
  case_model.save()
  variant_model.save()

  # send the user back to the case the was marked as solved
  return redirect(request.referrer or case_url)


@core.route('/<institute_id>/<case_id>/<variant_id>/email-sanger',
            methods=['POST'])
@login_required
def email_sanger(institute_id, case_id, variant_id):
  # very basic security check
  institute = validate_user(current_user, institute_id)

  case = get_document_or_404(Case, owner=institute_id, display_name=case_id)
  variant = store.variant(document_id=variant_id)

  recipients = institute.sanger_recipients
  if len(recipients) == 0:
    flash('No sanger recipients added to the institute.')
    return abort(403)

  # build variant page URL
  variant_url = url_for('.variant', institute_id=institute_id,
                        case_id=case_id, variant_id=variant_id)

  hgnc_symbol = ', '.join(variant.hgnc_symbols)
  functions = ["<li>{}</li>".format(function) for function in
               variant.protein_changes]
  gtcalls = ["<li>{}: {}</li>".format(individual.display_name,
                                      individual.genotype_call)
             for individual in variant.samples]

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
    chromosome_position=variant.display_name,
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

  # add events
  event_kwargs = dict(
    link=url_for('.case', institute_id=institute_id, case_id=case_id),
    author=current_user.to_dbref(),
    verb="ordered Sanger sequencing for %s" % hgnc_symbol,
    subject=variant_id,
  )
  case.events.append(Event(**event_kwargs))
  case.save()

  # add to variant
  event_kwargs['link'] = variant_url
  variant.events.append(Event(**event_kwargs))
  variant.save()

  return redirect(variant_url)
