# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from flask import Blueprint, jsonify

from ..extensions import omim

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
