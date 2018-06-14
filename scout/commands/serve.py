# -*- coding: utf-8 -*-
import os.path
import logging

import click
from livereload import Server

from scout.server.app import create_app

from scout.adapter.utils import check_connection

log = logging.getLogger(__name__)

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
    
    valid_connection = check_connection(
        host=pymongo_config['MONGO_HOST'], 
        port=pymongo_config['MONGO_PORT'], 
        username=pymongo_config['MONGO_USERNAME'], 
        password=pymongo_config['MONGO_PASSWORD'],
        authdb=context.obj['authdb'],
        )

    log.info("Test if mongod is running")
    if not valid_connection:
        log.warning("Connection could not be established")
        log.info("Is mongod running?")
        context.abort()
    

    config = os.path.abspath(config) if config else None
    app = create_app(config=pymongo_config, config_file=config)
    if livereload:
        server = Server(app.wsgi_app)
        server.serve(host=host, port=port, debug=debug)
    else:
        app.run(host=host, port=port, debug=debug)
