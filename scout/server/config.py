# -*- coding: utf-8 -*-
SECRET_KEY = 'this is not secret...'
REMEMBER_COOKIE_NAME = 'scout_remember_me'

MONGO_DBNAME = 'scoutTest'

BOOTSTRAP_SERVE_LOCAL = True
TEMPLATES_AUTO_RELOAD = True

DEBUG_TB_INTERCEPT_REDIRECTS = False

# Flask-mail: http://pythonhosted.org/flask-mail/
# see: https://bitbucket.org/danjac/flask-mail/issue/3
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False

MAIL_USERNAME = 'dummyscoutuser@gmail.com'
MAIL_PASSWORD = 'scoutPWD01'
ADMINS = [
    'dummyscoutuser@gmail.com',
]

# Chanjo-Report
REPORT_LANGUAGE = 'en'
ACCEPT_LANGUAGES = ['en', 'sv']

# FEATURE FLAGS
SHOW_CAUSATIVES = True

# OMIM API KEY: Required for downloading definitions from OMIM (https://www.omim.org/api)
#OMIM_API_KEY = 'valid_omim_api_key'
