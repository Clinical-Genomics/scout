import logging
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, TextIO

import yaml
from flask import current_app

LOG = logging.getLogger(__name__)
from scout.constants import ORDERED_FILE_TYPE_MAP

CLINICAL_VCF_FIELDS = [
    file_type
    for file_type, config in ORDERED_FILE_TYPE_MAP.items()
    if config["variant_type"] == "clinical"
]

RESEARCH_VCF_FIELDS = [
    file_type
    for file_type, config in ORDERED_FILE_TYPE_MAP.items()
    if config["variant_type"] == "research"
]


class ExternalVariantLoader:
    """Run external variant loaders."""

    @staticmethod
    @contextmanager
    def temp_case_config_from_case_dict(
        case_obj: dict, is_research: bool = False
    ) -> Iterator[TextIO]:
        """Create a temporary case config YAML file from a case dictionary."""
        case_config = {
            "family": case_obj.get("_id", case_obj.get("case_id")),
            "owner": case_obj["owner"],
            "human_genome_build": case_obj["genome_build"],
            "rank_score_threshold": int(case_obj["rank_score_threshold"]),
            "samples": [
                {
                    "sample_id": individual["individual_id"],
                    "sample_name": individual.get("display_name"),
                    "phenotype": "affected" if individual.get("phenotype") == "2" else "unaffected",
                }
                for individual in case_obj.get("individuals", [])
            ],
        }

        vcf_files = case_obj.get("vcf_files", {})

        if is_research:
            case_config.update(
                {key: vcf_files[key] for key in RESEARCH_VCF_FIELDS if key in vcf_files}
            )
        else:
            case_config.update(
                {key: vcf_files[key] for key in CLINICAL_VCF_FIELDS if key in vcf_files}
            )
            case_config["gene_panels"] = case_obj.get("gene_panels", [])

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".yaml",
            encoding="utf-8",
        ) as yaml_file:
            yaml.safe_dump(case_config, yaml_file, sort_keys=False)
            yaml_file.flush()
            yield yaml_file

    @staticmethod
    def run_external_scout_loader(case_obj: dict, is_research: bool = False) -> None:
        """Run scout_loader using the provided case configuration file.

        Create a temporary TOML configuration with Scout's MongoDB connection
        settings, invoke the Rust loader, and remove the temporary configuration
        when execution finishes.

        scout_loader (https://github.com/Clinical-Genomics/scout_loader)

        Args:
            case_obj: file containing the case configuration data.
            is_research: load research variants instead of clinical variants

        Raises:
            subprocess.CalledProcessError: If scout_loader exits with a non-zero status.
        """
        with (
            ExternalVariantLoader.temp_case_config_from_case_dict(
                case_obj=case_obj, is_research=is_research
            ) as case_yaml_file,
            tempfile.TemporaryDirectory() as temp_dir,
        ):
            mongo_config_path = Path(temp_dir) / "config.toml"
            mongo_uri = current_app.config.get("MONGO_URI") or "mongodb://127.0.0.1:27017"
            mongo_dbname = current_app.config.get("MONGO_DBNAME") or "scout-demo"
            mongo_config_path.write_text(
                f'mongo_uri = "{mongo_uri}"\nmongo_dbname = "{mongo_dbname}"\n',
                encoding="utf-8",
            )

            command = [
                current_app.config["VARIANTS_LOADER"],
                "--case-config",
                str(case_yaml_file.name),
                "--config",
                str(mongo_config_path),
            ]

            if is_research:
                command.append("--research")

            subprocess.run(command, check=True)
