#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.script import Manager, Server

from scout.app import AppFactory
from scout.extensions import ctx

app = AppFactory()
manager = Manager(app)


class SecureServer(Server):

  """Enable conditional setup of SSL context.

  Takes effect during ``app.run()`` execution depending on the ``DEBUG``
  flag status.
  """

  def __call__(self, app, *args, **kwargs):
    """Setup server using SSL (HTTPS)."""
    if not app.config.get('SSL_MODE'):
      # remove SSL context
      del self.server_options['ssl_context']

    # run the original ``__call__`` function
    super(SecureServer, self).__call__(app, *args, **kwargs)


@manager.shell
def make_shell_context():
  """Return context dict for a shell session.

  This enables quick access to the Flask ``app`` object.

  Returns:
    dict: context object for the Shell session.
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
# command meant to be run in a Vagrant environment during development
manager.add_command('vagrant', Server(host='0.0.0.0', use_reloader=True))
# command meant to be run in production using SSL encryption
manager.add_command('serve', SecureServer(ssl_context=ctx, host='0.0.0.0'))


if __name__ == '__main__':
  manager.run()
