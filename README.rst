===============================
Scout
===============================

Quickstart
----------

Run the following commands to bootstrap your development environment.

.. code-block:: bash

    # it's always a good idea to work in a virtual environment
    $ mkvirtualenv scout
    $ workon scout

    $ git clone https://github.com/Clinical-Genomics/scout.git
    $ cd scout
    $ pip install -r requirements/dev.txt
    $ python manage.py vagrant

This doesn't mean that everything will work just like that. You also need some Google OAuth keys and other secret stuff. The config should be stored in a config file:

.. code-block::

  /scout
    /instance
      scout-dev.cfg  <-- put config here!
    /scout

When you have the instance folder in place you can start Flask like so:

.. code-block:: bash

  $ python manage.py -c "$(pwd)/instance/scout.cfg" vagrant


Running Tests
-------------

To run all tests, run:

.. code-block:: bash

    $ python manage.py test
