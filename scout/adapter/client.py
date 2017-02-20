"""
client.py

Establish a connection to the database

"""
import logging

from pymongo import MongoClient
from pymongo.errors import (ConnectionFailure, ServerSelectionTimeoutError)

try:
    # Python 3.x
    from urllib.parse import quote_plus
except ImportError:
    # Python 2.x
    from urllib import quote_plus


logger = logging.getLogger(__name__)


def get_connection(host='localhost', port=27017, username=None, password=None,
                   uri=None, app=None, timeout=20):
    """Get a client to the mongo database

        host(str): Host of database
        port(int): Port of database
        username(str)
        password(str)
        uri(str)
        app
        timeout(int): How long should the client try to connect

    """
    if not uri:
        if app:
            config = getattr(app, 'config', {})

            host = config.get('MONGODB_HOST', 'localhost')
            port = config.get('MONGODB_PORT', 27017)
            username = config.get('MONGODB_USERNAME', None)
            password = config.get('MONGODB_PASSWORD', None)

        if username and password:
            uri = ("mongodb://{}:{}@{}:{}/scoutTest"
                   .format(quote_plus(username), quote_plus(password), host, port))
        else:
            uri = "mongodb://%s:%s" % (host, port)

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=timeout)
    except ServerSelectionTimeoutError as err:
        logger.warning("Connection Refused")
        raise ConnectionFailure

    logger.info("Connection established")
    return client
