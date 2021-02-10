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
from scout.utils.scout_requests import get_request_json as api_get

LOG = logging.getLogger(__name__)

BINARY_PATH = "binary_path"
CONFIG_PATH = "config_path"
VERSION = "version"
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
        LOG.warning("Something went wrong with loqusdb")
        raise err
    return output.decode("utf-8")


class LoqusDB:
    """Interface to loqusdb from Flask

    NOTE: * initialied in __init__.py called from server/extensins/__init.py__ but also
            init_app is called from server/app.init.
          * in practice this is a singleton class
          * configured in `scout/server/config.py`"""

    def __init__(
        self,
        loqusdb_binary=None,
        loqusdb_config=None,
        loqusdb_args=None,
        api_url=None,
        version=None,
    ):
        """Initialise from args"""
        self.loqusdb_settings = [
            {
                "id": "default",
                "binary_path": loqusdb_binary,
                "config_path": loqusdb_args,
                "api_url": api_url,
            }
        ]
        LOG.debug(
            "Initializing loqus extension with config: %s",
            self.loqusdb_settings,
        )

    @staticmethod
    def app_config(app):
        """Read config.py to handle single or multiple loqusdb configurations.

           Returns: loqus_db_settings(list
        )"""
        cfg = app.config["LOQUSDB_SETTINGS"]
        if isinstance(cfg, list):
            return cfg
        # backwards compatible, add default id
        cfg["id"] = "default"
        return [cfg]

    def init_app(self, app):
        """Initialize from Flask."""
        LOG.info("Init and check loqusdb connection settings")
        self.loqusdb_settings = self.app_config(app)
        # Check that each Loqus configuration in the settings list is valid
        for setting in self.loqusdb_settings:
            LOG.error(f"Setting--->{setting}")
            # Scout might connect to Loqus via an API or an executable, define which one for every instance
            setting["instance_type"] = "api" if "api_url" in setting else "exec"
            setting["version"] = self.get_instance_version(setting)

    def get_instance_version(self, instance_settings):
        """Returns version of a LoqusDB instance.
        Args:
            instance_settings(dict) : The settings of a specific loqusdb instance

        Returns:
            version (float)
        """
        version = None
        if instance_settings["instance_type"] == "api":
            version = self.get_api_loqus_version(api_url=instance_settings.get(API_URL))
        else:
            version = self.get_exec_loqus_version(loqusdb_id=instance_settings.get("id"))

        if not version >= 2.5:
            LOG.info("Please update your loqusdb version to >=2.5")
            raise EnvironmentError("Only compatible with loqusdb version >= 2.5")
        return version

    @staticmethod
    def get_api_loqus_version(api_url):
        """Get version of LoqusDB instance available from a REST API"""
        if api_url is None:
            return None
        json_resp = api_get("".join([api_url, "/"]))
        return float(json_resp.get("loqusdb_version"))

    @staticmethod
    def get_exec_loqus_version(loqusdb_id=None):
        """Get LoqusDB version as float"""

        call_str = self.get_command(loqusdb_id)
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

    def search_loqus_instance(self, id):
        """Search settings for a LoqusDB instance by id

        Returns:
            {'binary_path':(str), 'id': (str), 'config_path': (str), 'instance_type': 'exec'} or
            {'api_url':(str), 'instance_type':'api', 'id': (str)}
        """
        for i in self.loqusdb_settings:
            if i.get("id") == id:
                return i
        return None

    def case_count(self, variant_category, loqusdb_id="default"):
        """Returns number of cases in loqus instance

        Args:
            loqusdb_id(string)

        Returns:
            nr_cases(int)
        """
        nr_cases = 0
        loqus_instance = self.search_loqus_instance(loqusdb_id)
        if loqus_instance is None:
            LOG.error(f"Could not find a Loqus instance with id:{loqusdb_id}")
            return nr_cases

        # loqus queried via executable
        if loqus_instance.get("instance_type") == "exec":
            case_call = self.get_command(loqusdb_id)
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

        else:  # loqus queried via REST API
            search_url = f"{loqus_instance.get(API_URL)}/cases"
            search_resp = api_get(search_url)
            if search_resp.get("status_code") != 200:
                return 0
            if variant_category == "snv":
                nr_cases = search_resp.get("nr_cases_snvs", 0)
            elif variant_category == "sv":
                nr_cases = search_resp.get("nr_cases_svs", 0)
        return nr_cases

    def get_variant(self, variant_info, loqusdb_id="default"):
        """Return information for a variant (SNV or SV) from loqusdb

        Args:
            variant_info(dict)
            loqusdb_id(string)

        Returns:
            loqus_variant(dict)
        Raises:
            EnvironmentError("Only compatible with loqusdb version >= 2.5")
        """
        loqus_instance = self.search_loqus_instance(loqusdb_id)
        if loqus_instance is None:
            LOG.error(f"Could not find a Loqus instance with id:{loqusdb_id}")
            return

        if loqus_instance.get("instance_type") == "exec":
            return self.get_exec_loqus_variant(loqus_instance, variant_info)

        # Loqus instace is a REST API
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
        search_data = {}
        chrom = variant_info["chrom"]
        end_chrom = variant_info["end_chrom"]
        pos = variant_info["pos"]
        end = variant_info["end"]

        if category == "variants":  # SNVs
            search_url = f"{search_url}/{variant_info['_id']}"
        else:  # SVs
            sv_type = variant_info["variant_type"]
            search_url = f"{search_url}/svs?chrom={chrom}&end_chrom={end_chrom}&pos={pos}&end={end}&sv_type={sv_type}"

        search_resp = api_get(search_url)
        if search_resp.get("status_code") != 200:
            LOG.warning(search_resp.get("detail"))
            return {}
        return search_resp

    @staticmethod
    def get_exec_loqus_variant(loqus_instance, variant_info):
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
                    "--case-count",
                ]
            )
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

    def default_setting(self):
        """Get default loqusdb configuration

        Returns:
            institute_settings(dict)
        """
        return self.search_setting("default")

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
