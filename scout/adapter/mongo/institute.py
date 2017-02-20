import logging

logger = logging.getLogger(__name__)


class InstituteHandler(object):
    
    def add_institute(self, institute_obj):
        """Add a institute to the database

            Args:
                institute_obj(Institute)
        """
        self.mongoengine_adapter.add_institute(institute_obj=institute_obj)

    def update_institute(self, internal_id, sanger_recipient=None,
                         coverage_cutoff=None):
        """Update the information for an institute

            Args:
                internal_id(str): The internal institute id
                sanger_recipient(str): Email adress for ordering sanger
                coverage_cutoff(int): Update coverage cutoff
        """
        self.mongoengine_adapter.add_institute(
            internal_id=internal_id,
            sanger_recipient=sanger_recipient,
            coverage_cutoff=coverage_cutoff
        )

    def institute(self, institute_id):
        """Featch a single institute from the backend

            Args:
                institute_id(str)

            Returns:
                Institute object
        """
        return self.mongoengine_adapter.institute(institute_id=institute_id)
        

    def institutes(self):
        """Fetch all institutes."""
        return self.mongoengine_adapter.institutes()
    
