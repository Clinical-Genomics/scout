"""Code for loqus flask extension"""
import copy
import json
import logging
import subprocess
from subprocess import CalledProcessError

LOG = logging.getLogger(__name__)


# TODO: add in documentation requirement of loqusdb vsn 2.5 or greater


def execute_command(cmd):
    """
        Prints stdout + stderr of command in real-time while being executed

    Args:
        cmd (list): command sequence

    Yields:
        line (str): line of output from command
    """
    output = ""
    cmd = [x for x in cmd if x != []]  # remove empty lists
    cmd_string = " ".join(cmd)  # remove empty list
    LOG.info("Running: %s", cmd_string)
    try:
        output = subprocess.check_output(cmd, shell=False)
    except CalledProcessError as err:
        LOG.warning("Something went wrong with loqusdb")
        raise err

    return output.decode("utf-8")


class LoqusDB:
    """Interface to loqusdb from Flask

     NOTE: * initialied in __init__.py
           * in practice this is a singleton class
           * configured in `confgi.py`"""

    # TODO: rename 'config_path to args'
    # TODO: decorator for try/catch undefined dict attributes
    # TODO: version is no longer checked in init_app() -when? where? never?
    # -could loqusdb be updated to return non-zero value and we handle that instead

    def __init__(self, loqusdb_binary=None, loqusdb_args=None):
        """Initialise from args"""
        self.loqusdb_settings = [
            {"id": "default", "binary_path": loqusdb_binary, "config_path": loqusdb_args,}
        ]
        LOG.info("Initializing loqus extension with config: %s", self.loqusdb_settings)

    def init_app(self, app):
        """Initialize from Flask."""
        LOG.info("Init loqusdb app")
        self.loqusdb_settings = app.config["LOQUSDB_SETTINGS"]
        LOG.info("Use loqusdb config file %s", self.loqusdb_settings)

    # version_check() is not called now after implementation of loqusdb per institute
    # -don't know institute until page is loaded
    def version_check(self):
        """Check if a compatible version is used otherwise raise an error"""
        if not self.version >= 2.5:
            LOG.info("Please update your loqusdb version to >=2.5 (current: {})").format(
                self.version
            )
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

        Args:=
            variant_info(dict)
            loqusdb_id(string)

        Returns:
            loqus_variant(dict)
        """
        loqus_id = variant_info["_id"]
        cmd = [self.get_bin_path(loqusdb_id)]
        args = self.get_config_path(loqusdb_id)
        if args:
            cmd.extend(["--config", [args]])
        cmd.extend(["variants", "--to-json", "--variant-id", loqus_id])
        # TODO: add version check here instead? 2.5 needed for json export?!
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
        return res

    def search_dictlist(self, key):
        """Search list of dicts, """
        for i in self.loqusdb_settings:
            if i.get("id") == key:
                return i
        return None

    def default_setting(self):
        """Get default loqusdb configuration  """
        return self.search_dictlist("default")

    def get_bin_path(self, loqusdb_id=None):
        """Return path to `loqusdb` binary as configured per
        loqusdb_id or default"""
        if isinstance(self.loqusdb_settings, list) and loqusdb_id is None:
            return self.default_setting().get("binary_path")
        elif isinstance(self.loqusdb_settings, list) and loqusdb_id is not None:
            return self.search_dictlist(loqusdb_id).get("binary_path")
        else:
            return self.loqusdb_settings.get("binary_path")

    def get_config_path(self, loqusdb_id=None):
        """Return path to `loqusdb` config arguments  as configured per
        loqusdb_id or default"""
        if isinstance(self.loqusdb_settings, list) and loqusdb_id is None:
            return self.default_setting().get("config_path")
        elif isinstance(self.loqusdb_settings, list) and loqusdb_id is not None:
            return self.search_dictlist(loqusdb_id).get("config_path")
        else:
            return self.loqusdb_settings.get("config_path")

    # XXX: not called since removal of version check >=2.5
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
        """Get LoqusDB verson as float"""
        call_str = [self.get_bin_path()]
        call_str.extend(["--version"])
        print("***-----")
        print(call_str)
        try:
            output = execute_command(call_str)
        except CalledProcessError:
            LOG.warning("Something went wrong with loqus")
            return -1.0

        version = output.rstrip().split(" ")[-1]
        return float(version)

    def __repr__(self):
        return f"LoqusDB(loqusdb_settings={self.loqusdb_settings},"
