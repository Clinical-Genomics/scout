import logging
import datetime

from scout.exceptions import IntegrityError

logger = logging.getLogger(__name__)

class UserHandler(object):

    def getoradd_user(self, email, name, location=None, institutes=None):
        """Get or create a new user."""
        
        user_obj = self.user(email=email)
        
        if user_obj is None:
            logger.info('create user: %s', email)
            self.user_collection.insert_one({
                '_id': email,
                'email': email,
                'created_at': datetime.datetime.now(),
                'location': location,
                'name': name,
                'institutes': institutes,
            })
            user_obj = self.user(email=email)

        return user_obj

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
        
        if user_obj:
            institutes = []
            for institute_id in user_obj['institutes']:
                institute_obj = self.institute(institute_id=institute_id)
                if not institute_obj:
                    logger.warning("Institute %s not in database", institute_id)
                    ##TODO Raise exception here?
                else:
                    institutes.append(institute_obj)
            user_obj['institutes'] = institutes
        
        return user_obj

    def update_access(self, user_obj):
        user_obj['accessed_at'] = datetime.datetime.now()
        self.user_collection.find_and_update(
            {'_id': user_obj['_id']},
            user_obj
            )

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