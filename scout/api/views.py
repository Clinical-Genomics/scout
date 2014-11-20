# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from flask import Blueprint, jsonify

from ..extensions import omim

api = Blueprint('api', __name__, url_prefix='/api/v1')


@api.route('/omim/gene/<hgnc_symbol>')
def omim_clinical_synopsis(hgnc_symbol):
  return jsonify(**omim.gene(hgnc_symbol))


@api.route('/omim/inheritance/<mim_number>')
def omim_inheritance(mim_number):
  res = omim.clinical_synopsis(mim_number)
  entry = res.json()['omim']['clinicalSynopsisList'][0]

  inheritance_str = entry['clinicalSynopsis']['inheritance']
  inheritance_human = inheritance_str.split('{')[0].rstrip()
  inheritance = {
    'Autosomal recessive': 'AR',
    'Autosomal dominant': 'AD',
    'X-linked dominant': 'XD',
    'X-linked recessive': 'XR'
  }.get(inheritance_human, 'unknown')

  return jsonify(inheritance=inheritance, inheritance_human=inheritance_human)
