import logging

from scout.exceptions import IntegrityError
from mongoengine import DoesNotExist
from scout.models.institute import Institute

logger = logging.getLogger(__name__)


class InstituteHandler(object):
    
    def add_institute(self, institute_obj):
        """Add a institute to the database

            Args:
                institute_obj(Institute)
        """
        logger.info("Adding institute with internal_id: {0} and "
                    "display_name: {1}".format(institute_obj['internal_id'],
                                               institute_obj['display_name']))
        if self.institute(institute_id=institute_obj['internal_id']):
            raise IntegrityError("Institute {0} already exists in database"
                                 .format(institute_obj['internal_id']))
        institute_obj.save()
        logger.info("Institute saved")

    def update_institute(self, internal_id, sanger_recipient=None,
                         coverage_cutoff=None):
        """Update the information for an institute

            Args:
                internal_id(str): The internal institute id
                sanger_recipient(str): Email adress for ordering sanger
                coverage_cutoff(int): Update coverage cutoff
        """
        institute = self.institute(internal_id)
        if institute:
            if sanger_recipient:
                logger.info("Updating sanger recipients for institute"\
                            " {0} with {1}".format(
                                internal_id, sanger_recipient))
                institute.sanger_recipients.append(sanger_recipient)
            if coverage_cutoff:
                logger.info("Updating coverage cutoff for institute"\
                            " {0} with {1}".format(
                                internal_id, coverage_cutoff))
                institute.coverage_cutoff = coverage_cutoff
            institute.save()

    def institute(self, institute_id):
        """Featch a single institute from the backend

            Args:
                institute_id(str)

            Returns:
                Institute object
        """
        logger.debug("Fetch institute {}".format(institute_id))
        try:
            return Institute.objects.get(internal_id=institute_id)
        except DoesNotExist:
            logger.debug("Could not find institute {0}".format(institute_id))
            return None

    def institutes(self):
        """Fetch all institutes."""
        return Institute.objects()
    
