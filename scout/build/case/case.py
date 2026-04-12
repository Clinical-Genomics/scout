"""Build module for creating case objects ready for database insertion.

This module provides factory methods and helper functions for building case and
phenotype objects. It uses Pydantic models for validation and the CaseFactory
pattern for orchestrating complex object construction.
"""

import logging
from typing import Dict

from scout.build.case.factory import CaseFactory

LOG = logging.getLogger(__name__)


def build_phenotype(phenotype_id: str, adapter) -> Dict[str, str]:
    """Build a small phenotype object with ID and description.

    This is a convenience function that uses the CaseFactory's method.
    It builds a dictionary with phenotype_id and description from the HPO term.

    Args:
        phenotype_id: HPO term ID (e.g., "HP:0001250")
        adapter: MongoAdapter instance for database queries

    Returns:
        dict with phenotype_id and feature (description), or empty dict if not found

    Example:
        >>> pheno = build_phenotype("HP:0001250", adapter)
        >>> print(pheno)
        {'phenotype_id': 'HP:0001250', 'feature': 'Seizures'}
    """
    factory = CaseFactory(adapter)
    return factory.build_phenotype(phenotype_id)


def build_case(case_data: dict, adapter) -> dict:
    """Build a case object that is to be inserted to the database.

    This function uses the CaseFactory to build a validated case dictionary
    ready for database insertion. It orchestrates the building of individuals,
    panels, phenotypes, and all case metadata while ensuring all necessary
    fields are populated and relationships are validated.

    The function performs the following operations:
    1. Validates required fields (case_id, owner)
    2. Validates institute exists in database
    3. Builds and validates all individuals
    4. Processes gene panels
    5. Processes phenotype terms and groups
    6. Handles cohorts and may update institute with new cohorts
    7. Collects and validates all files/reports
    8. Determines which variant types are present

    All fields that exist in the original code are preserved in the output.

    Args:
        case_data: Dictionary with case information including:
            - case_id: Unique case identifier (required)
            - owner: Institute ID that owns the case (required)
            - display_name: Human-readable case name (optional, defaults to case_id)
            - individuals: List of individual dictionaries
            - gene_panels: List of gene panel names
            - default_panels: List of gene panel names to display by default
            - And many optional fields for reports, analysis info, etc.
        adapter: MongoAdapter instance for database queries

    Returns:
        dict: Validated case data ready for database insertion with fields:
            - _id: Case identifier (from case_id)
            - display_name: Display name of the case
            - owner: Institute that owns the case
            - collaborators: List of institutes that can view the case
            - individuals: List of validated individual dictionaries
            - created_at, updated_at: Timestamps
            - scout_load_version: Version of Scout used to load the case
            - panels: List of validated gene panel information
            - phenotype_terms: Phenotype terms if provided
            - phenotype_groups: Phenotype groups if provided
            - vcf_files: VCF file paths
            - omics_files: Omics analysis files
            - Various flags: has_svvariants, has_strvariants, etc.
            - And many other fields (see scout/models/case_db.py for complete list)

    Raises:
        ConfigError: If case is missing required fields (case_id, owner)
        IntegrityError: If referenced institute doesn't exist in database
        PedigreeError: If individual data is invalid or relationships inconsistent

    Example:
        >>> case_data = {
        ...     'case_id': 'family_001',
        ...     'owner': 'cust000',
        ...     'display_name': 'Family 001',
        ...     'individuals': [...],
        ...     'gene_panels': ['panel_1', 'panel_2'],
        ...     'genome_build': '38',
        ... }
        >>> case_dict = build_case(case_data, adapter)
        >>> adapter.case_collection.insert_one(case_dict)
    """
    factory = CaseFactory(adapter)
    return factory.build_case(case_data)
