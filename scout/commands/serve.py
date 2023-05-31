# -*- coding: utf-8 -*-
import logging
import sys

import click
from flask.cli import current_app, with_appcontext
from livereload import Server
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError
from werkzeug.serving import run_simple

LOG = logging.getLogger(__name__)


@click.command(deprecated=True)
@click.option("-h", "--host", default="localhost", help="Where to serve")
@click.option("-p", "--port", default=5000, help="Which port to listen on")
@click.option("-d", "--debug", is_flag=True, help="Run server in debug mode")
@click.option("-l", "--livereload", is_flag=True, help="Enable Live Reload server")
@click.option("-test", "--test", is_flag=True, help="Test app params")
@with_appcontext
def serve(host, port, debug, livereload, test):
    """Start the web server."""

    # Verify the database connectivity before launching the app
    mongo_client = current_app.config.get("MONGO_DATABASE")._Database__client
    try:
        mongo_client.server_info()
        if test:
            LOG.info("Connection could be established")
            return
    except (ServerSelectionTimeoutError, OperationFailure, ConnectionFailure) as err:
        sys.exit("No database connection available")

    if livereload:
        server = Server(current_app.wsgi_app)
        server.serve(host=host, port=port, debug=debug)
    else:
        return run_simple(
            hostname=host,
            port=port,
            application=current_app,
            use_reloader=False,
            use_debugger=debug,
        )
