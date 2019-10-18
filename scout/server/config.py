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

# Chanjo-Report
REPORT_LANGUAGE = 'en'
ACCEPT_LANGUAGES = ['en', 'sv']

# FEATURE FLAGS
SHOW_CAUSATIVES = True

# OMIM API KEY: Required for downloading definitions from OMIM (https://www.omim.org/api)
#OMIM_API_KEY = 'valid_omim_api_key'

LDAP = dict(
    # LDAP connection settings
    LDAP_PORT = 389,
    # Hostname of your LDAP Server
    LDAP_HOST = 'documize-ad.eastus.cloudapp.azure.com',
    # Base DN of your directory
    LDAP_BASE_DN = 'DC=mycompany,DC=local',
    # The RDN attribute for your user schema on LDAP
    #LDAP_USER_RDN_ATTR = 'cn',
    # The Attribute you want users to authenticate to LDAP with.
    #LDAP_USER_LOGIN_ATTR = 'accountName',
    # The Username to bind to LDAP with
    LDAP_BIND_USER_DN = 'CN=Mr Manager,CN=Users,DC=mycompany,DC=local',
    # The Password to bind to LDAP with
    LDAP_BIND_USER_PASSWORD = 'Pass@word1!',
    # Required group user has to belong to (dirty hack)
    #LDAP_REQUIRED_GROUP = 'CN=fakey_cn,OU=Genetik,OU=System,OU=Grupper,OU=VLL,DC=vll,DC=se',
    # Has to be there
    #LDAP_USER_SEARCH_SCOPE = 'SUBTREE',
    #LDAP_GROUP_OBJECT_FILTER = '(objectclass=groupOfNames)',
)
