# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from bson.json_util import dumps
from flask import Blueprint, jsonify, Response, request

from ..extensions import omim
from ..models import Institute, Case
from ..helpers import get_document_or_404

TERMS_MAPPER = {
  'Autosomal recessive': 'AR',
  'Autosomal dominant': 'AD',
  'X-linked dominant': 'XD',
  'X-linked recessive': 'XR',
  'Autosomal dominant; Isolated cases': 'AD'
}

api = Blueprint('api', __name__, url_prefix='/api/v1')


@api.route('/omim/gene/<hgnc_symbol>')
def omim_gene(hgnc_symbol):
  return jsonify(**omim.gene(hgnc_symbol))


@api.route('/omim/inheritance/<hgnc_symbol>')
def omim_inheritance(hgnc_symbol):
  entry = omim.gene(hgnc_symbol)
  models = set(phenotype['inheritance'] for phenotype in entry['phenotypes'])
  terms = [TERMS_MAPPER.get(model_human, model_human) for model_human in models]

  return jsonify(models=terms)


@api.route('/<institute_id>/cases')
def cases(institute_id):
  institute = Institute.objects.get(display_name=institute_id)
  cases_json = dumps([case.to_mongo() for case in institute.cases])

  return Response(cases_json, mimetype='application/json; charset=utf-8')


@api.route('/<institute_id>/<case_id>/status', methods=['PUT'])
def case_status(institute_id, case_id):
  case = get_document_or_404(Case, case_id)
  case.status = request.json.get('status', case.status)
  case.save()

  # TODO: create a new event here!

  return jsonify(status=case.status, ok=True)
