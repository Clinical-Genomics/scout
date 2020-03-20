"""Code for loqus flask extension"""
import copy
import json
import logging
import subprocess
from subprocess import CalledProcessError

LOG = logging.getLogger(__name__)


def execute_command(cmd):
    """
        Prints stdout + stderr of command in real-time while being executed

    Args:
        cmd (list): command sequence

    Yields:
        line (str): line of output from command
    """
    output = ""
    message = " ".join(cmd)
    LOG.info("Running: %s", message)
    try:
        output = subprocess.check_output(cmd, shell=False)
    except CalledProcessError as err:
        LOG.warning("Something went wrong with loqusdb")
        raise err

    output = output.decode("utf-8")

    if not output:
        return output

    return output


class LoqusDB:
    """Interface to loqusdb from Scout"""

    def __init__(self, loqusdb_binary=None, loqusdb_config=None, version=None):
        """Initialise from args"""
        self.loqusdb_binary = loqusdb_binary
        self.loqusdb_config = loqusdb_config
        self.version = version or 0.0
        LOG.info(
            "Initializing loqus extension with binary: %s, version: %d",
            self.loqusdb_binary,
            self.version,
        )

        self.base_call = [self.loqusdb_binary]
        if self.loqusdb_config:
            self.base_call.extend(["--config", self.loqusdb_config])

    def init_app(self, app):
        """Initialize from Flask."""
        LOG.info("Connecting to loqusdb")
        self.loqusdb_binary = app.config["LOQUSDB_SETTINGS"].get(
            "binary_path", "loqusdb"
        )
        LOG.info("Use loqusdb: %s", self.loqusdb_binary)
        self.loqusdb_config = app.config["LOQUSDB_SETTINGS"].get("config_path")

        self.base_call = [self.loqusdb_binary]
        if self.loqusdb_config:
            LOG.info("Use loqusdb config file %s", self.loqusdb_config)
            self.base_call.extend(["--config", self.loqusdb_config])

        self.version = app.config["LOQUSDB_SETTINGS"].get("version")
        if not self.version:
            self.version = self.get_version()
        self.version_check()

    def version_check(self):
        """Check if a compatible version is used"""
        if not self.version >= 2.5:
            LOG.info("Please update your loqusdb version to >=2.5")
            raise SyntaxError("Only compatible with loqusdb version >= 2.5")

    @staticmethod
    def set_coordinates(variant_info):
        """Update coordinates depending on variant type

        Some SVs have tricky ways to represent coordinates.

        - Insertions have the same start and end position but they have a length
        - Some of them have a unknown length which will then be -1.

        This function will calculate the end position based on these assumptions.

        Args:
            variant_info(dict)
        """
        sv_type = variant_info.get("variant_type")
        start = variant_info["pos"]
        end = variant_info["end"]
        length = variant_info.get("length", -1)
        # Insertions have same start and end positions
        if sv_type == "INS" and length > 0:
            end = start + length
            LOG.info("Updating length to %s", end)
        variant_info["end"] = end

    def get_variant(self, variant_info):
        """Return information for a variant from loqusdb

        SNV/INDELS can be queried in loqus by defining a simple id. For SVs we need to call them
        with coordinates.

        Args:
            variant_info(dict)

        Returns:
            loqus_variant(dict)
        """
        loqus_id = variant_info["_id"]
        variant_call = copy.deepcopy(self.base_call)
        variant_call.extend(["variants", "--to-json", "--variant-id", loqus_id])
        # If sv we need some more info
        if variant_info.get("category", "snv") in ["sv"]:
            self.set_coordinates(variant_info)

            variant_call.extend(
                [
                    "-t",
                    "sv",
                    "-c",
                    variant_info["chrom"],
                    "-s",
                    str(variant_info["pos"]),
                    "-e",
                    str(variant_info["end"]),
                    "--end-chromosome",
                    variant_info["end_chrom"],
                    "--sv-type",
                    variant_info["variant_type"],
                ]
            )

        if self.version > 2.4:
            variant_call.extend(["--case-count"])

        output = ""
        try:
            output = execute_command(variant_call)
        except CalledProcessError as err:
            LOG.warning("Something went wrong with loqus")
            raise err

        res = {}
        if output:
            res = json.loads(output)

        if self.version < 2.5:
            res["total"] = self.case_count()

        return res

    def case_count(self):
        """Returns number of cases in loqus instance

        Returns:
            nr_cases(int)
        """
        nr_cases = 0
        case_call = copy.deepcopy(self.base_call)

        case_call.extend(["cases", "--count"])
        output = ""
        try:
            output = execute_command(case_call)
        except CalledProcessError:
            LOG.warning("Something went wrong with loqus")
            return nr_cases

        if not output:
            LOG.info("Could not find information about loqusdb cases")
            return nr_cases

        try:
            nr_cases = int(output.strip())
        except ValueError:
            pass

        return nr_cases

    def get_version(self):
        """Test if loqus version"""
        version_call = copy.deepcopy(self.base_call)
        version_call.extend(["--version"])
        loqus_version = 0.0

        try:
            output = execute_command(version_call)
        except CalledProcessError:
            LOG.warning("Something went wrong with loqus")
            return loqus_version

        version = output.rstrip().split(" ")[-1]
        if version:
            return float(version)

        return loqus_version

    def __repr__(self):
        return f"LoqusDB(binary={self.loqusdb_binary}," f"config={self.loqusdb_config})"
