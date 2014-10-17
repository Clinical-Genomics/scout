# -*- coding: utf-8 -*-
from . import BaseAdapter


VARIANTS = [
  {'id': 1, 'RS': 'rs78426951', 'CHROM': '2', 'POS': 38049774,
   'REF': 'C', 'ALT': 'A', 'QUAL': 4372.34, 'FILTER': True},
  {'id': 2, 'RS': None, 'CHROM': '1', 'POS': 152287169, 'REF': 'G',
   'ALT': 'T', 'QUAL': 6506.35, 'FILTER': False},
  {'id': 3, 'RS': 'rs78426951', 'CHROM': '2', 'POS': 38049774, 'REF': 'C',
   'ALT': 'A', 'QUAL': 4372.34, 'FILTER': True},
  {'id': 4, 'RS': 'rs201157354', 'CHROM': '2', 'POS': 241536279, 'REF': 'C',
   'ALT': 'T', 'QUAL': 3396.34, 'FILTER': True},
  {'id': 5, 'RS': 'rs201157355', 'CHROM': '2', 'POS': 241536280, 'REF': 'C',
   'ALT': 'T', 'QUAL': 3396.34, 'FILTER': True},
]


class FixtureAdapter(BaseAdapter):
  """docstring for API"""
  def __init__(self, app=None, fixtures=VARIANTS):
    super(FixtureAdapter, self).__init__()

    self.fixtures = (fixtures or [])

  def find_all(self):
    return self.fixtures

  def find_many(self, variant_ids):
    variants = []

    for variant in self.fixtures:
      if variant['id'] in variant_ids:
        variants.append(variant)

    return variants

  def find(self, variant_id):
    for variant in self.fixtures:
      if variant['id'] == int(variant_id):
        return variant

    return None

  def create(self, variant):
    # Find out last ID
    try:
      last_id = self.fixtures[-1]['id']
    except IndexError:
      last_id = 0

    next_id = last_id + 1

    # Assign id to the new variant
    variant['id'] = next_id

    # Add new variant to the list
    self.fixtures.append(variant)

    return variant
