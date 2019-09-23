# Install Scout
This guide will walk you through how to setup a working instance of scout.
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
You have to use python 3 for scout: on some systems (i.e. CentOS 7.6) you can have pip3.6 and python3.6 
(or other versions) installed by the distribution package managers. Alternatively, you can use 
[conda](http://conda.io) to get the right version for your tool.


```bash
pip install scout-browser
```

## 2. Setup

### Full setup

For full setup you have to have the proper (i.e. scout.myUserName) user added to your
mongo DB. See db.createUser() in the mongo CLI documentation if you have login problems, and check the flas.conf.py file below.

Furthermore, you must have your OMIM API key (that can take weeks to get). To initialize a working instance with all genes, diseases etc run

```bash
scout setup database --api-key xXxXxXxXxXxXx
```

for more info, run `scout --help`

> If you intent to use authentication, make sure you are using a Google email!

To test scout you have to add and institute and a user (and you may consider update roles) :

```
scout load institute --internal-id myInstitute
scout load user --institute-id myInstitute --user-name "Joe Bloggs" --user-mail joe.bloggs@bugger.com

```

The previous command setup the database with a curated collection of gene definitions with links to OMIM along with HPO phenotype terms. Now we will load some example data. Scout expects the analysis to be accomplished using various gene panels so let\'s load one and then our first analysis case:

```
scout load panel scout/demo/panel_1.txt
scout load case scout/demo/643594.config.yaml
```

scout load panel --panel-id cancer_test --institute BTB --omim --api-key XtviywdmR0WnbrFskEar5A cancer_panel.tx



For more information about populating the database, please see [admin-guide][admin-guide].

### Demo

This option is used to quickly get a operating instance with some example data

```
scout setup demo
scout --demo serve


```

Test config.yaml:



[google-console]: https://console.developers.google.com/project
[omim-register]: http://omim.org/api
[vagrant]: https://www.vagrantup.com/
[mongodb]: https://docs.mongodb.com/manual/installation/
[admin-guide]: admin-guide/README.md
