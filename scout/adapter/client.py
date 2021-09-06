"""
client.py

Establish a connection to the database

"""
import logging

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

try:
    # Python 3.x
    from urllib.parse import quote_plus
except ImportError:
    # Python 2.x
    from urllib import quote_plus


LOG = logging.getLogger(__name__)


def get_connection(
    host="localhost",
    port=27017,
    username=None,
    password=None,
    uri=None,
    mongodb=None,
    authdb=None,
    timeout=20,
    *args,
    **kwargs
):
    """Get a client to the mongo database

    host(str): Host of database
    port(int): Port of database
    username(str)
    password(str)
    uri(str)
    authdb (str): database to use for authentication
    timeout(int): How long should the client try to connect

    """
    authdb = authdb or mongodb
    if uri is None:
        if username and password:
            uri = "mongodb://{}:{}@{}:{}/{}".format(
                quote_plus(username), quote_plus(password), host, port, authdb
            )
            log_uri = "mongodb://{}:****@{}:{}/{}".format(quote_plus(username), host, port, authdb)
        else:
            log_uri = uri = "mongodb://%s:%s" % (host, port)

    LOG.info("Try to connect to %s" % log_uri)
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=timeout)
    except ServerSelectionTimeoutError as err:
        LOG.warning("Connection Refused")
        raise ConnectionFailure

    LOG.info("Connection established")
    return client
