# -*- coding: utf-8 -*-
from scout.ext.backend import FixtureAdapter

from .fixtures import VARIANTS


def no_variants(adapter):
  """Tests adapter without first loading any fixtures."""
  # Test finding all variants
  assert adapter.variants() == []

  # Test finding multiple variants by id
  assert adapter.variants(variant_ids=[1, 3]) == []

  # Test finding a single variant
  assert adapter.variant(5) == None

  # Test creating a new variant and checking it's given id
  assert adapter.create_variant({'RS': None})['id'] == 1


def some_variants(adapter):
  """Used to test any given adapter, using the standard fixture variants."""
  # Test finding all variants
  assert adapter.variants() == VARIANTS

  # Test finding multiple variants by id
  assert adapter.variants(variant_ids=[1, 3]) == VARIANTS[0:4:2]

  # Test finding a single variant by id
  assert adapter.variant(5) == VARIANTS[4]

  # Test creating a new variant and checking it's given id
  assert adapter.create_variant({'RS': None})['id'] == 6


def test_fixture():
  # Test running for no variants loaded
  no_variants(FixtureAdapter(fixtures=None))

  # Run the test suit
  some_variants(FixtureAdapter(fixtures=VARIANTS))
