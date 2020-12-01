# Setting up a user login system

Scout currently supports 3 types of login systems:
- [Google authentication via OpenID Connect](##Google-OpenID-Connect-login-system)
- [LDAP authentication](##Login-using-Lightweight-Directory-Access-Protocol-(LDAP)
- [Simple authentication using userid and password](## Simple login with user and password)

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

To enable LDAP authentication, add and customize the following lines in the config file:

```
# LDAP connection settings
LDAP_PORT = ldap-port (usually 389)
LDAP_HOST = 'ldap-host'
LDAP_BASE_DN = 'dc=example,dc=com'
LDAP_BIND_USER_DN = 'cn=read-only-admin,dc=example,dc=com'
LDAP_REQUIRED_GROUP = 'ou=scientists,dc=example,dc=com'
LDAP_USER_SEARCH_SCOPE = 'SUBTREE',
LDAP_GROUP_OBJECT_FILTER = '(objectClass=GroupOfUniqueNames)'
```

- Make sure that all users that should be allowed to log in in the app are already present in the Scout database with an ID corresponding to a valid LDAP.

The following command can be used to add a create a new user into the database:
`scout load user -id ldap_id -i cust000 -u "User Name" -m useremail@email.com`

Please note that the while the `-id ldap_id` option is not a mandatory parameter in the command used for adding users to the database, it is necessary for the LDAP login to successfully recognize the user in the system.


## Simple login with userid and password

Basic login with userid and password is the login system available whenever no advanced login system (either Google or LDAP) is specified in the Scout config file. To enable it, comment out or remove the LDAP and GOOGLE lines mentioned above from your config. It is an un-secure system which is not recommended to use. This is also the login system available in the demo instance of Scout.
