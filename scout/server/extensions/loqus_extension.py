"""Code for loqus flask extension

* Requires loqusdb version 2.5 or greater.
* If multiple instances are configured, version will be default's.
"""
import json
import logging
import subprocess
import traceback
from subprocess import CalledProcessError

from scout.exceptions.config import ConfigError
from scout.utils.scout_requests import get_request_json as api_get

LOG = logging.getLogger(__name__)

BINARY_PATH = "binary_path"
CONFIG_PATH = "config_path"
API_URL = "api_url"


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
        # traceback contains subprocess' error code and command that failed
        LOG.error("Error calling Loqusdb - {} ".format(traceback.format_exc()))
        raise err
    return output.decode("utf-8")


class LoqusDB:
    """Interface to loqusdb from Flask
    Initialized from server/app.py (extensions.loqusdb.init_app(app))
    Loqus config params should be set in Scout config file
    """

    def __init__(self):
        self.loqusdb_settings = {}
        self.loqus_ids = []

    def settings_list_to_dict(self, cfg):
        """Convert LoqusDB list of settings into dictionary settings.

        Args:
            cgf(list): list of dictionaries probably containing containing key/values "binary_path" and "config_path"
        """
        for setting in cfg:
            cfg_id = setting.get("id") or "default"
            self.loqusdb_settings[cfg_id] = setting

    def init_app(self, app):
        """Initialize LoqusDB from Flask app and check that settings are valid."""
        LOG.info("Init and check loqusdb connection settings")
        cfg = app.config["LOQUSDB_SETTINGS"]

        if isinstance(cfg, list):  # A list of dict instances
            self.settings_list_to_dict(cfg)
            LOG.warning(
                "Deprecated settings: Scout version >=5 will no longer accept LoqusDB settings defined as a list. For additional info please check the Scout admin guide."
            )
        elif isinstance(cfg, dict) and (
            "binary_path" in cfg or "api_url" in cfg
        ):  # One instance, formatted as a dictionary
            self.loqusdb_settings[cfg.get("id") or "default"] = cfg
            LOG.warning(
                "Deprecated settings: Scout version >=5 will no longer accept LoqusDB settings missing the instance ID. For additional info please check the Scout admin guide."
            )
        elif isinstance(
            cfg, dict
        ):  # Multiple Loqus settings in a dictionary, each key is a distinct instance
            for cfg_id, setting in cfg.items():
                self.loqusdb_settings[cfg_id] = setting

        for key, setting in self.loqusdb_settings.items():
            # Scout might connect to Loqus via an API or an executable, define which one for every instance
            setting["instance_type"] = "api" if setting.get(API_URL) else "exec"
            setting["id"] = key
            if app.config["TESTING"] is True:
                setting["version"] = "2.5"
            else:
                setting["version"] = self.get_instance_version(setting)
            self.version_check(setting)

        self.loqus_ids = self.loqusdb_settings.keys()
        LOG.debug(f"LoqusDB setup: {self.__repr__()}")

    def version_check(self, loqusdb_settings):
        """Check if a compatible version is used otherwise raise an error"""
        if not loqusdb_settings["version"] >= "2.5":
            LOG.info("Please update your loqusdb version to >=2.5")
            raise EnvironmentError("Only compatible with loqusdb version >= 2.5")

    def get_instance_version(self, instance_settings):
        """Returns version of a LoqusDB instance.
        Args:
            instance_settings(dict) : The settings of a specific loqusdb instance

        Returns:
            version (string)
        """
        version = None
        if instance_settings["instance_type"] == "api":
            version = self.get_api_loqus_version(api_url=instance_settings.get(API_URL))
        else:
            version = self.get_exec_loqus_version(loqusdb_id=instance_settings.get("id"))

        return version

    @staticmethod
    def get_api_loqus_version(api_url):
        """Get version of LoqusDB instance available from a REST API"""
        if api_url is None:
            return None
        json_resp = api_get("".join([api_url, "/"]))
        version = json_resp.get("content", {}).get("loqusdb_version")
        if version is None:
            raise ConfigError(f"LoqusDB API url '{api_url}' did not return a valid response.")

        return version

    def get_exec_loqus_version(self, loqusdb_id=None):
        """Get LoqusDB version as string"""
        call_str = self.get_command(loqusdb_id)
        call_str.extend(["--version"])
        LOG.debug("call_str: {}".format(call_str))
        try:
            output = execute_command(call_str)
        except CalledProcessError:
            return "-1.0"

        version = output.rstrip().split(" ")[-1]
        LOG.debug("version: {}".format(version))
        return version

    def case_count(self, variant_category, loqusdb_id="default"):
        """Returns number of cases in loqus instance

        Args:
            loqusdb_id(string)

        Returns:
            nr_cases(int)
        """
        nr_cases = 0
        loqus_instance = self.loqusdb_settings.get(loqusdb_id)
        if loqus_instance is None:
            LOG.error(f"Could not find a Loqus instance with id:{loqusdb_id}")
            return nr_cases

        # loqus queried via executable
        if loqus_instance.get("instance_type") == "exec":
            case_call = self.get_command(loqusdb_id)
            case_call.extend(["cases", "--count", "-t", variant_category])
            output = ""
            try:
                output = execute_command(case_call)
            except CalledProcessError:
                # is returning 0 appropriate after catching a crash?
                return nr_cases
            try:
                nr_cases = int(output.strip())
            except ValueError:
                pass

        else:  # loqus queried via REST API
            search_url = f"{loqus_instance.get(API_URL)}/cases"
            search_resp = api_get(search_url)
            if search_resp.get("status_code") != 200:
                return 0
            if variant_category == "snv":
                nr_cases = search_resp.get("content", {}).get("nr_cases_snvs", 0)
            elif variant_category == "sv":
                nr_cases = search_resp.get("content", {}).get("nr_cases_svs", 0)

        return nr_cases

    def get_variant(self, variant_info, loqusdb_id="default"):
        """Return information for a variant (SNV or SV) from loqusdb

        Args:
            variant_info(dict)
            loqusdb_id(string)

        Returns:
            loqus_variant(dict)
        """
        loqus_instance = self.loqusdb_settings.get(loqusdb_id)
        if loqus_instance is None:
            LOG.error(f"Could not find a Loqus instance with id:{loqusdb_id}")
            return

        if loqus_instance.get("instance_type") == "exec":
            return self.get_exec_loqus_variant(loqus_instance, variant_info)

        # Loqus instance is a REST API
        return self.get_api_loqus_variant(loqus_instance.get(API_URL), variant_info)

    @staticmethod
    def get_api_loqus_variant(api_url, variant_info):
        """get variant data using a Loqus instance available via REST API

        SNV/INDELS can be queried in loqus by defining a simple id. For SVs we need to call them
        with coordinates.

        Args:
            api_url(str): query url for the Loqus API
            variant_info(dict): dictionary containing variant coordinates

        Returns:
            res(dict)
        """
        category = "variants" if variant_info["category"] == "snv" else "svs"
        search_url = f"{api_url}/{category}"

        if category == "variants":  # SNVs
            search_url = f"{search_url}/{variant_info['_id']}"
        else:  # SVs
            chrom = variant_info["chrom"]
            end_chrom = variant_info["end_chrom"]
            pos = variant_info["pos"]
            end = variant_info["end"]

            sv_type = variant_info["variant_type"]
            search_url = f"{search_url}/svs/?chrom={chrom}&end_chrom={end_chrom}&pos={pos}&end={end}&sv_type={sv_type}"

        search_resp = api_get(search_url)
        if search_resp.get("status_code") != 200:
            LOG.info(search_resp.get("detail"))
            return {}
        return search_resp.get("content")

    def get_exec_loqus_variant(self, loqus_instance, variant_info):
        """Get variant data using a local executable instance of Loqus

        SNV/INDELS can be queried in loqus by defining a simple id. For SVs we need to call them
        with coordinates.

        Args:
            loqus_instance(dict)
            variant_info(dict)

        Returns:
            res(dict)
        """
        loqus_id = variant_info["_id"]
        cmd = self.get_command(loqus_instance.get("id"))
        cmd.extend(["variants", "--to-json", "--variant-id", loqus_id, "--case-count"])
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
        try:
            output = execute_command(cmd)
            if output is not None:
                return json.loads(output)
        except CalledProcessError:
            pass
        return {}

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

    def get_bin_path(self, loqusdb_id="default"):
        """Return path to `loqusdb` binary as configured per loqusdb_id or default

        Args:
            loqusdb(str)

        Returns:
            path_to_bin(str)
        """
        if loqusdb_id in [None, "", "default"]:
            return self.loqusdb_settings["default"].get(BINARY_PATH)
        try:
            return self.loqusdb_settings.get(loqusdb_id).get(BINARY_PATH)
        except AttributeError:
            raise ConfigError("LoqusDB id not found: {}".format(loqusdb_id))

    def get_config_path(self, loqusdb_id="default"):
        """Return path to `loqusdb` config arguments  as configured per loqusdb_id or default

        Args:
            loqusdb(str)

        Returns:
            path_to_cfg(str)
        """
        if loqusdb_id in [None, "", "default"]:
            return self.loqusdb_settings["default"].get(CONFIG_PATH)
        try:
            return self.loqusdb_settings.get(loqusdb_id).get(CONFIG_PATH)
        except AttributeError:
            raise ConfigError("LoqusDB id not found: {}".format(loqusdb_id))

    def get_command(self, loqusdb_id="default"):
        """Get command string, with additional arguments if configured

        Returns: path(str)"""
        path = [self.get_bin_path(loqusdb_id)]
        args = self.get_config_path(loqusdb_id)
        if args:
            path.extend(["--config", args])
        return path

    def __repr__(self):
        return f"LoqusDB(loqusdb_settings={self.loqusdb_settings}."
