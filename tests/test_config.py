# -*- coding: utf-8 -*-
import pytest

from scout.app import create_app
from scout.config import BaseConfig, DefaultConfig


def test_production_config():
  assert BaseConfig.PROJECT == 'prod'
