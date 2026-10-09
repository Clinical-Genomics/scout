import logging
import subprocess
import tempfile
from pathlib import Path
from typing import TextIO

from flask import current_app

LOG = logging.getLogger(__name__)


class ExternalVariantLoader:
    """Run external variant loaders."""

    def run_scout_loader(self, case_config: TextIO) -> None:
        """Run scout_loader using the provided case configuration file.

        Create a temporary TOML configuration with Scout's MongoDB connection
        settings, invoke the Rust loader, and remove the temporary configuration
        when execution finishes.

        scout_loader (https://github.com/Clinical-Genomics/scout_loader)

        Args:
            case_config: Open file containing the case configuration YAML.

        Raises:
            subprocess.CalledProcessError: If scout_loader exits with a non-zero status.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            mongo_config_path = Path(temp_dir) / "config.toml"
            mongo_uri = current_app.config.get("MONGO_URI") or "mongodb://127.0.0.1:27017"
            mongo_dbname = current_app.config.get("MONGO_DBNAME") or "scout-demo"
            mongo_config_path.write_text(
                f'mongo_uri = "{mongo_uri}"\n' f'mongo_dbname = "{mongo_dbname}"\n',
                encoding="utf-8",
            )

            subprocess.run(
                [
                    current_app.config["VARIANTS_LOADER"],
                    "--case-config",
                    str(case_config.name),
                    "--config",
                    str(mongo_config_path),
                ],
                check=True,
            )
