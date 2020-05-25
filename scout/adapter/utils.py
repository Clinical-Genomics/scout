import logging

try:
    # Python 3.x
    from urllib.parse import quote_plus
except ImportError:
    # Python 2.x
    from urllib import quote_plus


from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure

LOG = logging.getLogger(__name__)


def check_connection(
    host="localhost", port=27017, username=None, password=None, authdb=None, max_delay=1
):
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
    # uri looks like:
    # mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]
    if username and password:
        uri = "mongodb://{}:{}@{}:{}/{}".format(
            quote_plus(username), quote_plus(password), host, port, authdb
        )
        log_uri = "mongodb://{}:****@{}:{}/{}".format(quote_plus(username), host, port, authdb)
    else:
        log_uri = uri = "mongodb://%s:%s" % (host, port)

    LOG.info("Test connection with uri: %s", log_uri)
    client = MongoClient(uri, serverSelectionTimeoutMS=max_delay)
    try:
        client.server_info()
    except (ServerSelectionTimeoutError, OperationFailure) as err:
        LOG.warning(err)
        return False

    return True
