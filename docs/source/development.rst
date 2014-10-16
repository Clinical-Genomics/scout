===============
Development
===============

Core developers
---------------

- Robin Andeer (RA)
- Mats Dahlberg (MD)
- Henrik Stranneheim (HS)
- Måns Magnusson (MM)


Choices
-------
**MongoDB**. No migrations. Simple installation.

**Flask**. There isn't any supirior server but we still picked one for a reason. Flask is very Pythonic, a large and growing user base, lots of actively developed extensions, and uses Jinja2 which is the best templating engine around. In short, it meets all the nessesary requirements for a good choice of Python server. What finally convinced me that it was the right choice for this project was reading `these comments <https://news.ycombinator.com/item?id=2705770>`_.

**MongoEngine**. Using an ODM has the benefit of dealing with a cleaner interface to the database which increases code readability. It also allows us to use the Flask-Admin plugin and enforces DRY when using Flask-WTForms.


Flask structure
---------------
As much as possible, we try to separate code into logical Blueprints. I've also set up an experiment to futher componentalize blueprints. Now, blueprint-specific extensions are defined inside the blueprint and initialized in a custom ``init_blueprint`` function.

The Blueprint is now responsible for templates, (static files), Flask extensions, and views. One extension is the admin blueprint where I haven't worked out a way of overwriting templates inside the blueprint package.
