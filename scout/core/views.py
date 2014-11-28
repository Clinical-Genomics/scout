# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import (abort, Blueprint, current_app, flash, jsonify, redirect,
                   request, url_for)
from flask.ext.login import login_required, current_user
from flask.ext.mail import Message

from ..models import Institute, Variant, Case
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
  case.save()

  return redirect(url_for('.case', institute_id=institute_id, case_id=case_id))


@core.route('/<institute_id>/<case_id>/unassign', methods=['POST'])
def remove_assignee(institute_id, case_id):
  case = get_document_or_404(Case, case_id)

  # unassign user and persist changes
  case.assignee = None
  case.save()

  return redirect(url_for('.case', institute_id=institute_id, case_id=case_id))


@core.route('/<institute_id>/<case_id>/variants')
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

  return dict(variants=store.variants(case.case_id, nr_of_variants=per_page,
                                      skip=skip),
              case=case,
              case_id=case_id,
              institute=institute,
              institute_id=institute_id,
              current_batch=(skip + per_page))


@core.route('/<institute_id>/<case_id>/variants/<variant_id>')
@templated('variant.html')
@login_required
def variant(institute_id, case_id, variant_id):
  """View a single variant in a single case."""
  institute = get_document_or_404(Institute, institute_id)
  case = get_document_or_404(Case, case_id)
  variant = store.variant(variant_id=variant_id)

  return dict(
    institute=institute,
    institute_id=institute_id,
    case=case,
    case_id=case_id,
    variant_id=variant_id,
    variant=variant,
    specific=variant.specific[case.id]
  )


@core.route('/<institute_id>/email-sanger', methods=['POST'])
@login_required
def email_sanger(institute_id):
  institute = get_document_or_404(Institute, institute_id)

  recipients = institute.sanger_recipients
  if len(recipients) == 0:
    flash('No sanger recipients added to the institute.')
    return abort(404)

  html = """
    <p>
      Case %(family_id)s:
      <a class='activity-caption-link' href='%(url)s'>%(variant_id)s</a>
    </p>
    <p>HGNC symbol: %(hgnc_symbol)s</p>
    <p>Database: %(database_id)s</p>
    <p>
      Chr position: <br>
      %(chromosome_position)s
    </p>
    <p>
      Amino acid change(s): <br>
      <ul>#{(functions.join('') or '<li>No protein changes</li>')}</ul>
    </p>
    <p>
      GT-call: <br>
      <ul>#{gtcalls.join('')}</ul>
    </p>
    <p>Ordered by: %(name)s</p>
  """ % dict(family_id=None, name=current_user.name)

  kwargs = dict(
    subject="SCOUT: Sanger sequencing of %s" % request.form['hgnc_symbol'],
    html=request.form.get('message', 'Hi, default here'),
    sender=current_app.config['MAIL_USERNAME'],
    recipients=recipients,
    # cc the sender of the email for confirmation
    cc=[current_user.email],
    bcc=[current_app.config['MAIL_USERNAME']]
  )

  # compose and send the email message
  msg = Message(**kwargs)
  mail.send(msg)

  return jsonify(**kwargs)
