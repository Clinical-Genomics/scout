## Setup Scout

### Demo

Once installed, you can setup Scout by running a few commands using the included command line interface. Given you have a MongoDB server listening on the default port (27017), this is how you would setup a fully working Scout demo:

```bash
scout setup demo
```

This will setup an instance of scout with a database called `scout-demo`. Now run

```bash
scout --demo serve
```
And play around with the interface. A user has been created with email clark.kent@mail.com so use that adress to get access

### Initialize scout

To initialize a working instance with all genes, diseases etc run

```bash
scout setup database
```

for more info, run `scout --help`


### Setting up users login

Scout login system currently supports
1. Google login via OpenID Connect. Click [here](./login-system.md/#google-openid-connect-login-system) for instructions on how to set up a Google login system
1. Connection via Lightweight Directory Access Protocol (LDAP). Click [here](./login-system.md/##Login-using-Lightweight-Directory-Access-Protocol-(LDAP) for instructions on how to set up a LDAP login system.
1. [Simple login](./login-system.md/#simple-login-with-userid) - for operation tests or a trusted local environment only. Fallback - will operate if no other auth configuration is specified.
