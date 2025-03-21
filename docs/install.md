# Install Scout
This guide will walk you through how to setup a working instance of scout by cloning the repository from GitHub and installing it with the `pip install command`. For instructions on how to deploy Scout command line and server using containers check the [Deploy Scout in containers][containers] page
The instructions are divided into multiple sections.
One section describes how to set up a demo version with some cases just to see how it could look like.


## 0. Intro
Make sure you have a `mongod` process running. First install [mongodb][mongodb] and follow the instructions.


## 1. Install
Installation of Scout is possible via PyPi, GitHub or Dockerhub.
Let's start by pulling down the GitHub repository with the source code.

### GitHub

Use `git` to clone from [GitHub](https://github.com/Clinical-Genomics/scout), either the `https` or `ssh` route.
Scout is configured to use `uv`: either run, install, or install as a tool.

```bash
git clone https://github.com/Clinical-Genomics/scout
cd scout

uv sync --frozen
uv run scout
```
Or if you rather, the project definition is compatible with pip, so instead of the `uv` statement above you can just

```
pip install --editable .
```

### Pip

To get the latest development (`main`) version, use the above. When using pip the latest stable release will be installed.

```bash
pip install scout-browser
```


## 2. Configure
In order to make full use of Scout, you will want to integrate with both external resources and a number of available extensions,
e.g. `chanjo` for coverage analysis and `gens` for seamless visualisation and triage of larger CNVs.

You will want to sign up for access to a few web APIs like Google OAuth and
OMIM. The keys and secrets should be added to
the Flask instance config. To learn more about possible settings, take a
look in the ``scout/settings.py`` module.


### Autentication
If you intend to use authentication, which you should, there are several options!

OAuth2 via an ODIC provider (we have good experience with Google) or a KeyCloak server of you own. Scout also supports LDAP.
See the [admin-guide][admin-guide] for details.

#### Google OAuth
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

## 2. Setup

### Demo setup

This option is used to quickly get a operating instance with some example data

```
scout setup demo
scout --demo serve
```
The previous command setup the database with a truncated collection of gene definitions with links to OMIM along with HPO phenotype terms.

### Full setup

For more info, run `scout --help`!

To initialize a working instance - a database where you store genes, diseases, cases, variants etc run

```bash
scout setup database
```
You will want to make sure you have a full complement of these genes, diseases etc before you start working on cases.

```
scout download everything --api-key YOUR_OMIM_API_KEY
scout update hpo --hpoterms hpo.obo --hpo-to-genes phenotype_to_genes.txt
scout update diseases -f .
scout update genes -f .
```

A common task is to have a couple of broad screening panels for rare disease genomics set up. We provide automation for two such in silico panels
out of the box, one with OMIM morbid genes, and one with all PanelApp ``Green`` genes. Here you provide the name of an institute you created that
will serve as responsible for these panels (`cust002` below):
```
scout update omim --institute cust002 --genemap2 genemap2.txt --mim2genes mim2genes.txt
scout update panelapp-green -i cust002 --force
```

For more information about populating and updating the database, please see [admin-guide][admin-guide].

```
scout load panel scout/demo/panel_1.txt
scout load case scout/demo/643594.config.yaml
```



[google-console]: https://console.developers.google.com/project
[omim-register]: http://omim.org/api
[mongodb]: https://docs.mongodb.com/manual/installation/
[admin-guide]: admin-guide/README.md
[containers]: admin-guide/containers/container-deploy.md
