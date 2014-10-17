# -*- coding: utf-8 -*-
import io
import json
import os

from . import BaseAdapter


class FixtureAdapter(BaseAdapter):
  """docstring for API"""
  def init_app(self, app):
    # get root path of the Flask app
    project_root = '/'.join(app.root_path.split('/')[0:-1])

    # combine path to the local development fixtures
    variants_path = os.path.join(project_root, 'tests/fixtures/variants.json')
    families_path = os.path.join(project_root, 'tests/fixtures/families.json')

    # open the json fixtures and convert to dict
    with io.open(variants_path, encoding='utf-8') as handle:
      self._variants = json.load(handle)

    with io.open(families_path, encoding='utf-8') as handle:
      self._families = json.load(handle)


  def variants(self, query=None, variant_ids=None):
    if variant_ids:
      return self._many_variants(variant_ids)

    return self._variants

  def _many_variants(self, variant_ids):
    variants = []

    for variant in self._variants:
      if variant['id'] in variant_ids:
        variants.append(variant)

    return variants

  def variant(self, variant_id):
    for variant in self._variants:
      if variant['id'] == int(variant_id):
        return variant

    return None

  def create_variant(self, variant):
    # Find out last ID
    try:
      last_id = self._variants[-1]['id']
    except IndexError:
      last_id = 0

    next_id = last_id + 1

    # Assign id to the new variant
    variant['id'] = next_id

    # Add new variant to the list
    self._variants.append(variant)

    return variant
