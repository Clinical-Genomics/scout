import logging

from pymongo import (MongoClient)
from pymongo.errors import (ServerSelectionTimeoutError)

log = logging.getLogger(__name__)


def check_connection(host='localhost', port=27017, username=None, password=None, 
                     max_delay=1):
    """Check if a connection could be made to the mongo process specified"""
    #uri looks like:
    #mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]
    uri = "mongodb://{0}:{1}@{2}:{3}".format(
        username,
        password,
        host,
        port,
    )
    
    client = MongoClient(uri, serverSelectionTimeoutMS=max_delay)
    
    try:
        client.server_info()
    except ServerSelectionTimeoutError as err:
        return False
    
    return True
    
    