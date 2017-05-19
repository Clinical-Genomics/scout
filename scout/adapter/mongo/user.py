# -*- coding: utf-8 -*-
import logging
import datetime

import pymongo

log = logging.getLogger(__name__)

class UserHandler(object):

    def update_user(self, user_obj):
        """Update an existing user.
        
        
            Args:
                user_obj(dict)
        
            Returns:
                updated_user(dict)
        """
        updated_user = self.user_collection.find_one_and_update(
            {'_id': user_obj['_id']},
            {'$set': user_obj},
            return_document=pymongo.ReturnDocument.AFTER
        )
        return updated_user

    def add_user(self, user_info):
        """Add a user object to the database

            Args:
                user_info(dict): A dictionary with user information
        
            Returns:
                user_info(dict): a copy of what was inserted
        """
        log.info("Adding user %s to the database", user_info['email'])
        if not '_id' in user_info:
            user_info['_id'] = user_info['email']
    
        user_info['created_at'] = datetime.datetime.now()

        self.user_collection.insert_one(user_info)
        log.debug("User inserted")

        return user_info

    def users(self, institute=None):
        """Return all users from the database
        
            Args:
                institute(str): A institute_id
        
            Returns:
                res(pymongo.Cursor): A cursor with users
        """
        query = {}
        if institute:
            log.info("Fetching all users from institute %s", institute)
            query = {'institutes': {'$in': [institute]}}
        else:
            log.info("Fetching all users")
            
        res = self.user_collection.find(query)
        return res

    def user(self, email):
        """Fetch a user from the database.
        
            Args:
                email(str)
        
            Returns:
                user_obj(dict)
        """
        log.info("Fetching user %s", email)
        user_obj = self.user_collection.find_one({'_id': email})

        return user_obj
    
    def delete_user(self, email):
        """Delete a user from the database
        
        Args:
            email(str)
    
        Returns:
            user_obj(dict)
        
        """
        log.info("Deleting user %s", email)
        user_obj = self.user_collection.delete_one({'_id': email})
        
        return user_obj
        

