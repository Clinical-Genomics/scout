"""Factory pattern implementation for building case and individual objects.

This module provides a CaseFactory class that orchestrates the building of
individual and case objects with Pydantic validation, ensuring data consistency
and type safety before database insertion.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from scout import __version__
from scout.constants import PHENOTYPE_GROUPS
from scout.exceptions import ConfigError, IntegrityError
from scout.models.case.case import Case
from scout.models.individual import Individual

LOG = logging.getLogger(__name__)


class CaseFactory:
    """Factory for building validated Case objects with related Individuals.

    This factory encapsulates the logic for constructing case dictionaries
    that are ready for database insertion. It uses Pydantic models for validation
    and provides helper methods for common operations.

    Example:
        >>> factory = CaseFactory(adapter)
        >>> case_dict = factory.build_case(case_data)
    """

    def __init__(self, adapter):
        """Initialize the factory with a database adapter.

        Args:
            adapter: MongoAdapter instance for database queries
        """
        self.adapter = adapter

    def build_phenotype(self, phenotype_id: str) -> Dict[str, str]:
        """Build a small phenotype object with ID and description.

        Args:
            phenotype_id: HPO term ID (e.g., "HP:0001250")

        Returns:
            dict with phenotype_id and feature (description)
        """
        phenotype_obj = {}
        phenotype = self.adapter.hpo_term(phenotype_id)
        if phenotype:
            phenotype_obj["phenotype_id"] = phenotype["hpo_id"]
            phenotype_obj["feature"] = phenotype["description"]
        return phenotype_obj

    def build_individual(self, ind_data: dict) -> dict:
        """Build and validate an Individual object.

        This method converts input individual data into a validated Individual
        model, handling path resolution and type conversions.

        Args:
            ind_data: Dictionary with individual information

        Returns:
            dict: Individual data ready for database insertion

        Raises:
            PedigreeError: If required fields are missing or invalid
        """
        try:
            # Create validated Pydantic model
            individual = Individual(**ind_data)
            return individual.to_dict()
        except Exception as err:
            LOG.error(
                f"Error building individual {ind_data.get('individual_id', 'unknown')}: {err}"
            )
            raise

    def _populate_pipeline_info(self, case_obj: dict, case_data: dict) -> None:
        """Populate pipeline version information.

        Args:
            case_obj: Case dictionary to update
            case_data: Input case data
        """
        if case_data.get("exe_ver"):
            case_obj["pipeline_version"] = case_data["exe_ver"]

    def _process_panels(self, case_data: dict) -> List[Dict[str, Any]]:
        """Process and validate gene panels for the case.

        Args:
            case_data: Input case data

        Returns:
            List of panel dictionaries with metadata
        """
        case_panels = case_data.get("gene_panels", [])
        default_panels = case_data.get("default_panels", [])
        panels = []

        for panel_name in case_panels:
            panel_obj = self.adapter.gene_panel(panel_name)
            if not panel_obj:
                LOG.warning(f"Panel {panel_name} does not exist in database and will not be saved.")
                continue

            panel = {
                "panel_id": panel_obj["_id"],
                "panel_name": panel_obj["panel_name"],
                "display_name": panel_obj["display_name"],
                "version": panel_obj["version"],
                "updated_at": panel_obj["date"],
                "nr_genes": len(panel_obj["genes"]),
                "is_default": panel_name in default_panels,
            }
            panels.append(panel)

        return panels

    def _process_phenotypes(self, case_data: dict) -> Optional[List[Dict[str, str]]]:
        """Process and validate phenotype terms.

        Args:
            case_data: Input case data

        Returns:
            List of phenotype dictionaries or None
        """
        if not case_data.get("phenotype_terms"):
            return None

        phenotypes = []
        for phenotype_id in case_data["phenotype_terms"]:
            phenotype_obj = self.adapter.hpo_term(phenotype_id)
            if phenotype_obj is None:
                LOG.warning(f"HPO term '{phenotype_id}' not found in database, skipping.")
                continue

            phenotypes.append(
                {
                    "phenotype_id": phenotype_id,
                    "feature": phenotype_obj.get("description"),
                }
            )

        return phenotypes or None

    def _process_phenotype_groups(
        self, case_data: dict, institute_obj: dict, institute_id: str
    ) -> Optional[List[Dict[str, str]]]:
        """Process and validate phenotype groups.

        Args:
            case_data: Input case data
            institute_obj: Institute object from database
            institute_id: Institute ID

        Returns:
            List of phenotype group dictionaries or None
        """
        if not case_data.get("phenotype_groups"):
            return None

        phenotype_groups = []
        institute_phenotype_groups = set(PHENOTYPE_GROUPS.keys())
        if institute_obj.get("phenotype_groups"):
            institute_phenotype_groups.update(institute_obj.get("phenotype_groups").keys())

        for phenotype in case_data["phenotype_groups"]:
            if phenotype not in institute_phenotype_groups:
                LOG.warning(
                    f"Phenotype group '{phenotype}' not found for institute '{institute_id}'."
                )
                continue

            phenotype_obj = self.build_phenotype(phenotype)
            if phenotype_obj:
                phenotype_groups.append(phenotype_obj)
            else:
                LOG.warning(f"Could not find phenotype group '{phenotype}' in term collection.")

        return phenotype_groups or None

    def _process_cohorts(self, case_obj: dict, case_data: dict, institute_obj: dict) -> None:
        """Process and store cohort information, updating institute if needed.

        Args:
            case_obj: Case dictionary to update
            case_data: Input case data
            institute_obj: Institute object from database
        """
        if not case_data.get("cohorts"):
            return

        case_obj["cohorts"] = case_data["cohorts"]

        # Check if all case cohorts are registered under the institute
        institute_cohorts = set(institute_obj.get("cohorts", []))
        all_cohorts = institute_cohorts.union(set(case_obj["cohorts"]))
        if len(all_cohorts) > len(institute_cohorts):
            LOG.warning("Updating institute with new cohort terms")
            self.adapter.institute_collection.find_one_and_update(
                {"_id": institute_obj["_id"]}, {"$set": {"cohorts": list(all_cohorts)}}
            )

    def _process_individuals(self, case_data: dict) -> List[dict]:
        """Process and validate individuals for the case.

        Args:
            case_data: Input case data

        Returns:
            List of validated individual dictionaries, sorted by phenotype

        Raises:
            PedigreeError: If individual data is invalid
        """
        ind_objs = []
        try:
            for individual_data in case_data.get("individuals", []):
                ind_objs.append(self.build_individual(individual_data))
        except Exception:
            raise

        # Sort individuals by phenotype (affected first)
        sorted_inds = sorted(ind_objs, key=lambda ind: -ind["phenotype"])
        return sorted_inds

    def build_case(self, case_data: dict) -> dict:
        """Build a complete case object ready for database insertion.

        This is the main entry point for case building. It orchestrates the
        building of all sub-components and applies all validations.

        Args:
            case_data: Dictionary with case information including:
                - case_id: Unique case identifier (required)
                - owner: Institute ID that owns the case (required)
                - display_name: Human-readable case name
                - individuals: List of individual dictionaries
                - gene_panels: List of gene panel names
                - And many optional fields (see scout/models/case_db.py)

        Returns:
            dict: Validated case data ready for database insertion

        Raises:
            ConfigError: If case is missing required owner
            IntegrityError: If referenced institute doesn't exist
            PedigreeError: If individual data is invalid
        """
        LOG.info(f"Building case with id: {case_data.get('case_id')}")

        # Validate case_id
        try:
            case_id = case_data["case_id"]
        except KeyError:
            raise ConfigError("Case must have a case_id")

        # Validate and get institute
        try:
            owner = case_data["owner"]
        except KeyError:
            raise ConfigError("Case must have an owner")

        institute_obj = self.adapter.institute(owner)
        if not institute_obj:
            raise IntegrityError(f"Institute {owner} not found in database")

        # Start building case object
        now = datetime.now()
        case_obj = {
            "_id": case_id,
            "display_name": case_data.get("display_name", case_id),
            "owner": owner,
            "created_at": now,
            "updated_at": now,
            "scout_load_version": __version__,
        }

        # Collaborators (always include owner)
        collaborators = set(case_data.get("collaborators", []))
        collaborators.add(owner)
        case_obj["collaborators"] = list(collaborators)

        # Optional: assignees
        if case_data.get("assignee"):
            case_obj["assignees"] = [case_data["assignee"]]

        # Optional: paraphrase
        if case_data.get("paraphrase"):
            case_obj["paraphrase"] = case_data["paraphrase"]

        # Optional: SMA TSV
        if case_data.get("smn_tsv"):
            case_obj["smn_tsv"] = case_data["smn_tsv"]

        # Process individuals
        case_obj["individuals"] = self._process_individuals(case_data)

        # Suspects and causatives
        if case_data.get("suspects"):
            case_obj["suspects"] = case_data["suspects"]
        if case_data.get("causatives"):
            case_obj["causatives"] = case_data["causatives"]

        # Case metadata
        case_obj["synopsis"] = case_data.get("synopsis", "")
        case_obj["status"] = case_data.get("status") or "inactive"
        case_obj["is_research"] = False
        case_obj["research_requested"] = False
        case_obj["rerun_requested"] = False
        case_obj["lims_id"] = case_data.get("lims_id", "")
        case_obj["analysis_date"] = case_data.get("analysis_date", now)

        # Gene panels
        case_obj["panels"] = self._process_panels(case_data)
        case_obj["dynamic_gene_list"] = []

        # Genome builds
        case_obj["genome_build"] = case_data.get("genome_build", "37")
        case_obj["rna_genome_build"] = case_data.get("rna_genome_build", "38")

        # Rank model info
        for conditional_key in [
            "rank_model_url",
            "rank_model_version",
            "sv_rank_model_url",
            "sv_rank_model_version",
        ]:
            value = case_data.get(conditional_key)
            if value:
                case_obj[conditional_key] = str(value)

        # Rank score threshold
        rank_score = case_data.get("rank_score_threshold")
        if rank_score:
            case_obj["rank_score_threshold"] = float(rank_score)

        # Cohorts (may update institute)
        self._process_cohorts(case_obj, case_data, institute_obj)

        # Phenotypes
        phenotypes = self._process_phenotypes(case_data)
        if phenotypes:
            case_obj["phenotype_terms"] = phenotypes

        # Phenotype groups
        phenotype_groups = self._process_phenotype_groups(case_data, institute_obj, owner)
        if phenotype_groups:
            case_obj["phenotype_groups"] = phenotype_groups

        # Files and reports
        case_obj["madeline_info"] = case_data.get("madeline_info")
        case_obj["custom_images"] = case_data.get("custom_images")

        # VCF and omics files
        case_obj["vcf_files"] = case_data.get("vcf_files", {})
        case_obj["omics_files"] = case_data.get("omics_files", {})
        case_obj["delivery_report"] = case_data.get("delivery_report")
        case_obj["rna_delivery_report"] = case_data.get("rna_delivery_report")

        # Pipeline info
        self._populate_pipeline_info(case_obj, case_data)

        # Determine variant types present
        case_obj["has_svvariants"] = bool(
            case_obj["vcf_files"].get("vcf_sv") or case_obj["vcf_files"].get("vcf_sv_research")
        )
        case_obj["has_strvariants"] = bool(case_obj["vcf_files"].get("vcf_str"))
        case_obj["has_meivariants"] = bool(case_obj["vcf_files"].get("vcf_mei"))
        case_obj["has_outliers"] = bool(
            case_obj["omics_files"].get("fraser")
            or case_obj["omics_files"].get("outrider")
            or case_obj["omics_files"].get("methbat")
        )
        case_obj["has_methylation"] = bool(case_obj["omics_files"].get("methbat"))

        # Migration status
        case_obj["is_migrated"] = False

        # Track (rare or cancer)
        case_obj["track"] = case_data.get("track", "rare")

        # Group
        case_obj["group"] = case_data.get("group", [])

        return case_obj
