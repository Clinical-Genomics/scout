# -*- coding: utf-8 -*-
import logging
import datetime

import pymongo
from pymongo.errors import DuplicateKeyError

from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)


class UserHandler(object):
    def update_user(self, user_obj):
        """Update an existing user.

        Args:
            user_obj(dict)

        Returns:
            updated_user(dict)
        """
        LOG.info("Updating user %s", user_obj["_id"])
        updated_user = self.user_collection.find_one_and_replace(
            {"_id": user_obj["_id"]},
            user_obj,
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return updated_user

    def add_user(self, user_obj):
        """Add a user object to the database

        Args:
            user_obj(scout.models.User): A dictionary with user information

        Returns:
            user_info(dict): a copy of what was inserted
        """
        LOG.info("Adding user %s to the database", user_obj["email"])
        if not "_id" in user_obj:
            user_obj["_id"] = user_obj["email"]

        try:
            self.user_collection.insert_one(user_obj)
            LOG.debug("User inserted")
        except DuplicateKeyError as err:
            raise IntegrityError("User {} already exists in database".format(user_obj["email"]))

        return user_obj

    def users(self, institute=None):
        """Return all users from the database

        Args:
            institute(str): A institute_id

        Returns:
            res(pymongo.Cursor): A cursor with users
        """
        query = {}
        if institute:
            LOG.info("Fetching all users from institute %s", institute)
            query = {"institutes": {"$in": [institute]}}
        else:
            LOG.info("Fetching all users")

        res = self.user_collection.find(query)
        return res

    def user(self, email=None, user_id=None):
        """Fetch a user from the database.

        Args:
            email(str)
            user_id(str)

        Returns:
            user_obj(dict)
        """
        if not (user_id or email):
            LOG.warning("No key provided to fetch user")
            return None
        query = {}
        if user_id:
            LOG.info("Fetching user %s", user_id)
            query["_id"] = user_id
        else:
            LOG.info("Fetching user %s", email)
            query["email"] = email

        user_obj = self.user_collection.find_one(query)

        return user_obj

    def delete_user(self, email):
        """Delete a user from the database

        Args:
            email(str)

        Returns:
            user_obj(dict)

        """
        LOG.info("Deleting user %s", email)
        result = self.user_collection.delete_one({"email": email})
        return result
