#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.script import Manager, Server

from scout.app import AppFactory

app = AppFactory()

manager = Manager(app)
TEST_CMD = "py.test tests"


@manager.shell
def make_shell_context():
  """Return context dict for a shell session so you can access
  app, db, and the User model by default.
  """
  return dict(app=app())


@manager.command
def test():
  """Run the tests."""
  import pytest
  exit_code = pytest.main(['tests', '--verbose'])
  return exit_code


manager.add_option(
  '-c', '--config', dest='config', required=False, help='config file path')
manager.add_command('server', Server())
manager.add_command('vagrant', Server(host='0.0.0.0', use_reloader=True))


if __name__ == '__main__':
  manager.run()
