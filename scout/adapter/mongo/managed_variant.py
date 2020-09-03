import logging
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from bson import ObjectId
import pymongo

from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)


class ManagedVariantHandler(object):
    """Class to handle variant events for the mongo adapter"""

    def load_managed_variant(self, managed_variant_obj):
        """Load a managed variant object

        Args:
            managed_variant_obj(ManagedVariant)

        Returns:
            inserted_id
        """
        try:
            result = self.managed_variant_collection.insert_one(managed_variant_obj)
        except DuplicateKeyError as err:
            raise IntegrityError(
                "Variant %s already exists in database",
                managed_variant_obj["display_id"],
            )

        return result.inserted_id

    def upsert_managed_variant(self, managed_variant_obj):
        """Load a managed variant object

        Args:
            managed_variant_obj(ManagedVariant)

        Returns:
            updated_managed_variant
        """

        LOG.debug("Upserting variant %s", managed_variant_obj["display_id"])

        managed_variant_obj["date"] = managed_variant_obj.get("date", datetime.now())

        try:
            result = self.managed_variant_collection.insert_one(managed_variant_obj)
        except DuplicateKeyError as err:
            check_variant_obj = self.find_managed_variant(
                managed_variant_obj["managed_variant_id"],
            )
            if check_variant_obj:
                LOG.debug("Variant %s already exists in database", check_variant_obj["display_id"])

            result = self.managed_variant_collection.find_one_and_update(
                {"variant_id": managed_variant_obj["variant_id"]},
                {"$set": managed_variant_obj},
            )

        updated_managed_variant = self.variant_collection.find_one(
            {"variant_id": managed_variant_obj["variant_id"]}
        )

        return updated_managed_variant

    def managed_variant(self, document_id):
        """Retrieve a managed variant of known id.

        Arguments:
            document_id(ObjectId)

        Returns:
            ManagedVariant
        """

        managed_variant_obj = self.managed_variant_collection.find_one(
            {"_id": ObjectId(document_id)}
        )

        return managed_variant_obj

    def find_managed_variant(self, managed_variant_id):
        """Fetch eg search for a managed variant.

        Arguments:
            display_id(str): chrom_pos_ref_alt_category_build
                category: "snv", "cancer" - "sv", "cancer_sv" possible but not expected
                build: "37" or "38"

        Returns:
            ManagedVariant
        """
        managed_variant = self.managed_variant_collection.find_one(
            {"managed_variant_id": managed_variant_id}
        )

        return managed_variant

    def managed_variants(self, category="snv", build="37"):
        """Return a cursor to all managed variants of a particular category and build.

        Arguments:
            category(str):
            sub_category(str):
            build(str):

        Returns:
            managed_variants(pymongo.Cursor)

        """
        managed_variants_res = self.managed_variant_collection.find(
            {"category": category, "build": build}
        )

        return managed_variants_res

    def delete_managed_variant(self, managed_variant_id):
        """Delete a managed variant of known id.

        Arguments:
            variant_id(str)

        Returns:
            ManagedVariant
        """

        managed_variant_obj = self.managed_variant_collection.find_one(
            {"managed_variant_id": managed_variant_id}
        )
        if not managed_variant_obj:
            LOG.info(
                "FAILED deleting managed variant: variant_id %s not found.", managed_variant_id
            )
        else:
            LOG.info("Deleting managed variant %s.", managed_variant_obj.get("display_name"))

        result = self.managed_variant_collection.find_one_and_delete(
            {"managed_variant_id": managed_variant_id}
        )

        return result
