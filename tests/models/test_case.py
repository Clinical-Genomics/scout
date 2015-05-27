# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from datetime import datetime

from .setup_objects import setup_case


def test_case():
  """Test the case class"""
  case = setup_case()
  assert case.case_id == "Institute0_1"