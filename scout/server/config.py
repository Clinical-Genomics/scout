# -*- coding: utf-8 -*-
SECRET_KEY = 'this is not secret...'
REMEMBER_COOKIE_NAME = 'scout_remember_me'

MONGO_DBNAME = 'scout'

BOOTSTRAP_SERVE_LOCAL = True
TEMPLATES_AUTO_RELOAD = True

DEBUG_TB_INTERCEPT_REDIRECTS = False

# Flask-mail: http://pythonhosted.org/flask-mail/
# see: https://bitbucket.org/danjac/flask-mail/issue/3
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False

# connection details for LoqusDB MongoDB database
# LOQUSDB_SETTINGS = dict(
#     binary='/path/to/bin/loqusdb',
#     config_path=<path/to/loqus/config>
#
# )
# If not on localhost 27017 one needs to provide uri with
# connection details for LoqusDB MongoDB database
#    uri=("mongodb://{}:{}@localhost:{}/loqusdb".format(MONGO_USERNAME, MONGO_PASSWORD, MONGO_PORT))


# Chanjo-Report
REPORT_LANGUAGE = 'en'
ACCEPT_LANGUAGES = ['en', 'sv']

# FEATURE FLAGS
SHOW_CAUSATIVES = True

# OMIM API KEY: Required for downloading definitions from OMIM (https://www.omim.org/api)
#OMIM_API_KEY = 'valid_omim_api_key'

# Rank model links

RANK_MODEL_LINK_PREFIX = "https://github.com/Clinical-Genomics/reference-files/blob/master/rare-disease/rank_model/rank_model_-v"
RANK_MODEL_LINK_POSTFIX = "-.ini"
SV_RANK_MODEL_LINK_PREFIX = "https://github.com/Clinical-Genomics/reference-files/blob/master/rare-disease/rank_model/svrank_model_-v"
SV_RANK_MODEL_LINK_POSTFIX = "-.ini"
