# -*- coding: utf-8 -*-
import os.path

import click
from livereload import Server

from scout.server.app import create_app


@click.command()
@click.option('-c', '--config', type=click.Path(exists=True), envvar='SCOUT_CONFIG',
              help='Python config file')
@click.option('-h', '--host', default='localhost', help='Where to serve')
@click.option('-p', '--port', default=5000, help='Which port to listen on')
@click.option('-d', '--debug', is_flag=True, help='Run server in debug mode')
@click.option('-l', '--livereload', is_flag=True, help='Enable Live Reload server')
@click.pass_context
def serve(context, config, host, port, debug, livereload):
    """Start the web server."""
    pymongo_config = dict(
        MONGO_HOST=context.obj['host'],
        MONGO_PORT=context.obj['port'],
        MONGO_DBNAME=context.obj['mongodb'],
        MONGO_USERNAME=context.obj['username'],
        MONGO_PASSWORD=context.obj['password'],
    )
    config = os.path.abspath(config) if config else None
    app = create_app(config=pymongo_config, config_file=config)
    if livereload:
        server = Server(app.wsgi_app)
        server.serve(host=host, port=port, debug=debug)
    else:
        app.run(host=host, port=port, debug=debug)
