import logging
from typing import Dict, Optional

from scout.constants import OMICS_FILE_TYPE_MAP
from scout.models.omics_variant import OmicsVariantLoader
from scout.parse.omics_variant import parse_omics_file

LOG = logging.getLogger(__name__)


class OmicsVariantHandler:
    def delete_omics_variants(self, case_id: str, omics_file: str):
        """Delete OMICS variants for a case"""
        file_type = OMICS_FILE_TYPE_MAP.get("omics_file")
        category = file_type["category"]
        sub_category = file_type["sub_category"]
        variant_type = file_type["variant_type"]
        analysis_type = file_type["analysis_type"]

        LOG.info(
            "Deleting old %s %s %s %s OMICS variants.",
            analysis_type,
            variant_type,
            sub_category,
            category,
        )

        query = {
            "case_id": case_id,
            "variant_type": variant_type,
            "analysis_type": analysis_type,
            "category": category,
            "sub_category": sub_category,
        }
        result = self.omics_variant_collection.delete_many(query)

        LOG.info("%s variants deleted", result.deleted_count)

    def _connect_gene(self, omics_model: dict):
        """Internal member function to connect gene based on the hgnc_id / symbol / geneID given in outlier file.
        We start with the case of having one hgnc_id.
        """
        hgnc_gene = self.hgnc_gene(omics_model["hgnc_id"], omics_model["build"])
        if hgnc_gene:
            omics_model["genes"] = [hgnc_gene]

    def load_omics_variants(self, case_obj: dict, file_type: str, build: Optional[str] = "37"):
        """Load OMICS variants for a case"""

        case_panels = case_obj.get("panels", [])
        gene_to_panels = self.gene_to_panels(case_obj)
        # genes = [gene_obj for gene_obj in self.all_genes(build=build)]
        # hgncid_to_gene = self.hgncid_to_gene(genes=genes, build=build)

        omics_file_type: dict = OMICS_FILE_TYPE_MAP.get("file_type")

        nr_inserted = 0

        file_handle = open(case_obj["omics_files"].get(file_type), "r")

        for omics_info in parse_omics_file(
            file_handle, omics_file_type=case_obj["omics_files"].get(file_type)
        ):
            omics_info["case_id"] = case_obj["_id"]
            omics_info["build"] = "37" if "37" in build else "38"
            omics_info["file_type"] = file_type
            for key in ["category", "sub_category", "variant_type", "analysis_type"]:
                omics_info[key] = omics_file_type[key]

            omics_model = OmicsVariantLoader(**omics_info).model_dump(by_alias=True)

            self._connect_gene(omics_model)

            self._get_ids(omics_model)

            # If case has gene panels, only add clinical variants with a matching gene
            variant_genes = [gene["hgnc_id"] for gene in omics_model["genes"]]
            if (
                omics_model["variant_type"] == "clinical"
                and case_panels
                and all(variant_gene not in gene_to_panels for variant_gene in variant_genes)
            ):
                continue

            # try - catch to catch duplicates?
            self.omics_variant_collection.insert_one(omics_model)
            nr_inserted += 1

        LOG.info("%s variants inserted", nr_inserted)

    def omics_variant(self, variant_id: str, projection: Optional[Dict] = None):
        """Return omics variant"""

        return self.omics_variant_collection.find({"_id": variant_id}, projection)

    def omics_variants(
        self,
        case_id: str,
        variant_type: str = "clinical",
        category: str = "outlier",
        hgnc_id: Optional[str] = None,
        projection: Optional[Dict] = None,
    ):
        """Return omics variants for a case, of a particular type (clinical, research) and category (outlier, ...)."""

        query = {"case_id": case_id, "variant_type": variant_type, "category": category}

        if hgnc_id:
            query["genes.hgnc_id"] = hgnc_id

        return self.omics_variant_collection.find(query, projection)
