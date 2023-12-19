# -*- coding: utf-8 -*-
SECRET_KEY = "this is not secret..."
REMEMBER_COOKIE_NAME = "scout_remember_me"  # Prevent session timeout when user closes browser
# SESSION_TIMEOUT_MINUTES = 60  # Minutes of inactivity before session times out

# MONGO_URI = "mongodb://127.0.0.1:27011,127.0.0.1:27012,127.0.0.1:27013/?replicaSet=rs0&readPreference=primary"
MONGO_DBNAME = "scout"

BOOTSTRAP_SERVE_LOCAL = True
TEMPLATES_AUTO_RELOAD = True

DEBUG_TB_INTERCEPT_REDIRECTS = False

# Flask-mail: http://pythonhosted.org/flask-mail/
# see: https://bitbucket.org/danjac/flask-mail/issue/3
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False

# Filename of accrediation bagde image in server/bluprints/public/static
# If null no badge is displayed in scout
ACCREDITATION_BADGE = "swedac-1926-iso17025.png"

# LDAP login Settings
# Complete list of accepted parameters available here: https://github.com/rroemhild/flask-ldapconn
# LDAP_HOST = "localhost" # Can also be named LDAP_SERVER
# LDAP_PORT = 389
# LDAP_BASE_DN = 'cn=admin,dc=example,dc=com # Can also be named LDAP_BINDDN
# LDAP_USER_LOGIN_ATTR = "mail" # Can also be named LDAP_SEARCH_ATTR
# LDAP_USE_SSL = False
# LDAP_USE_TLS = True

# Parameters required for Google Oauth 2.0 login
# GOOGLE = dict(
#    client_id="client.apps.googleusercontent.com",
#    client_secret="secret",
#    discovery_url="https://accounts.google.com/.well-known/openid-configuration",
# )

# Chanjo database connection string - used by chanjo report to create coverage reports
# SQLALCHEMY_DATABASE_URI = "mysql+pymysql://test_user:test_passwordw@127.0.0.1:3306/chanjo"

# Configure gens service
# GENS_HOST = "127.0.0.1"
# GENS_PORT = 5000

# Connection details for communicating with a rerunner service
# RERUNNER_API_ENTRYPOINT = "http://rerunner:5001/v1.0/rerun"
# RERUNNER_TIMEOUT = 10
# RERUNNER_API_KEY = "I am the Keymaster of Gozer"

# Matchmaker connection parameters
# - Tested with PatientMatcher (https://github.com/Clinical-Genomics/patientMatcher) -
# MME_ACCEPTS = "application/vnd.ga4gh.matchmaker.v1.0+json"
# MME_URL = "http://localhost:9020"
# MME_TOKEN = "DEMO"

# Beacon connection settings
# - Tested with cgbeacon2 (https://github.com/Clinical-Genomics/cgbeacon2) -
# BEACON_URL = "http://localhost:6000/apiv1.0"
# BEACON_TOKEN = "DEMO"

# connection details for LoqusDB MongoDB database
# Example with 2 instances of LoqusDB, one using a binary file and one instance connected via REST API
# When multiple instances are available, admin users can modify which one is in use for a given institute from the admin settings page
# LOQUSDB_SETTINGS = {
#    "default" : {"binary_path": "/miniconda3/envs/loqus2.5/bin/loqusdb", "config_path": "/home/user/settings/loqus_default.yaml"},
#    "loqus_api" : {"api_url": "http://127.0.0.1:9000"},
# }

# Connection details for Scout REViewer service
# SCOUT_REVIEWER_URL = "http://127.0.0.1:8000/reviewer"

#
# Cloud IGV tracks can be configured here to allow users to enable them on their IGV views.
# A number of publicly-available tracks can be found here: https://trackhubregistry.org/
# CLOUD_IGV_TRACKS = [
#    {
#        "name": "public_tracks",
#        "access": "public",
#        "tracks": [
#            {
#                "name": "dbVar common SVs (global)",
#                "type": "annotation",
#                "format": "bigbed",
#                "build": "37",
#                "url": "https://ftp.ncbi.nlm.nih.gov/pub/dbVar/sandbox/dbvarhubtest/hg19/common_global.bb",
#            },
#            {
#                "name": "dbVar common SVs (global)",
#                "type": "annotation",
#                "format": "bigbed",
#                "build": "38",
#                "url": "https://ftp.ncbi.nlm.nih.gov/pub/dbVar/sandbox/dbvarhubtest/hg38/common_global.bb",
#            },
#        ],
#    },
# ]

# Chanjo-Report
REPORT_LANGUAGE = "en"
ACCEPT_LANGUAGES = ["en", "sv"]

# FEATURE FLAGS
SHOW_CAUSATIVES = True
SHOW_OBSERVED_VARIANT_ARCHIVE = True
HIDE_ALAMUT_LINK = True

# URL of a general web page where users can place orders for analyses or reruns
RERUN_URL = "https://clinical.scilifelab.se/"
# Display case rerun monitoring toggle
RERUN_MONITOR = True

# OMIM API KEY: Required for downloading definitions from OMIM (https://www.omim.org/api)
# OMIM_API_KEY = 'valid_omim_api_key'

# Parameters for enabling Phenomizer queries
# PHENOMIZER_USERNAME = "test_user"
# PHENOMIZER_PASSWORD = "test_password"

# Parameters for Phenopacket-api backend
PHENOPACKET_API_URL = "https://phenopacket-stage.scilifelab.se"

# Rank model link
RANK_MODEL_LINK_PREFIX = "https://raw.githubusercontent.com/Clinical-Genomics/reference-files/master/rare-disease/rank_model/rank_model_-v"
RANK_MODEL_LINK_POSTFIX = "-.ini"
SV_RANK_MODEL_LINK_PREFIX = "https://raw.githubusercontent.com/Clinical-Genomics/reference-files/master/rare-disease/rank_model/svrank_model_-v"
SV_RANK_MODEL_LINK_POSTFIX = "-.ini"

# BioNano Access Server extension
# BIONANO_ACCESS = "https://bionano-access.scilifelab.se"
# BIONANO_USERNAME = "USERNAME"
# BIONANO_PASSWORD = "PASSWORD"
