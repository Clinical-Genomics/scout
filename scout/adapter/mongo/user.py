# -*- coding: utf-8 -*-
import logging
import datetime

import pymongo

logger = logging.getLogger(__name__)


class UserHandler(object):

    def update_user(self, user_obj):
        """Update an existing user."""
        updated_user = self.user_collection.find_one_and_update(
            {'_id': user_obj['_id']},
            {'$set': user_obj},
            return_document=pymongo.ReturnDocument.AFTER
        )
        return updated_user

    def add_user(self, user_obj):
        """Add a user object to the database

            Args:
                user_obj(dict): A dictionary with user information
        """
        logger.info("Adding user to the database")
        user_obj['_id'] = user_obj['email']
        user_obj['created_at'] = datetime.datetime.now()
        self.user_collection.insert_one(user_obj)
        logger.debug("User inserted")

    def users(self):
        """Return all users from the database"""
        return self.user_collection.find()

    def user(self, email=None):
        """Fetch a user from the database."""
        logger.info("Fetching user %s", email)
        user_obj = self.user_collection.find_one({'_id': email})

        # if user_obj:
        #     institutes = []
        #     for institute_id in user_obj['institutes']:
        #         institute_obj = self.institute(institute_id=institute_id)
        #         if not institute_obj:
        #             logger.warning("Institute %s not in database", institute_id)
        #             ##TODO Raise exception here?
        #         else:
        #             institutes.append(institute_obj)
        #     user_obj['institutes'] = institutes

        return user_obj

    def add_whitelist(self, email, institutes):
        """Add a whitelist object

        Args:
            email(str)
            institutes(list)
        """
        logger.info("Adding whitelist %s to database", email)
        whitelist_obj = dict(
            _id= email,
            email=email,
            created_at=datetime.datetime.now(),
            institutes=institutes
        )
        self.whitelist_collection.insert_one(whitelist_obj)
