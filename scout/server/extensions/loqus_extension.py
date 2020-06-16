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
    print("cmd")
    print(cmd)
    message = " ".join(cmd)
    LOG.info("Running: %s", message)
    try:
        output = subprocess.check_output(cmd, shell=False)
    except CalledProcessError as err:
        LOG.warning("Something went wrong with loqusdb")
        raise err

    return output.decode("utf-8")



class LoqusDB:
    """Interface to loqusdb from Scout

    Implemented as singleton"""

    __instance = None

    def __new__(cls, loqusdb_binary=None):
        if cls.__instance is None:
            print('Creating the object')
        cls.__instance = super(LoqusDB, cls).__new__(cls)
        # Put any initialization here.
        return cls.__instance


    def __init__(self, loqusdb_binary=None, loqusdb_args=None):
        """Initialise from args"""
        self.loqusdb_config = {'id':"init", 'binary_path': loqusdb_binary, 'args':loqusdb_args}
        self.version = self.get_version()

        LOG.info(
            "Initializing loqus extension with binary: %s, version: %d",
            self.get_bin_path(),
            self.version,
        )


    def init_app(self, app):
        """Initialize from Flask."""
        LOG.info("Connecting to loqusdb")
        self.loqus_config = app.config["LOQUSDB_SETTINGS"]
        LOG.info("Use loqusdb config file %s", self.loqusdb_config)
        self.version = self.get_version()
        self.version_check()    # why is version check done? here and not in __init__ + what if it fails?


    def version_check(self):
        """Check if a compatible version is used otherwise raise an error"""
        if not self.version >= 2.5:
            LOG.info("Please update your loqusdb version to >=2.5 (current: {})").format(self.version)
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


    def get_variant(self, variant_info, institute=None):
        """Return information for a variant from loqusdb

        SNV/INDELS can be queried in loqus by defining a simple id. For SVs we need to call them
        with coordinates.

        Args:=
            variant_info(dict)

        Returns:
            loqus_variant(dict)
        """
        loqus_id = variant_info["_id"]
        variant_call = get_bin_path(institute)
        variant_call = add_args(variant_call)
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


    def get_bin_path(self, institute=None):
        """Return path to `loqusdb` binary as a list, as configured per institute or default"""
        if institute:
            institute_config=next((item for item in dicts if item["id"] == insitute), None)
            return [institute_config['binary_path']]
        else:
            return [self.loqusdb_config['binary_path']]


    def get_args(self, loqus_id, institute=None):
        if institute:
            loqus_setting=next((item for item in dicts if item["id"] == insitute), None)
            return loqus_setting['args']
        else:
#            self.base_call.extend(["--config", self.loqusdb_config])
            self.setting['args']



    def add_args(bin_path):
        """Add configured arguments to bin string creating a string
        usable for calling loqusdb via shell invokation"""
        return bin_path.extend(["--config", self.args])



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
        call_str = self.get_bin_path()
        call_str.extend(["--version"])
        print("***")
        print(call_str)
        try:
            output = execute_command(call_str)
        except CalledProcessError:
            LOG.warning("Something went wrong with loqus")
            return -1.0

        version = output.rstrip().split(" ")[-1]
        return float(version)


    def __repr__(self):
        return f"LoqusDB(loqusdb_config={self.loqusdb_config}," 
