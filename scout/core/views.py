# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import (abort, Blueprint, current_app, flash, redirect, request,
                   url_for)
from flask.ext.login import login_required, current_user
from flask.ext.mail import Message

from .forms import FiltersForm
from ..models import Institute, Case, Event
from ..extensions import mail, store
from ..helpers import templated, get_document_or_404

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
  institute = get_document_or_404(Institute, institute_id)

  # very basic security check
  if institute not in current_user.institutes:
    flash('You do not have access to this institute.')
    return abort(403)

  # fetch cases from the data store
  return dict(institute=institute, institute_id=institute_id)


@core.route('/<institute_id>/<case_id>')
@templated('case.html')
@login_required
def case(institute_id, case_id):
  """View one specific case."""
  # abort with 404 error if case/institute doesn't exist
  institute = get_document_or_404(Institute, institute_id)
  case = get_document_or_404(Case, case_id)

  # fetch a single, specific case from the data store
  return dict(institute=institute, case=case, statuses=Case.status.choices)


@core.route('/<institute_id>/<case_id>/assign', methods=['POST'])
def assign_self(institute_id, case_id):
  case = get_document_or_404(Case, case_id)

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
  case = get_document_or_404(Case, case_id)

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


@core.route('/<institute_id>/<case_id>/variants', methods=['GET', 'POST'])
@templated('variants.html')
@login_required
def variants(institute_id, case_id):
  """View all variants for a single case."""
  per_page = 50

  # fetch all variants for a specific case
  institute = get_document_or_404(Institute, institute_id)
  case = get_document_or_404(Case, case_id)
  skip = int(request.args.get('skip', 0))

  # update case status if currently inactive
  if case.status == 'inactive':
    case.status = 'active'
    case.save()

  form = FiltersForm(**request.form)
  form.gene_list.choices = [(option, option) for option in case.gene_lists]

  return dict(variants=store.variants(case.case_id, nr_of_variants=per_page,
                                      skip=skip),
              case=case,
              case_id=case_id,
              institute=institute,
              institute_id=institute_id,
              current_batch=(skip + per_page),
              form=form)


@core.route('/<institute_id>/<case_id>/variants/<variant_id>')
@templated('variant.html')
@login_required
def variant(institute_id, case_id, variant_id):
  """View a single variant in a single case."""
  institute = get_document_or_404(Institute, institute_id)
  case = get_document_or_404(Case, case_id)
  variant = store.variant(variant_id=variant_id)

  prev_variant = store.previous_variant(variant_id=variant_id,
                                        case_id=case.case_id)
  next_variant = store.next_variant(variant_id=variant_id,
                                    case_id=case.case_id)

  return dict(
    institute=institute,
    institute_id=institute_id,
    case=case,
    case_id=case_id,
    variant_id=variant_id,
    variant=variant,
    specific=variant.specific[case.id],
    prev_variant=prev_variant,
    next_variant=next_variant,
  )


@core.route('/<institute_id>/<case_id>/<variant_id>/pin', methods=['POST'])
def pin_variant(institute_id, case_id, variant_id):
  """Pin or unpin a variant from the list of suspects."""
  case = get_document_or_404(Case, case_id)
  variant = store.variant(variant_id=variant_id)
  variant_url = url_for('.variant', institute_id=institute_id,
                        case_id=case_id, variant_id=variant_id)

  # add variant to list of pinned variants in the case model
  case.suspects.append(variant)
  verb = 'added'

  # add event
  case.events.append(Event(
    link=variant_url,
    author=current_user.to_dbref(),
    verb="%s a variant suspect: " % verb,
    subject=variant_id,
  ))

  # persist changes
  case.save()

  return redirect(request.args.get('next') or request.referrer or variant_url)


@core.route('/<institute_id>/<case_id>/<variant_id>/unpin', methods=['POST'])
def unpin_variant(institute_id, case_id, variant_id):
  """Pin or unpin a variant from the list of suspects."""
  case = get_document_or_404(Case, case_id)
  variant = store.variant(variant_id=variant_id)
  variant_url = url_for('.variant', institute_id=institute_id,
                        case_id=case_id, variant_id=variant_id)

  # remove an already existing pinned variant
  case.suspects.remove(variant)
  verb = 'removed'

  # add event
  case.events.append(Event(
    link=variant_url,
    author=current_user.to_dbref(),
    verb="%s a variant suspect: " % verb,
    subject=variant_id,
  ))

  # persist changes
  case.save()

  return redirect(request.args.get('next') or request.referrer or variant_url)


@core.route('/<institute_id>/<case_id>/<variant_id>/email-sanger',
            methods=['POST'])
@login_required
def email_sanger(institute_id, case_id, variant_id):
  institute = get_document_or_404(Institute, institute_id)
  case = get_document_or_404(Case, case_id)
  variant = store.variant(variant_id=variant_id)
  specific = variant.specific[case.id]

  recipients = institute.sanger_recipients
  if len(recipients) == 0:
    flash('No sanger recipients added to the institute.')
    return abort(404)

  # build variant page URL
  variant_url = url_for('.variant', institute_id=institute_id,
                        case_id=case_id, variant_id=variant_id)

  hgnc_symbol = ', '.join(variant.common.hgnc_symbols)
  functions = ["<li>%s</li>" % function for function in
               variant.common.protein_change]
  gtcalls = ["<li>%s: %s</li>" % (individual.sample, individual.genotype_call)
             for individual in specific.samples]

  html = """
    <p>Case {case_id}: <a href='{url}'>{variant_id}</a></p>
    <p>HGNC symbol: {hgnc_symbol}</p>
    <p>Database: {database_id}</p>
    <p>Chr position: {chromosome_position}</p>
    <p>Amino acid change(s): <br> <ul>{functions}</ul></p>
    <p>GT-call: <br> <ul>{gtcalls}</ul></p>
    <p>Ordered by: {name}</p>
  """.format(
    case_id=case_id,
    url=variant_url,
    variant_id=variant_id,
    hgnc_symbol=hgnc_symbol,
    database_id='coming soon',
    chromosome_position="%s:%s-%s" % (variant.chromosome,
                                      variant.position,
                                      variant.end_position),
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
    cc=[current_user.email],
    bcc=[current_app.config['MAIL_USERNAME']]
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
  specific.events.append(Event(**event_kwargs))
  variant.save()

  return redirect(variant_url)
