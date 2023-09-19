# Install Scout
This guide will walk you through how to setup a working instance of scout by cloning the repository from GitHub and installing it with the `pip install command`. For instructions on how to deploy Scout command line and server using containers check the [Deploy Scout in containers][containers] page
The instructions are divided into multiple sections.
One section describes how to set up a demo version with some cases just to see how it could look like.


## 0. Intro
Make sure you have a `mongod` process running. First install [mongodb][mongodb] and follow the instructions.


## 1. Install
Installation of Scout is possible via pip or GitHub.
Let's start by pulling down the GitHub repository with the source code.

### GitHub


```bash
git clone https://github.com/Clinical-Genomics/scout
cd scout
pip install --requirement requirements.txt --editable .
```

### Pip

To get the latest version, use the above. When using pip the latest stable release will be installed.

```bash
pip install scout-browser
```


<!-- ## 2. Configure
You need to sign up for access to a few web APIs like Google OAuth and
OMIM to make full use of Scout. The keys and secrets should be added to
the Flask instance config. To learn more about possible settings, take a
look in the ``scout/settings.py`` module.

### Google OAuth
Create a new project in your [Google Developer console][google-console].
Under your project, click "APIs & auth" > "Credentials". Here you will
find your "CLIENT ID" and "CLIENT SECRET". You also need to add some
"REDIRECT URLS" and "JAVASCRIPT ORIGINS".

**REDIRECT URLS**:

  - http://localhost:5023/authorized
  - https://localhost:5023/authorized

**JAVASCRIPT ORIGINS**:

  - http://localhost:5023
  - https://localhost:5023

Remember that it might take a while for the tokens to start working.

### OMIM API
You can [register][omim-register] for free OMIM API access. You will be
sent the authentication token eventually :)

### Gmail
The Sanger email feature requires credentials for a Gmail account. Any
account should work so you don't need to sign up for any special access.

### MongoDB
If you are using a password protected Mongo database you also need to add
the authentication details to the instance config.


## 3. Boostrap
We use gulp.js to compile the statis assets (CSS, JS, etc.)

```bash
$ gulp build --production
```


## 4. Develop
You are now ready to start the development server and complete the setup
in the admin interface.

```bash
$ python manage.py -c "$(pwd)/configs/boilerplate.cfg" vagrant
```

That's it! Go and explore Scout. -->

## 2. Setup

### Full setup

To initialize a working instance with all genes, diseases etc run

```bash
scout setup database
```

for more info, run `scout --help`

> If you intent to use authentication, make sure you are using a Google email!

The previous command setup the database with a curated collection of gene definitions with links to OMIM along with HPO phenotype terms. Now we will load some example data. Scout expects the analysis to be accomplished using various gene panels so let's load one and then our first analysis case:

```
scout load panel scout/demo/panel_1.txt
scout load case scout/demo/643594.config.yaml
```


For more information about populating the database, please see [admin-guide][admin-guide].

### Demo

This option is used to quickly get a operating instance with some example data

```
scout setup demo
scout --demo serve
```


[google-console]: https://console.developers.google.com/project
[omim-register]: http://omim.org/api
[vagrant]: https://www.vagrantup.com/
[mongodb]: https://docs.mongodb.com/manual/installation/
[admin-guide]: admin-guide/README.md
[containers]: admin-guide/containers/container-deploy.md
