import logging

from pymongo import (MongoClient)
from pymongo.errors import (ServerSelectionTimeoutError, OperationFailure)

LOG = logging.getLogger(__name__)


def check_connection(host='localhost', port=27017, username=None, password=None,
                     authdb=None, max_delay=1):
    """Check if a connection could be made to the mongo process specified

    Args:
        host(str)
        port(int)
        username(str)
        password(str)
        authdb (str): database to to for authentication
        max_delay(int): Number of milliseconds to wait for connection

    Returns:
        bool: If connection could be established
    """
    #uri looks like:
    #mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]
    uri = "mongodb://"
    if username and password:
        uri += "{0}:{1}@".format(username, password)
    uri += "{0}:{1}".format(host, port)
    if authdb:
        uri = "{}/{}".format(uri, authdb)
    client = MongoClient(uri, serverSelectionTimeoutMS=max_delay)
    try:
        client.server_info()
    except (ServerSelectionTimeoutError,OperationFailure) as err:
        LOG.warning(err)
        return False

    return True
