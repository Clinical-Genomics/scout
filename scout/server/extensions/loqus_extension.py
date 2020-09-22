"""Code for loqus flask extension

* Requires loqusdb version 2.5 or greater.
* If multiple instances are configured, version will be default's.
"""
import copy
import json
import logging
import subprocess
from subprocess import CalledProcessError
from scout.exceptions.config import ConfigError

LOG = logging.getLogger(__name__)


BINARY_PATH = "binary_path"
CONFIG_PATH = "config_path"
VERSION = "version"


def execute_command(cmd):
    """
        Prints stdout + stderr of command in real-time while being executed

    Args:
        cmd (list): command sequence

    Returns:
        line (str): line of output from command
    """
    output = ""
    cmd = [x for x in cmd if x != []]  # remove empty lists
    cmd_string = " ".join(cmd)  # add spacing to create a command string
    LOG.info("Running command: %s", cmd_string)
    try:
        output = subprocess.check_output(cmd, shell=False)
    except CalledProcessError as err:
        LOG.warning("Something went wrong with loqusdb")
        raise err
    return output.decode("utf-8")


class LoqusDB:
    """Interface to loqusdb from Flask

    NOTE: * initialied in __init__.py called from server/extensins/__init.py__ but also
            init_app is called from server/app.init.
          * in practice this is a singleton class
          * configured in `scout/server/config.py`"""

    def __init__(self, loqusdb_binary=None, loqusdb_config=None, loqusdb_args=None, version=None):
        """Initialise from args"""
        self.loqusdb_settings = [
            {"id": "default", "binary_path": loqusdb_binary, "config_path": loqusdb_args}
        ]
        self.version = version
        LOG.info(
            "Initializing loqus extension with config: %s",
            self.loqusdb_settings,
        )

    def init_app(self, app):
        """Initialize from Flask."""
        LOG.info("Init loqusdb app")
        self.loqusdb_settings = self.app_config(app)
        self.version = self.get_configured_version()
        if not self.version:
            self.version = self.get_version()
        self.version_check()
        LOG.info("Use loqusdb config file %s", self.loqusdb_settings)

    @staticmethod
    def app_config(app):
        """Read config.py to handle single or multiple loqusdb configurations.

        Returns: loqus_db_settings(list)"""
        cfg = app.config["LOQUSDB_SETTINGS"]
        if isinstance(cfg, list):
            return cfg
        # backwards compatible, add default id
        cfg["id"] = "default"
        return [cfg]

    def version_check(self):
        """Check if a compatible version is used otherwise raise an error"""
        if not self.version >= 2.5:
            LOG.info("Please update your loqusdb version to >=2.5")
            raise EnvironmentError("Only compatible with loqusdb version >= 2.5")

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

    def get_variant(self, variant_info, loqusdb_id=None):
        """Return information for a variant from loqusdb

        SNV/INDELS can be queried in loqus by defining a simple id. For SVs we need to call them
        with coordinates.

        Args:
            variant_info(dict)
            loqusdb_id(string)

        Returns:
            loqus_variant(dict)
        Raises:
            EnvironmentError("Only compatible with loqusdb version >= 2.5")
        """
        loqus_id = variant_info["_id"]
        cmd = self.get_command(loqusdb_id)
        cmd.extend(["variants", "--to-json", "--variant-id", loqus_id])
        # If sv we need some more info
        if variant_info.get("category", "snv") in ["sv"]:
            self.set_coordinates(variant_info)
            cmd.extend(
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
            cmd.extend(["--case-count"])

        output = ""
        try:
            output = execute_command(cmd)
        except CalledProcessError as err:
            LOG.warning("Something went wrong with loqus")
            raise err

        res = {}
        if output:
            res = json.loads(output)

        if self.version < 2.5:
            res["total"] = self.case_count()

        return res

    def search_setting(self, key):
        """Search settings for 'key' and return configuration for matchin 'id'

        Returns: {'binary_path':(str), 'id': (str), 'config_path': (str)}"""
        for i in self.loqusdb_settings:
            if i.get("id") == key:
                return i
        return None

    def default_setting(self):
        """Get default loqusdb configuration

        Returns:
            institute_settings(dict)
        """
        return self.search_setting("default")

    def get_bin_path(self, loqusdb_id=None):
        """Return path to `loqusdb` binary as configured per loqusdb_id or default

        Args:
            loqusdb(str)

        Returns:
            path_to_bin(str)
        """
        if loqusdb_id is None or loqusdb_id == "":
            return self.default_setting().get(BINARY_PATH)
        try:
            return self.search_setting(loqusdb_id).get(BINARY_PATH)
        except AttributeError:
            raise ConfigError("LoqusDB id not found: {}".format(loqusdb_id))

    def get_config_path(self, loqusdb_id=None):
        """Return path to `loqusdb` config arguments  as configured per loqusdb_id or default

        Args:
            loqusdb(str)

        Returns:
            path_to_cfg(str)
        """
        if loqusdb_id is None or loqusdb_id == "":
            return self.default_setting().get(CONFIG_PATH)

        try:
            return self.search_setting(loqusdb_id).get(CONFIG_PATH)
        except AttributeError:
            raise ConfigError("LoqusDB id not found: {}".format(loqusdb_id))

    def get_configured_version(self, loqusdb_id=None):
        """Return configured version
        Args:
            loqusdb(str)

        Returns:
            loqus_versio(str)
        """
        if loqusdb_id is None or loqusdb_id == "":
            return self.default_setting().get(VERSION)

        try:
            return self.search_setting(loqusdb_id).get(VERSION)
        except AttributeError:
            raise ConfigError("LoqusDB id not found: {}".format(loqusdb_id))

    def case_count(self):
        """Returns number of cases in loqus instance

        Returns:
            nr_cases(int)
        """
        nr_cases = 0
        case_call = self.get_command()
        case_call.extend(["cases", "--count"])
        output = ""
        try:
            output = execute_command(case_call)
        except CalledProcessError:
            LOG.warning("Something went wrong with loqus")
            return nr_cases

        try:
            nr_cases = int(output.strip())
        except ValueError:
            pass

        return nr_cases

    def get_version(self):
        """Get LoqusDB version as float"""
        if self.version:
            return self.version

        call_str = self.get_command()
        call_str.extend(["--version"])
        LOG.debug("call_str: {}".format(call_str))
        try:
            output = execute_command(call_str)
        except CalledProcessError:
            LOG.warning("Something went wrong with loqus")
            return -1.0

        version = output.rstrip().split(" ")[-1]
        LOG.debug("version: {}".format(version))
        return float(version)

    def __repr__(self):
        return f"LoqusDB(loqusdb_settings={self.loqusdb_settings},"

    def get_command(self, loqusdb_id=None):
        """Get command string, with additional arguments if configured

        Returns: path(str)"""
        path = [self.get_bin_path(loqusdb_id)]
        args = self.get_config_path(loqusdb_id)
        if args:
            path.extend(["--config", args])
        return path
