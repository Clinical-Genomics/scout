import logging
from typing import Dict, Optional

from scout.constants import OMICS_FILE_TYPE_MAP
from scout.models.omics_variant import OmicsVariantLoader
from scout.parse.omics_variant import parse_omics_file

LOG = logging.getLogger(__name__)


class OmicsVariantHandler:
    def delete_omics_variants(self, case_id: str, file_type: str):
        """Delete OMICS variants for a case"""
        omics_file_type = OMICS_FILE_TYPE_MAP.get(file_type)
        category = omics_file_type["category"]
        sub_category = omics_file_type["sub_category"]
        variant_type = omics_file_type["variant_type"]

        LOG.info(
            "Deleting old %s %s %s OMICS variants.",
            variant_type,
            sub_category,
            category,
        )

        query = {
            "case_id": case_id,
            "variant_type": variant_type,
            "category": category,
            "sub_category": sub_category,
        }
        result = self.omics_variant_collection.delete_many(query)

        LOG.info("%s variants deleted", result.deleted_count)

    def get_matching_omics_sample_id(self, case_obj: dict, omics_model: dict) -> dict:
        """Select individual that matches omics model sample on omics_sample_id if these are provided."""
        for ind in case_obj.get("individuals"):
            if omics_model["sample_id"] == ind.get("omics_sample_id"):
                return ind

    def get_matching_sample_id(self, case_obj: dict, omics_model: dict) -> dict:
        """
        Select individual that matches omics model on sample id (as when we are loading a pure RNA case eg).
        """
        for ind in case_obj.get("individuals"):
            if omics_model["sample_id"] == ind.get("individual_id"):
                return ind

    def _get_affected_individual(self, case_obj: dict) -> dict:
        """
        Fall back to assigning the variants to an individual with affected status to have them display
        on variantS queries.
        """
        for ind in case_obj.get("individuals"):
            if ind.get("phenotype") in [2, "affected"]:
                return ind

    def _get_first_individual(self, case_obj: dict) -> dict:
        """
        Fall back to assigning the variants to any one individual to have them display
        on variantS queries.
        """
        return case_obj.get("individuals")[0]

    def set_samples(self, case_obj: dict, omics_model: dict):
        """Internal member function to connect individuals for a single OMICS variant.
        OMICS variants do not have a genotype as such.
        Select individuals that match on omics_sample_id if these are provided.
        For a fallback, match on sample id (as when we are loading a pure RNA case eg),
        or fall back to assigning the variants to an individual with affected status to have them display
        on variantS queries.
        ."""

        samples = []

        match = (
            self.get_matching_omics_sample_id(case_obj, omics_model)
            or self.get_matching_sample_id(case_obj, omics_model)
            or self._get_affected_individual(case_obj)
            or self._get_first_individual(case_obj)
        )

        sample = {
            "sample_id": match["individual_id"],
            "display_name": match["display_name"],
            "genotype_call": "./1",
        }
        samples.append(sample)

        omics_model["samples"] = samples

    def set_genes(self, omics_model: dict):
        """Internal member function to connect gene based on the hgnc_id / symbol / geneID given in outlier file.
        We start with the case of having one hgnc_id.
        """
        hgnc_gene = self.hgnc_gene(omics_model["hgnc_ids"][0], omics_model["build"])
        if hgnc_gene:
            omics_model["genes"] = [hgnc_gene]

    def load_omics_variants(self, case_obj: dict, file_type: str, build: Optional[str] = "37"):
        """Load OMICS variants for a case"""

        case_panels = case_obj.get("panels", [])
        gene_to_panels = self.gene_to_panels(case_obj)

        omics_file_type: dict = OMICS_FILE_TYPE_MAP.get(file_type)

        nr_inserted = 0

        file_handle = open(case_obj["omics_files"].get(file_type), "r")

        for omics_info in parse_omics_file(file_handle, omics_file_type=omics_file_type):
            omics_info["case_id"] = case_obj["_id"]
            omics_info["build"] = "37" if "37" in build else "38"
            omics_info["file_type"] = file_type
            omics_info["institute"] = case_obj["owner"]
            for key in ["category", "sub_category", "variant_type", "analysis_type"]:
                omics_info[key] = omics_file_type[key]

            omics_model = OmicsVariantLoader(**omics_info).model_dump(
                by_alias=True, exclude_none=True
            )

            self.set_genes(omics_model)
            self.set_samples(case_obj, omics_model)

            # If case has gene panels, only add clinical variants with a matching gene
            variant_genes = [gene["hgnc_id"] for gene in omics_model.get("genes", [])]
            if (
                omics_model["variant_type"] == "clinical"
                and case_panels
                and all(variant_gene not in gene_to_panels for variant_gene in variant_genes)
            ):
                continue

            self.omics_variant_collection.insert_one(omics_model)
            nr_inserted += 1

        LOG.info("%s variants inserted", nr_inserted)

    def omics_variant(self, variant_id: str, projection: Optional[Dict] = None):
        """Return omics variant"""

        return self.omics_variant_collection.find_one({"omics_variant_id": variant_id}, projection)

    def omics_variants(
        self,
        case_id: str,
        query=None,
        category: str = "outlier",
        nr_of_variants=50,
        skip=0,
        projection: Optional[Dict] = None,
        build="37",
    ):
        """Return omics variants for a case, of a particular type (clinical, research) and category (outlier, ...)."""

        if nr_of_variants == -1:
            nr_of_variants = 0  # This will return all variants
        else:
            nr_of_variants = skip + nr_of_variants

        query = self.build_query(case_id, query=query, category=category, build=build)
        return self.omics_variant_collection.find(
            query, projection, skip=skip, limit=nr_of_variants
        )

    def count_omics_variants(
        self, case_id, query, variant_ids=None, category="outlier", build="37"
    ):
        """Returns number of variants

        Arguments:
            case_id(str): A string that represents the case
            query(dict): A query dictionary

        Returns:
             integer
        """

        query = self.build_query(
            case_id, query=query, variant_ids=variant_ids, category=category, build=build
        )
        return self.omics_variant_collection.count_documents(query)
