"""Code for handler that helps export bson to json"""

import datetime

import bson


def bson_handler(field):
    if isinstance(field, datetime.datetime):
        return field.isoformat()
    if isinstance(field, bson.objectid.ObjectId):
        return str(field)
    else:
        raise TypeError(field)
