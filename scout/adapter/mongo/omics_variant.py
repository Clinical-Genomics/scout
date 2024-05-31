# stdlib modules
import logging

from typing import Dict

LOG = logging.getLogger(__name__)

class OmicsVariantHandler(OmicsVariantLoader):
    def delete_omics_variants(self, case_id: str, file_type: Dict[str, str]):
        """Delete OMICS variants for a case"""
        category = file_type["category"]
        sub_category = file_type["sub_category"]
        variant_type = file_type["variant_type"]
        analysis_type = file_type["analysis_type"]
        LOG.info("Deleting old %s %s %s %s OMICS variants.", analysis_type, variant_type, sub_category, category)
        query = {"case_id": case_id, "variant_type": variant_type, "analysis_type": analysis_type, "category": category, "sub_category": sub_category, }
        result = self.omics_variant_collection.delete_many(query)
        LOG.info("%s variants deleted", result.deleted_count)

    def load_omics_variants(self):


    def omics_variant(self):


