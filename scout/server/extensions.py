# -*- coding: utf-8 -*-
import logging
import copy
import subprocess
import json

from subprocess import CalledProcessError

from pymongo.errors import (ConnectionFailure)

from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension()

from flask_bootstrap import Bootstrap
bootstrap = Bootstrap()

from scout.adapter import MongoAdapter
store = MongoAdapter()

from flask_login import LoginManager
from flask_ldap3_login import LDAP3LoginManager
from flask_oauthlib.client import OAuth

login_manager = LoginManager()
ldap_manager = LDAP3LoginManager()

oauth = OAuth()
# use Google as remote application
# you must configure 3 values from Google APIs console
# https://code.google.com/apis/console
google = oauth.remote_app('google', app_key='GOOGLE')

from flask_mail import Mail
mail = Mail()

from scout.adapter.client import get_connection

LOG = logging.getLogger(__name__)

def execute_command(cmd):
    """
        Prints stdout + stderr of command in real-time while being executed

    Args:
        cmd (list): command sequence

    Yields:
        line (str): line of output from command
    """
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               bufsize=1)

    for line in process.stdout:
        yield line.decode('utf-8').strip()

    def process_failed(process):
        """See if process failed by checking returncode"""
        return process.poll() != 0

    if process_failed(process):
        raise CalledProcessError(returncode=process.returncode, cmd=cmd)

class LoqusDB():
    def init_app(self, app):
        """Initialize from Flask."""
        LOG.info("Connecting to loqusdb")
        self.loqusdb_binary = app.config['LOQUSDB_SETTINGS'].get('binary', 'loqusdb')
        self.loqusdb_config = app.config['LOQUSDB_SETTINGS'].get('config_path')
        
        self.base_call = [self.loqusdb_binary]
        if self.loqusdb_config:
            self.base_call.extend(['--config', self.loqusdb_config])
        return

    def _fetch_variant(self, variant_info):
        """Query loqusdb for variant information
        
        Args:
            variant_info(dict): The variant id in loqusdb format
        
        Returns:
            res
        """
        loqus_id = variant_info['_id']
        res = {}
        variant_call = copy.deepcopy(self.base_call)
        variant_call.extend([
            'variants', '--to-json', '--case-count',
            '--variant-id', loqus_id])
        # If sv we need some more info
        if variant_info.get('category', 'snv') in ['sv']:
            variant_call.extend([
                '-t', 'sv', '-c', variant_info['chrom'], '-s', str(variant_info['pos']),
                '-e' , str(variant_info['end']), '--end-chromosome', variant_info['end_chrom'],
                '--sv-type', variant_info['variant_type']
            ])
        output = ''
        try:
            output = subprocess.check_output(
                ' '.join(variant_call),
                shell=True
            )
        except CalledProcessError as err:
            LOG.warning("Something went wrong with loqus")
            return

        if not output:
            LOG.info("Could not find information about variant %s", loqus_id)
            return res

        output = output.decode('utf-8')


        res = json.loads(output)

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

    def _case_count(self):
        """Return number of cases that the observation is based on
        
        Returns:
            nr_cases(int)
        """
        nr_cases = 0
        case_call = copy.deepcopy(self.base_call)
        
        case_call.extend(['cases', '--count'])
        output = ''
        try:
            output = subprocess.check_output(
                ' '.join(case_call),
                shell=True
            )
        except CalledProcessError as err:
            LOG.warning("Something went wrong with loqus")
            return
        
        if not output:
            LOG.info("Could not find information about loqusdb cases")
            return nr_cases

        output = output.decode('utf-8')

        try:
            nr_cases = int(output.strip())
        except Exception:
            pass
        
        return nr_cases
    
    def test_loqus(self):
        """Test if loqus seems to work"""
        version_call = copy.deepcopy(self.base_call)
        version_call.extend(['--version'])
    
    def __repr__(self):
        return (f"LoqusDB(binary={self.loqusdb_binary},"
                f"config={self.loqusdb_config})")

class MongoDB(object):

    def init_app(self, app):
        """Initialize from flask"""
        uri = app.config.get("MONGO_URI", None)

        db_name = app.config.get("MONGO_DBNAME", 'scout')

        try:
            client = get_connection(
                host = app.config.get("MONGO_HOST", 'localhost'),
                port=app.config.get("MONGO_PORT", 27017),
                username=app.config.get("MONGO_USERNAME", None),
                password=app.config.get("MONGO_PASSWORD", None),
                uri=uri,
                mongodb= db_name
            )
        except ConnectionFailure:
            context.abort()

        app.config["MONGO_DATABASE"] = client[db_name]
        app.config['MONGO_CLIENT'] = client



loqusdb = LoqusDB()
mongo = MongoDB()
