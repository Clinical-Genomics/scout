#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.script import Manager, Server

from scout.app import AppFactory
from scout.extensions import ctx

app = AppFactory()

manager = Manager(app)


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


class SecureServer(Server):
  """Enable conditional setup of SSL context.

  Takes effect during ``app.run()`` execution depending on DEBUG mode.
  """
  def __call__(self, app, *args, **kwargs):

    if not app.config.get('SSL_MODE'):
      # Remove SSL context
      del self.server_options['ssl_context']

    # Run the original ``__call__`` function
    super(SecureServer, self).__call__(app, *args, **kwargs)


manager.add_option(
  '-c', '--config', dest='config', required=False, help='config file path')
manager.add_command('vagrant', Server(host='0.0.0.0', use_reloader=True))
manager.add_command('serve', SecureServer(ssl_context=ctx, host='0.0.0.0'))


if __name__ == '__main__':
  manager.run()
