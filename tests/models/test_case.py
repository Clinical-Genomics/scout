# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from scout.models import Case, Individual


class TestIndividual:

  """Test functionality of the Individual (sample) class."""

  def setup(self):
    # create dummy individual (male, unaffected)
    self.male = Individual(
      display_name='123-4-1A',
      sex='1',
      phenotype=1,
      individual_id='23YU89812P',
      capture_kit=['Agilent_SureSelect.v4']
    )

    # create another individual (female, affected)
    self.female = Individual(
      display_name='123-4-2A',
      sex='2',
      phenotype=2,
      individual_id='894AA498464G',
      capture_kit=['Agilent_SureSelect.v5']
    )

  def test_sex_human(self):
    assert self.male.sex_human == 'male'
    assert self.female.sex_human == 'female'

  def test_phenotype_human(self):
    assert self.male.phenotype_human == 'unaffected'
    assert self.female.phenotype_human == 'affected'

  def test_unicode(self):
    assert str(self.male) == self.male.display_name
