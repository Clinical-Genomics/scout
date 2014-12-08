# Install Scout
This guide will walk you through bootstrapping a development environment. The instructions are divided into multiple sections.


## 0. Intro
Scout mainly consists of 3 moving parts that each must be installed separately. Runtime requirements include Python and MongoDB. Development and asset compilation requires Node.js.


## 1. Install
Let's start by pulling down the GitHub repository with the source code.

```bash
$ git clone https://github.com/Clinical-Genomics/scout
$ cd scout
```

The Scout repo contains a Bash script with full installation instructions for Ubuntu. I will from this point on assume that you have [Vagrant][vagrant] installed on you local development machine. If you plan to setup the project in any other way you should take a closer look at the *Vagrantfile* and the *provision.sh* script.

```bash
$ vagrant up
$ vagrant ssh
$ cd /vagrant
```


## 2. Configure
You need to sign up for access to a few web APIs like Google OAuth and OMIM to make full use of Scout. The keys and secrets should be added to the Flask instance config. To learn more about possible settings, take a look in the ``scout/settings.py`` module.

### Google OAuth
Create a new project in your [Google Developer console][google-console]. Under your project, click "APIs & auth" > "Credentials". Here you will find your "CLIENT ID" and "CLIENT SECRET". You also need to add some "REDIRECT URLS" and "JAVASCRIPT ORIGINS".

**REDIRECT URLS**:

  - http://localhost:5000/authorized
  - https://localhost:5000/authorized

**JAVASCRIPT ORIGINS**:

  - http://localhost:5000
  - https://localhost:5000

Remember that it might take a while for the tokens to start working.

### OMIM API
You can [register][omim-register] for free OMIM API access. You will be sent the authentication token eventually :)

### Gmail
The Sanger email feature requires credentials for a Gmail account. Any account should work so you don't need to sign up for any special access.

### MongoDB
If you are using a password protected Mongo database you also need to add the authentication details to the instance config.


## 3. Boostrap
We use gulp.js to compile the statis assets (CSS, JS, etc.)

```bash
$ gulp build
```

The included [invoke][invoke] tasks can help you to populate the database with some demo data. It's important that you use the correct email address when adding a user to the database.

```bash
# load variants, cases, and a default institute
$ inv init-data
# add user
$ inv add-user --email="your.name@example.com" --name="Your Name"
```


## 4. Develop
You are now ready to start the development server and complete the setup in the admin interface.

```bash
$ python manage.py -c "$(pwd)/configs/boilerplate.cfg" vagrant
```

The user you created with ``inv add-user`` has admin rights. You can access the admin interface by visiting ``/admin``.

```bash
$ open http://localhost:5000/admin
```

Go to the tab "Institute" and add a few "Cases" before pressing "Submit". Exit the admin interface and you will now see the list of cases that you added to the default institute.

That's it! Go and explore Scout.


[google-console]: https://console.developers.google.com/project
[invoke]: http://invoke.readthedocs.org/en/latest/
[omim-register]: http://omim.org/api
[vagrant]: https://www.vagrantup.com/
