# Setting up a user login system

Scout currently supports 4 types of login systems:
  - [keycloak authentication via OpenID Connect](#keycloak-openid-connect-login-system)
  - [Google authentication via OpenID Connect](#google-openid-connect-login-system)
  - [LDAP authentication](#login-using-lightweight-directory-access-protocol)
  - [Simple authentication using userid](#simple-login-with-userid)

**Login systems are mutually exclusive so when you choose a system, it will become be the only way all users will have access to the Scout app.**


## Keycloak OpenID Connect Login System

If your organization uses Keycloak as a login provider, Scout can be configured to authenticate users (who are already registered in the Scout database) using Keycloak in a few simple steps.

A small tutorial with basic settings (intended for testing only, not for production) is available [on this page](https://github.com/northwestwitch/keycloak_flask_auth?tab=readme-ov-file#keycloak_flask_auth).

Assuming a Keycloak realm containing users is available, you can edit the Scout configuration file to enable this authentication method:

```python
KEYCLOAK = dict(
    client_id="<name_of_client>",
    client_secret="secret", # available on Keycloak's admin console, under client credentials
    discovery_url="http://<url_to_keycloak_instance>/realms/<name_of_realm>/.well-known/openid-configuration",
    logout_url="http://<url_to_keycloak_instance>/realms/<name_of_realm>/protocol/openid-connect/logout",
)
```

**Please note**: For this setup to work, the Keycloak client must include the following parameter:

`Valid redirect URIs: "http://<scout-uri>/authorized"`


Users attempting to log in to Scout will be redirected to the Keycloak instance for authentication.

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


## Login using Lightweight Directory Access Protocol

Institutional directory services authentication via LDAP is supported by Scout.

LDAP authentication in Scout is achieved by using the [flask-ldapconn](https://github.com/rroemhild/flask-ldapconn) library.

Pre-requisites in order to authenticate users using LDAP:

- **An existing LDAP authentication server (external from Scout)**
- **All users that should be logged in Scout using the LDAP should be previously saved into the scout database with an ID corresponding to a valid LDAP user.**

The following command can be used to add a create a new user into the database:
`scout load user -id ldap_id (could be an email address) -i cust000 -u "User Name" -m useremail@email.com`

Please **note that the while the `-id ldap_id` option is not a mandatory parameter in the command used for adding users to the database, it is necessary for the LDAP login to successfully recognize the user in the system**.

LDAP server instances are different from case to case. Some basic LDAP config options (with example values) that can be used on the in the Scout config file are the following:

```
# LDAP_HOST = "localhost" # Can also be named LDAP_SERVER
# LDAP_PORT = 389
# LDAP_BASE_DN = 'cn=admin,dc=example,dc=com # Can also be named LDAP_BINDDN
# LDAP_USER_LOGIN_ATTR = "mail" # Can also be named LDAP_SEARCH_ATTR
# LDAP_USE_SSL = False
# LDAP_USE_TLS = True
```

A complete list of accepted parameters that can be used to reflect your LDAP server configuration is available in the [flask-ldapconn readme page](https://github.com/rroemhild/flask-ldapconn).

### Considerations regarding the LDAP login in Scout.

Since Scout software needs to define internal user objects for functioning properly, the LDAP login check against the server is only the first step of the login process. The second step would be making sure that a user authenticated by a certain password exists also in the `user` collection of the Scout database. Because of this latter authentication step, it is not strictly necessary to define a stringent set of rules (for instance which groups the user must belong to) for the LDAP login system, because a user from any group will be logged into Scout, as long as it's previously saved in the Scout database.

This entails that if a user should be removed from the system, it is enough just to remove it from the Scout database.

### Example of LDAP login setup using Docker

In order to understand how the LDAP authentication works, we are providing a docker-based example of a setup with a demo LDAP server containing pre-defined users. The LDAP auth server used here is based on the test server [docker-test-openldap](https://github.com/rroemhild/docker-test-openldap), that contains a number of pre-defined users and organizational user roles from the [Futurama Wiki](https://futurama.fandom.com/wiki/Futurama_Wiki) that are also described in the main page of the repository.

1) You could start the data-populated LDAP server running the Docker command:
```
docker run --rm -p 10389:10389 -p 10636:10636 rroemhild/test-openldap
```

2) From the LDAP server, let's choose one character from Futurama that we would like to add as a user in a local instance of Scout, for instance [Dr. Zoidberg](https://github.com/rroemhild/docker-test-openldap#cnjohn-a-zoidbergoupeopledcplanetexpressdccom)

![Dr. Zoidberg](https://static.wikia.nocookie.net/characterprofile/images/1/17/Zoidberg.png/revision/latest/scale-to-width-down/250?cb=20180603192711)

Let's start adding the user to Scout with the command:
```
scout --demo load user -i cust000 -u "Dr. Zoidberg" -m zoidberg@planetexpress.com -id zoidberg@planetexpress.com
```
Note that the created ID is an email address that is defined for the user in the demo LDAP server: https://github.com/rroemhild/docker-test-openldap#cnjohn-a-zoidbergoupeopledcplanetexpressdccom. Note also that the password for this user is `zoidberg`.

3) Finally, let's modify the Scout demo config file by adding the following lines:
```
LDAP_HOST = "localhost"
LDAP_PORT = 10389
LDAP_BASE_DN = "dc=planetexpress,dc=com"
LDAP_USER_LOGIN_ATTR = "mail"
LDAP_USE_SSL = False
LDAP_USE_TLS = True
```
Let's start the demo server with the command `scout --demo serve`.

4) It should be now possible to login the new user into Scout using email and password defined in the LDAP server!

## Simple login with userid

Basic login with userid and password is the login system available whenever no advanced login system (either Google or LDAP) is specified in the Scout config file. To enable it, comment out or remove the LDAP and GOOGLE lines mentioned above from your config. It is an un-secure system which is not recommended to use. This is also the login system available in the demo instance of Scout.
