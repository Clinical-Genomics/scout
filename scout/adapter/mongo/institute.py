import logging

from datetime import datetime

from scout.exceptions import IntegrityError

logger = logging.getLogger(__name__)


class InstituteHandler(object):

    def add_institute(self, institute_obj):
        """Add a institute to the database

            Args:
                institute_obj(Institute)
        """
        internal_id = institute_obj['internal_id']
        display_name = institute_obj['internal_id']
        
        # Check if institute already exists
        if self.institute(institute_id=internal_id):
            raise IntegrityError("Institute {0} already exists in database"
                                 .format(display_name))

        logger.info("Adding institute with internal_id: {0} and "
                    "display_name: {1}".format(internal_id,
                                               display_name))

        insert_info = self.institute_collection.insert_one(institute_obj)
        ##TODO check if insert info was ok
        logger.info("Institute saved")

    def update_institute(self, internal_id, sanger_recipient=None,
                         coverage_cutoff=None):
        """Update the information for an institute

            Args:
                internal_id(str): The internal institute id
                sanger_recipient(str): Email adress for ordering sanger
                coverage_cutoff(int): Update coverage cutoff
        """
        updates = {}
        
        if sanger_recipient:
            logger.info("Updating sanger recipients for institute"\
                        " {0} with {1}".format(
                            internal_id, sanger_recipient))
            updates['$push'] = {'sanger_recipients':sanger_recipient}
        
        if coverage_cutoff:
            logger.info("Updating coverage cutoff for institute"\
                        " {0} with {1}".format(
                            internal_id, coverage_cutoff))
            updates['$set'] = {'coverage_cutoff': coverage_cutoff}
        
        if updates:
            if '$set' in updates:
                updates['$set']['updated_at'] = datetime.now()
            else:
                updates['$set'] = dict(updated_at=datetime.now())
            
            ##TODO should this raise if institute not found?
            
            self.institute_collection.update_one({'_id':internal_id}, updates)

    def institute(self, institute_id):
        """Featch a single institute from the backend

            Args:
                institute_id(str)

            Returns:
                Institute object
        """
        logger.debug("Fetch institute {}".format(institute_id))
        institute_obj = self.institute_collection.find_one({
            '_id': institute_id
        })
        if institute_obj is None:
            logger.debug("Could not find institute {0}".format(institute_id))
        
        return institute_obj

    def institutes(self):
        """Fetch all institutes."""
        logger.info("Fetching all institutes")
        return self.institute_collection.find()

