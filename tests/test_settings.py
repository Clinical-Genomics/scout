# -*- coding: utf-8 -*-
from scout.settings import BaseConfig, DevelopmentConfig, TestConfig


def test_BaseConfig():
  """Ensure default configs is sane."""
  config = BaseConfig()
  assert config.PROJECT == 'scout'
  assert config.DEBUG is False
  assert config.MAIL_DEFAULT_SENDER == config.MAIL_USERNAME


def test_DevelopmentConfig():
  """Ensure development config is sane."""
  config = DevelopmentConfig()
  assert config.DEBUG is True
  assert config.DEBUG_TB_ENABLED is True


def test_TestConfig():
  """Ensure development config is sane."""
  config = TestConfig()
  assert config.DEBUG is True
  assert config.TESTING is True
