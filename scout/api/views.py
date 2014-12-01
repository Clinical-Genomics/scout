# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from bson.json_util import dumps
from flask import Blueprint, jsonify, Response, request, redirect
from flask.ext.login import current_user
import markdown as md

from ..extensions import omim
from ..models import Institute, Case, Event
from ..helpers import get_document_or_404

TERMS_MAP = {
  'Autosomal recessive': 'AR',
  'Autosomal dominant': 'AD',
  'X-linked dominant': 'XD',
  'X-linked recessive': 'XR',
  'Autosomal dominant; Isolated cases': 'AD'
}

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
  models = set(phenotype['inheritance'] for phenotype in entry['phenotypes'])
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
  cases_json = dumps([case.to_mongo() for case in institute.cases])

  return Response(cases_json, mimetype='application/json; charset=utf-8')


@api.route('/<institute_id>/<case_id>/status', methods=['PUT'])
def case_status(institute_id, case_id):
  """Update (PUT) status of a specific case."""
  case = get_document_or_404(Case, case_id)
  case.status = request.json.get('status', case.status)
  case.save()

  # TODO: create a new event here!

  return jsonify(status=case.status, ok=True)


@api.route('/<institute_id>/<case_id>/synopsis', methods=['PUT'])
def case_synopsis(institute_id, case_id):
  """Update (PUT) synopsis of a specific case."""
  case = get_document_or_404(Case, case_id)
  case.synopsis = request.json.get('synopsis', case.synopsis)
  case.save()

  # TODO: create a new event here!

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
@api.route('/<institute_id>/<case_id>/event/<int:event_id>',
           methods=['GET'])
def event(institute_id, case_id, event_id=None):
  case = get_document_or_404(Case, case_id)

  if request.method == 'POST':

    event = Event(
      title=request.form.get('title'),
      content=request.form.get('content'),
      link=request.form.get('link'),
      author=current_user.to_dbref(),
      verb=request.form.get('verb'),
      subject=request.form.get('subject'),
    )

    case.events.append(event)

  elif request.method == 'GET':  # TODO: make this work with DELETE!
    # remove event by index
    case.events.pop(event_id - 1)

  # persist changes
  case.save()

  if request.args.get('json'):
    case_json = dumps(case.to_mongo())
    return Response(case_json, mimetype='application/json; charset=utf-8')

  else:
    return redirect(request.referrer)
