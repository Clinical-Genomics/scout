# -*- coding: utf-8 -*-
import copy
import json
import logging
import subprocess
from subprocess import CalledProcessError

from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask_ldap3_login import LDAP3LoginManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_oauthlib.client import OAuth
from pymongo.errors import ConnectionFailure

from scout.adapter import MongoAdapter
from scout.adapter.client import get_connection

toolbar = DebugToolbarExtension()


bootstrap = Bootstrap()


store = MongoAdapter()


login_manager = LoginManager()
ldap_manager = LDAP3LoginManager()

oauth = OAuth()
# use Google as remote application
# you must configure 3 values from Google APIs console
# https://code.google.com/apis/console
google = oauth.remote_app("google", app_key="GOOGLE")


mail = Mail()


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
    LOG.info("Running: %s" % " ".join(cmd))
    try:
        output = subprocess.check_output(cmd, shell=False)
    except CalledProcessError as err:
        LOG.warning("Something went wrong with loqusdb")
        raise err

    if not output:
        return output

    output = output.decode("utf-8")
    return output


class LoqusDB:
    def __init__(self, loqusdb_binary=None, loqusdb_config=None, version=None):
        """Initialise from args"""
        self.loqusdb_binary = loqusdb_binary
        self.loqusdb_config = loqusdb_config
        self.version = version or 0.0
        LOG.info(
            "Initializing loqus extension with binary: {}, version: {}".format(
                self.loqusdb_binary, self.version
            )
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
        if self.loqusdb_config:
            LOG.info("Use loqusdb config file %s", self.loqusdb_config)

        self.base_call = [self.loqusdb_binary]
        if self.loqusdb_config:
            self.base_call.extend(["--config", self.loqusdb_config])

        self.version = self._version()
        return

    def _fetch_variant(self, variant_info):
        """Query loqusdb for variant information

        Args:
            variant_info(dict): The variant id in loqusdb format

        Returns:
            res
        """
        loqus_id = variant_info["_id"]
        res = {}
        variant_call = copy.deepcopy(self.base_call)
        variant_call.extend(["variants", "--to-json", "--variant-id", loqus_id])
        # If sv we need some more info
        if variant_info.get("category", "snv") in ["sv"]:
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
            return

        if not output:
            return res

        res = json.loads(output)

        if self.version < 2.5:
            res["total"] = self._case_count()

        return res

    def get_variant(self, variant_info):
        """Return information for a variant from loqusdb


        Args:
            variant_info(dict)

        Returns:
            loqus_variant(dict)
        """
        loqus_variant = self._fetch_variant(variant_info)

        return loqus_variant

    def case_count(self):
        """Returns number of cases in loqus instance

        Returns:
            nr_cases(int)
        """
        return self._case_count()

    def _case_count(self):
        """Return number of cases that the observation is based on

        Returns:
            nr_cases(int)
        """
        nr_cases = 0
        case_call = copy.deepcopy(self.base_call)

        case_call.extend(["cases", "--count"])
        output = ""
        try:
            output = execute_command(case_call)
        except CalledProcessError as err:
            LOG.warning("Something went wrong with loqus")
            return

        if not output:
            LOG.info("Could not find information about loqusdb cases")
            return nr_cases

        try:
            nr_cases = int(output.strip())
        except Exception:
            pass

        return nr_cases

    def _version(self):
        """Test if loqus version"""
        version_call = copy.deepcopy(self.base_call)
        version_call.extend(["--version"])
        loqus_version = 0.0

        try:
            output = execute_command(version_call)
        except CalledProcessError as err:
            LOG.warning("Something went wrong with loqus")
            return
        version = output.rstrip().split(" ")[-1]
        if version:
            return float(version)
        return loqus_version

    def __repr__(self):
        return f"LoqusDB(binary={self.loqusdb_binary}," f"config={self.loqusdb_config})"


class MongoDB(object):
    def init_app(self, app):
        """Initialize from flask"""
        uri = app.config.get("MONGO_URI", None)

        db_name = app.config.get("MONGO_DBNAME", "scout")

        try:
            client = get_connection(
                host=app.config.get("MONGO_HOST", "localhost"),
                port=app.config.get("MONGO_PORT", 27017),
                username=app.config.get("MONGO_USERNAME", None),
                password=app.config.get("MONGO_PASSWORD", None),
                uri=uri,
                mongodb=db_name,
            )
        except ConnectionFailure:
            context.abort()

        app.config["MONGO_DATABASE"] = client[db_name]
        app.config["MONGO_CLIENT"] = client


loqusdb = LoqusDB()
mongo = MongoDB()
