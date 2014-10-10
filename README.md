===============================
Scout
===============================

Quickstart
----------

First, set your app's secret key as an environment variable. For example, example add the following to ``.bashrc`` or ``.bash_profile``.

.. code-block:: bash

    export _SECRET = 'something-really-secret'


Then run the following commands to bootstrap your environment.


::

    git clone https://github.com/robinandeer/
    cd 
    pip install -r requirements/dev.txt
    python manage.py db init
    python manage.py db migrate
    python manage.py db upgrade
    python manage.py server



Deployment
----------

In your production environment, make sure the ``_ENV`` environment variable is set to ``"prod"``.


Shell
-----

To open the interactive shell, run ::

    python manage.py shell

By default, you will have access to ``app``, ``db``, and the ``User`` model.


Running Tests
-------------

To run all tests, run ::

    python manage.py test


Migrations
----------

Whenever a database migration needs to be made. Run the following commmands:
::

    python manage.py db migrate

This will generate a new migration script. Then run:
::

    python manage.py db upgrade

To apply the migration.

For a full migration command reference, run ``python manage.py db --help``.

## Development
Install MongoDB
http://tecadmin.net/install-mongodb-on-ubuntu/


Add to your ``.{zsh,bash}rc``:

```bash
export PATH="$HOME/.bin:$PATH"

alias ipython='nocorrect ipython'

export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_VIRTUALENV_ARGS='--no-site-packages'
source /usr/local/bin/virtualenvwrapper.sh

export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
```

## Development
Vagrant is used to create a separate and reproducible development environment. 

Two ports are forwarded to the host:

  - 5000 -> 5089 (Flask)
  - 3000 -> 3000 (BrowserSync, needs to be the same on guest/host!)

```html
<script type='text/javascript'>//<![CDATA[
document.write("<script async src='//HOST:3000/browser-sync/browser-sync-client.1.5.2.js'><\/script>".replace(/HOST/g, location.hostname).replace(/PORT/g, location.port));
//]]></script>
```

The development server is Flask (with debug and reload turned on.) Flask will reload the server automatically when changes are made to the code (but not reload the browser.)

When you work on the frontend Gulp+BrowserSync is used and started as a separate process to the Flask server. Gulp will compile assets and put them in a public folder (which is symlinked/connected to Flask "static"). For the finished assets, BrowserSync will inject CSS and auto-reload the browser when nessesary.

### CSS
The preprocessor for CSS used is SCSS and compiled using the node-sass/libsass compiler. The Bourbon library is loaded by default.

Browser support is limited and developers are encouraged to use flexbox instead of relying on something like Bootstrap.

### JavaScript
The preprocessor for JS is CoffeScript.

### HTML
HTML is not preprocessed since it's written as Jinja2 templates.

### Tips
Whenever in doubt, use whatever convention GitHub is using. No more JS than that, be strict about the REST interface conventions:

  /<username>/<repo>/issues/new
