# -*- coding: utf-8 -*-
import pytest

from scout.app import AppFactory
from scout.settings import TestConfig


@pytest.fixture(scope='session')
def app(request):
  """Session-wide test `Flask` application."""
  app = AppFactory()(__name__, config_obj=TestConfig)

  # establish an application context before running the tests.
  ctx = app.app_context()
  ctx.push()

  def teardown():
    ctx.pop()

  request.addfinalizer(teardown)
  return app


@pytest.fixture(scope='function')
def session(request):
  """Creates a new database session for a test."""

  def teardown():
    session.remove()

  request.addfinalizer(teardown)
  return session
