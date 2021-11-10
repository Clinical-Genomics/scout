# Setting up a user login system

Scout currently supports 3 types of login systems:
  - [Google authentication via OpenID Connect](##Google-OpenID-Connect-login-system)
  - [LDAP authentication](##Login-using-Lightweight-Directory-Access-Protocol-(LDAP)
  - [Simple authentication using userid](#simple-login-with-userid)

**Login systems are mutually exclusive so when you choose a system, it will become be the only way all users will have access to the Scout app.**


## Google OpenID Connect login system

Scout supports Google account login via OpenID Connect. Before setting up the Google authentication system in Scout it is necessary to register the Scout application in the Google API console and obtain OAuth 2.0 credentials. A detailed guide on how to do this is available [at this link](https://developers.google.com/identity/protocols/oauth2/openid-connect).

In brief:

### Create credentials for your demo app:

-  Go to this page:  https://console.developers.google.com/apis/credentials?project=my-project-1507807614573&folder=&organizationId=

- Click on `credentials` and choose the second option: `OAuth Client ID`
![image](https://user-images.githubusercontent.com/28093618/84499985-ef2c4200-acb3-11ea-8ade-1789219bfd73.png)

- Fill in this page with the following info:
 name: A name for your app
 Authorized JavaScript origins: **https://your-scout-implementation-url:port**
 Authorized redirect URIs: **http://your-scout-implementation-url:port/authorized**

- Save these settings by clicking on the "Save" button

- Note that a **client_id** and a **client_secret** are generated.

### Edit the scout config file adding the following lines:
```
GOOGLE = dict(
    client_id="client_id",
    client_secret="client_secret",
    discovery_url="https://accounts.google.com/.well-known/openid-configuration"
)
```

- Make sure that all users that should be allowed to log in in the app are already present in the Scout database with an id corresponding to a valid google email address.

The following command can be used to add a create a new user into the database:
`scout load user -i institute-id -u "User Name" -m user_emaill@email.com`


## Login using Lightweight Directory Access Protocol (LDAP)

Institutional directory services authentication via LDAP is supported by Scout.

LDAP authentication in Scout is acheved by using the [lask-ldap3-login](https://flask-ldap3-login.readthedocs.io/en/latest/) library.

Pre-requisites in order to authenticate users using LDAP:

- **An existing LDAP authentication server (external from Scout)**
- **All users that should be logged in Scout using the LDAP should be also saved in the scout database.**

LDAP server instances are different from case to case. Some basic config files to be provided in the Scout config file are the following:

```
# LDAP login Settings
# LDAP_HOST = 'ad.mydomain.com'
# LDAP_PORT = 389
# LDAP_BASE_DN = 'dc=mydomain,dc=com'
# LDAP_USER_DN = 'ou=users'
# LDAP_USER_LOGIN_ATTR = "mail"
```
A complete list of accepted parameters is available here in the  https://flask-ldap3-login.readthedocs.io/en/latest/configuration.html#core)

- Make sure that all users that should be allowed to log in in the app are already present in the Scout database with an ID corresponding to a valid LDAP user.

The following command can be used to add a create a new user into the database:
`scout load user -id ldap_id (could be an email address) -i cust000 -u "User Name" -m useremail@email.com`

Please note that the while the `-id ldap_id` option is not a mandatory parameter in the command used for adding users to the database, it is necessary for the LDAP login to successfully recognize the user in the system.

An docker-compose file containing an example of a scout instance with a simple LDAP authentication system can be used for testing this type of login.

The LDAP server used in the following example is based on the test server [docker-test-openldap](https://github.com/rroemhild/docker-test-openldap). This test contains data from the [Futurama Wiki](https://futurama.fandom.com/wiki/Futurama_Wiki).

In order to run this example:
- Save the following line in a file named `docker-compose-LDAP.yml` (this file should be saved under the main scout folder, at the same level of the Dockefile).

- Add the following line to the Scout config file (scout/server/config.py):
```
# LDAP_HOST = "openldap"
# LDAP_PORT = 10389
# LDAP_BASE_DN = "dc=planetexpress,dc=com"
# LDAP_USER_DN = "ou=people"
# LDAP_USER_LOGIN_ATTR = "mail"
```
- Run the containers with the command
```
docker-compose -f docker-compose-LDAP.yml up
```
- Log in in scout as Leela Turanga, using the same email and password specified in the [documentation](https://github.com/rroemhild/docker-test-openldap#cnturanga-leelaoupeopledcplanetexpressdccom)  (Username=leela@planetexpress.com,
Password=leela)

``` yaml
version: '3'

services:

  mongodb:
    image: mongo:4.4.9
    container_name: mongodb
    networks:
      - scout-net
    ports:
      - '27013:27017'
    expose:
      - '27017'

  openldap:
    image: rroemhild/test-openldap # https://github.com/rroemhild/docker-test-openldap
    ports:
      - '10389:10389'
      - '10636:10636'
    networks:
      - scout-net

  scout-web:
    build: .
    container_name: scout-web
    expose:
      - '5000'
    ports:
      - '5000:5000'
    command: bash -c '
      scout --host mongodb setup demo
      && scout --host mongodb --demo load user -i cust000 -u "Leela Turanga" -m leela@planetexpress.com -id leela@planetexpress.com
      && scout --host mongodb --demo serve --host 0.0.0.0'
    volumes:
      - ./scout:/home/worker/app/scout
      - ./volumes/scout/data:/home/worker/data
    depends_on:
      - mongodb
      - openldap
    networks:
      - scout-net

networks:
  scout-net:
    driver: bridge
```


## Simple login with userid

Basic login with userid and password is the login system available whenever no advanced login system (either Google or LDAP) is specified in the Scout config file. To enable it, comment out or remove the LDAP and GOOGLE lines mentioned above from your config. It is an un-secure system which is not recommended to use. This is also the login system available in the demo instance of Scout.
