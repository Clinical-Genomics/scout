# stdlib modules
import logging

from typing import Dict

from scout.constants import OMICS_FILE_TYPE_MAP
from scout.parse.omics_variant import parse_omics_file

LOG = logging.getLogger(__name__)


class OmicsVariantHandler(OmicsVariantLoader):
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

    def load_omics_variants(self, case_obj: str, file_type: str):
        """Load OMICS variants for a case"""

        gene_to_panels = self.gene_to_panels(case_obj)
        genes = [gene_obj for gene_obj in self.all_genes(build=build)]
        hgncid_to_gene = self.hgncid_to_gene(genes=genes, build=build)

        nr_inserted = 0

        # FIXME pass filename on dict
        file_handle = open(case_obj["omics_files"].get(file_type), "r")
        omics_infos = parse_omics_file(
            file_handle, omics_file_type=case_obj["omics_files"].get(file_type)
        )

        for info in omics_infos:
            omics_model_obj = OmicsVariantLoader(**info).model_dump()

    def omics_variant(self, id: str):
        """Return omics variant"""

    def omics_variants(
        self, case_id: str, variant_type: str = "clinical", category: str = "outlier"
    ):
        """Return omics variants"""
