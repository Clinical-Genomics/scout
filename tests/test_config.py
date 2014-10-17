# -*- coding: utf-8 -*-
from scout.config import BaseConfig


def test_base_config():
  """Test base config values."""
  assert BaseConfig.PROJECT == 'scout'
  assert BaseConfig.DEBUG == False
