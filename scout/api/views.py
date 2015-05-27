# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from bson.json_util import dumps
from flask import Blueprint, jsonify, Response, request, redirect, url_for
from flask.ext.login import current_user
import markdown as md

from scout.core.utils import validate_user
from ..extensions import omim, store
from ..models import Institute, Case, Event
from ..helpers import get_document_or_404

TERMS_MAP = {
  'Autosomal recessive': 'AR',
  'Autosomal dominant': 'AD',
  'X-linked dominant': 'XD',
  'X-linked recessive': 'XR',
}

TERMS_BLACKLIST = [
   'Isolated cases',
]

# markdown to HTML converter object
# can't use Flask-Markdown object since it doesn't support ``init_app``
mkd = md.Markdown()

api = Blueprint('api', __name__, url_prefix='/api/v1')


@api.route('/omim/gene/<hgnc_symbol>')
def omim_gene(hgnc_symbol):
  """Query OMIM for extended information on a specific gene.

  Args:
    hgnc_symbol (str): HGNC symbol for a gene

  Returns:
    Response: jsonified ``dict`` of gene specific information
  """
  # query using the OMIM extension
  return jsonify(**omim.gene(hgnc_symbol))


@api.route('/omim/inheritance/<hgnc_symbol>')
def omim_inheritance(hgnc_symbol):
  """Query OMIM for inheritance model of a specific gene.

  Args:
    hgnc_symbol (str): HGNC symbol for a gene

  Returns:
    Response: jsonified ``dict`` of inheritance model terms
  """
  entry = omim.gene(hgnc_symbol)
  models = set()
  for phenotype in entry['phenotypes']:
    if phenotype['inheritance'] is None: continue
    models.update([model.strip('? ') for model in phenotype['inheritance'].split(';')])
    models = models.difference(TERMS_BLACKLIST)

  terms = [TERMS_MAP.get(model_human, model_human) for model_human in models]

  return jsonify(models=terms)


@api.route('/<institute_id>/cases')
def cases(institute_id):
  """Fetch all cases belonging to a specific institute.

  Args:
    institute_id (str): unique institute display name

  Returns:
    Response: jsonified MongoDB objects as a list
  """
  institute = Institute.objects.get(display_name=institute_id)
  case_models = store.cases(collaborator=institute_id)
  cases_json = dumps([case.to_mongo() for case in case_models])

  return Response(cases_json, mimetype='application/json; charset=utf-8')


@api.route('/<institute_id>/<case_id>/status', methods=['PUT'])
def case_status(institute_id, case_id):
  """Update (PUT) status of a specific case."""
  case = get_document_or_404(Case, owner=institute_id, display_name=case_id)
  case.status = request.json.get('status', case.status)

  event = Event(
    link=url_for('core.case', institute_id=institute_id, case_id=case_id),
    author=current_user.to_dbref(),
    verb="updated the status to '%s' for" % case.status,
    subject=case.display_name,
  )
  case.events.append(event)

  case.save()

  return jsonify(status=case.status, ok=True)


@api.route('/<institute_id>/<case_id>/synopsis', methods=['PUT'])
def case_synopsis(institute_id, case_id):
  """Update (PUT) synopsis of a specific case."""
  case = get_document_or_404(Case, owner=institute_id, display_name=case_id)
  new_synopsis = request.json.get('synopsis', case.synopsis)

  if case.synopsis != new_synopsis:
    # create event only if synopsis was actually changed
    event = Event(
      link=url_for('core.case', institute_id=institute_id, case_id=case_id),
      author=current_user.to_dbref(),
      verb='edited synopsis for',
      subject=case.display_name,
    )
    case.events.append(event)

  case.synopsis = new_synopsis
  case.save()

  return jsonify(synopsis=case.synopsis, ok=True)


@api.route('/markdown', methods=['POST'])
def markdown():
  """Convert a Markdown string to HTML.

  Retrives the content (str) in the request object for the key
  ``markdown`` and converts it into HTML using a standard Markdown
  converter.

  Returns:
    Response: jsonified ``dict`` with the converted HTML string
  """
  mkd_string = request.json.get('markdown')
  html_string = mkd.convert(mkd_string)

  return jsonify(html=html_string)


@api.route('/<institute_id>/<case_id>/event', methods=['POST'])
def event(institute_id, case_id):
  case = get_document_or_404(Case, owner=institute_id, display_name=case_id)

  if request.method == 'POST':

    event_document = Event(
      content=request.form.get('content'),
      link=request.form.get('link'),
      author=current_user.to_dbref(),
      verb=request.form.get('verb'),
      subject=request.form.get('subject'),
    )

    case.events.append(event_document)

  # persist changes
  case.save()

  if request.args.get('json'):
    case_json = dumps(case.to_mongo())
    return Response(case_json, mimetype='application/json; charset=utf-8')

  else:
    return redirect(request.referrer)


@api.route('/<institute_id>/<case_id>/events/<event_id>', methods=['POST'])
def delete_event(institute_id, case_id, event_id=None):
  validate_user(current_user, institute_id)
  store.delete_event(event_id)
  return redirect(request.referrer)


@api.route('/<institute_id>/<case_id>/events', methods=['POST'])
def create_event(institute_id, case_id):
  institute = validate_user(current_user, institute_id)
  case_model = get_document_or_404(Case, owner=institute_id, display_name=case_id)

  link = request.form.get('link')
  content = request.form.get('content')
  variant_id = request.args.get('variant_id')

  if variant_id:
    # create a variant comment
    variant_model = store.variant(variant_id)
    level = request.form.get('level', 'specific')
    store.comment(institute, case_model, current_user, link, variant=variant_model,
                  content=content, comment_level=level)

  else:
    # create a case comment
    store.comment(institute, case_model, current_user, link, content=content)

  return redirect(request.referrer)


@api.route('/<institute_id>/<case_id>/<variant_id>/event', methods=['POST'])
@api.route('/<institute_id>/<case_id>/<variant_id>/event/<int:event_id>',
           methods=['GET'])
def variant_event(institute_id, case_id, variant_id, event_id=None):
  """For now this route only handles variant comments."""
  case = get_document_or_404(Case, owner=institute_id, display_name=case_id)
  variant = store.variant(document_id=variant_id)

  if request.method == 'POST':

    event = Event(
      title=request.form.get('title'),
      content=request.form.get('content'),
      link=request.form.get('link'),
      author=current_user.to_dbref(),
      verb=request.form.get('verb'),
      subject=request.form.get('subject'),
    )

    variant.comments.append(event)

  elif request.method == 'GET':  # TODO: make this work with DELETE!
    # remove event by index, expects list to be reversed in template
    variant.comments.pop(-event_id)

  # persist changes
  variant.save()

  if request.args.get('json'):
    document_json = dumps(variant.to_mongo())
    return Response(document_json, mimetype='application/json; charset=utf-8')

  else:
    return redirect(request.referrer)


@api.route('/<institute_id>/<case_id>/variants/<variant_id>/manual_rank',
           methods=['PUT'])
def manual_rank(institute_id, case_id, variant_id):
  """Update the manual variant rank for a variant."""
  variant = store.variant(document_id=variant_id)

  # update the manual rank
  new_manual_rank = int(request.json.get('manual_rank'))
  variant.manual_rank = new_manual_rank

  # log action event
  variant.events.append(Event(
    link=request.referrer,
    author=current_user.to_dbref(),
    verb="updated manual rank to {} for".format(new_manual_rank),
    subject=variant.display_name,
  ))

  variant.save()

  return jsonify(manual_rank=variant.manual_rank, ok=True)
