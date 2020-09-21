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

    def upsert_managed_variant(self, managed_variant_obj, original_obj_id=None):
        """Load or updated a managed variant object

        Args:
            managed_variant_obj(ManagedVariant)
            original_obj_id(str):   String representation of original obj id to update

        Returns:
            updated_managed_variant
        """

        LOG.debug("Upserting variant %s", managed_variant_obj["display_id"])

        managed_variant_obj["date"] = managed_variant_obj.get("date", datetime.now())

        collision = self.managed_variant_collection.find_one(
            {"managed_variant_id": managed_variant_obj["managed_variant_id"]}
        )
        if collision:
            LOG.debug("Collision - new variant already exists! Leaving variant unmodified.")
            return

        if original_obj_id:
            result = self.managed_variant_collection.find_one_and_update(
                {"_id": ObjectId(original_obj_id)},
                {"$set": managed_variant_obj},
            )

            return result

        try:
            result = self.managed_variant_collection.insert_one(managed_variant_obj)
        except DuplicateKeyError as err:
            LOG.debug(
                "Variant %s already exists in database with a document id %s.",
                managed_variant_obj["display_id"],
                managed_variant_obj["_id"],
            )

        return result

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

    def find_managed_variant_id(self, variant_id):
        """Fetch eg search for a managed variant with the encoded positional variant_id.

        Arguments:
            display_id(str): chrom_pos_ref_alt_category_build
                category: "snv", "cancer" - "sv", "cancer_sv" possible but not expected
                build: "37" or "38"

        Returns:
            ManagedVariant
        """
        managed_variant = self.managed_variant_collection.find_one({"variant_id": variant_id})

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

    def delete_managed_variant_obj_id(self, managed_variant_obj_id=None):
        """Delete a managed variant of known object id.

        Arguments:
            variant_obj_id(str)     string representation of _id ObjectId

        Returns:
            ManagedVariant
        """

        managed_variant_obj = self.managed_variant_collection.find_one(
            {"_id": ObjectId(managed_variant_obj_id)}
        )

        if not managed_variant_obj:
            LOG.info(
                "FAILED deleting managed variant: variant_id %s not found.", managed_variant_obj_id
            )
            return None

        LOG.info("Deleting managed variant %s.", managed_variant_obj.get("display_name"))

        result = self.managed_variant_collection.find_one_and_delete(
            {"_id": ObjectId(managed_variant_obj_id)}
        )
        return result

    def delete_managed_variant(self, managed_variant_id):
        """Delete a managed variant of known id.

        Arguments:
            variant_id(str)

        Returns:
            ManagedVariant
        """

        LOG.info("Attempting to delete managed variant with id %s.", managed_variant_id)

        result = self.managed_variant_collection.find_one_and_delete(
            {"managed_variant_id": managed_variant_id}
        )

        if not result:
            LOG.info(
                "FAILED deleting managed variant: variant_id %s not found.", managed_variant_id
            )

        return result
