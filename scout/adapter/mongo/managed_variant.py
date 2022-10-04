import logging
from datetime import datetime

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

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

        LOG.debug("MV: {}".format(managed_variant_obj))
        managed_variant_obj["date"] = managed_variant_obj.get("date", datetime.now())

        collision = self.managed_variant_collection.find_one(
            {"managed_variant_id": managed_variant_obj["managed_variant_id"]}
        )

        # edit from gui, may update key contruction values
        if collision and original_obj_id:
            LOG.debug("Update from GUI")
            result = self.managed_variant_collection.find_one_and_update(
                {"_id": ObjectId(original_obj_id)},
                {"$set": managed_variant_obj},
            )
            LOG.debug("RESULT: {}".format(result))
            return True

        # edit from file, write if key construction values are unchanged
        if collision:
            LOG.debug("COLLISION: {}".format(collision))
            if managed_variant_obj["managed_variant_id"] == collision["managed_variant_id"]:
                if not _equal(managed_variant_obj, collision):
                    LOG.debug("Update from FILE")
                    result = self.managed_variant_collection.find_one_and_update(
                        {"_id": ObjectId(original_obj_id)},
                        {"$set": managed_variant_obj},
                    )
                    LOG.debug("RESULT: {}".format(result))
                    return True
            else:
                LOG.debug(
                    "Collision -variant already exists but no original id given! Leaving variant unmodified."
                )

            return False

        try:
            LOG.debug("Update NEW")
            result = self.managed_variant_collection.insert_one(managed_variant_obj)
            LOG.debug("RESULT: {}".format(result))
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
                category: "snv", "cancer_snv" - "sv", "cancer_sv" possible but not expected
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
                category: "snv", "cancer_snv" - "sv", "cancer_sv" possible but not expected
                build: "37" or "38"

        Returns:
            ManagedVariant
        """
        managed_variant = self.managed_variant_collection.find_one({"variant_id": variant_id})

        return managed_variant

    def managed_variants(
        self,
        category=["snv", "sv", "cancer_snv", "cancer_sv"],
        query_options=None,
        build=None,
    ):
        """Return a cursor to all managed variants of a particular category and build.

        Arguments:
            category(str):
            query_options(str):
            build(str):

        Returns:
            managed_variants(pymongo.Cursor)

        """

        query = {"category": {"$in": category}}
        query_with_options = self.add_options(query, query_options)
        return self.managed_variant_collection.find(query_with_options)

    def count_managed_variants(
        self,
        category=["snv", "sv", "cancer_snv", "cancer_sv"],
        build="37",
        query_options=None,
    ):
        """Return count of documents to all managed variants of a particular category and build.

        Arguments:
            category(str):
            sub_category(str):
            build(str):

        Returns:
            integer

        """
        query = {"category": {"$in": category}, "build": build}
        query_with_options = self.add_options(query, query_options)

        return self.managed_variant_collection.count_documents(query_with_options)

    def add_options(self, query, query_options):
        """Update query with `query_options`"""

        if query_options:
            if "description" in query_options:
                query["description"] = {
                    "$regex": ".*" + query_options["description"] + ".*",
                    "$options": "i",
                }

            if "position" in query_options:
                query["end"] = {"$gte": int(query_options["position"])}

            if "end" in query_options:
                query["position"] = {"$lte": int(query_options["end"])}

            if "sub_category" in query_options:
                query["sub_category"] = {"$in": query_options["sub_category"]}

            if "chromosome" in query_options:
                query["chromosome"] = query_options["chromosome"]

        return query

    def get_managed_variants(self, category=["snv"], build="37"):
        """Return managed variant_ids. Limit by institute, category and build.

        Accepts:
            category(str): "snv", "sv"
            build(str): "37" or "38"

        Returns:
            managed_variant_ids(iterable(variant_id: String))
        """
        if not isinstance(category, list):
            category = [category]

        return [
            managed_variant["variant_id"]
            for managed_variant in self.managed_variants(category, build)
        ]

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
                "FAILED deleting managed variant: variant_id %s not found.",
                managed_variant_id,
            )

        return result

    def _equal(managed_variant_a, managed_variant_b):
        """Compare two managed variants"""
        return (
            managed_variant_a["alternative"] == managed_variant_b["alternative"]
            and managed_variant_a["build"] == managed_variant_b["build"]
            and managed_variant_a["category"] == managed_variant_b["category"]
            and managed_variant_a["chromosome"] == managed_variant_b["chromosome"]
            and managed_variant_a["date"] == managed_variant_b["date"]
            and managed_variant_a["description"] == managed_variant_b["description"]
            and managed_variant_a["display_id"] == managed_variant_b["display_id"]
            and managed_variant_a["end"] == managed_variant_b["end"]
            and managed_variant_a["institute"] == managed_variant_b["institute"]
            and managed_variant_a["maintainer"] == managed_variant_b["maintainer"]
            and managed_variant_a["managed_variant_id"] == managed_variant_b["managed_variant_id"]
            and managed_variant_a["position"] == managed_variant_b["position"]
            and managed_variant_a["reference"] == managed_variant_b["reference"]
            and managed_variant_a["sub_category"] == managed_variant_b["sub_category"]
            and managed_variant_a["variant_id"] == managed_variant_b["variant_id"]
        )
