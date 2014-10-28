# Development

## Core developers

- Robin Andeer (RA)
- Mats Dahlberg (MD)
- Henrik Stranneheim (HS)
- Måns Magnusson (MM)


## Choices
**MongoDB**. No migrations. Simple installation.

**Flask**. There isn't any supirior server but we still picked one for a reason. Flask is very Pythonic, a large and growing user base, lots of actively developed extensions, and uses Jinja2 which is the best templating engine around. In short, it meets all the nessesary requirements for a good choice of Python server. What finally convinced me that it was the right choice for this project was reading [these comments](https://news.ycombinator.com/item?id=2705770).

**MongoEngine**. Using an ODM has the benefit of dealing with a cleaner interface to the database which increases code readability. It also allows us to use the Flask-Admin plugin and enforces DRY when using Flask-WTForms.
I want to use gulp as my build tool. As such it will handle compilation of frontend code, both in production and during development.

**Frontend**
The build pipeline will need to handle all kinds of tasks and files but not right from the start.

  - HTML: it will vulcanize Polymer elements into a file ready to be included by Flask/Jinja.
  - Styles: it will comile SCSS files both for custom elements and the overall styles for the site.
  - Scripts: it will compile CoffeeScript both for custom elements and the overall scripts for the site.
  - In production, it will also minify and optimize the assets.
  - It should also enable live reloading and style injection through a proxy Flask server.
  - It will integrate with bower to download the dependencies
  - It will not initially have to deal with bourbon...

Implementation wise:

- polymer: future standard, ties in nicely with material design. Allows us to decide what is interactive and what isn't. We get a lot for free. I get more exitement out of the project.

- node: standard (besides Rails) in the industry, offers too many benefits for development to give up!

- gulp: I use gulp to get a readable config file and fast rebuilds

- browsersync: taken over after "live reload", seems like a more complete package

- scss: the closest to a standard and allows us to use fast libsass compilation
coffeescript: readability, boilerplate, easier to write quality JavaScript code



## Flask structure
As much as possible, we try to separate code into logical Blueprints. I've also set up an experiment to futher componentalize blueprints. Now, blueprint-specific extensions are defined inside the blueprint and initialized in a custom ``init_blueprint`` function.

The Blueprint is now responsible for templates, (static files), Flask extensions, and views. One extension is the admin blueprint where I haven't worked out a way of overwriting templates inside the blueprint package.


## Fixtures data
Flask defaults to using fixtures in the form of JSON documents (that are also meant to be used for testing.) The content in ``tests/fixtures/{families,variants}.json`` should reflect how variants and families will be delivered from either of the backend adapters.

The default fixtures adapter is implemented in ``chanjo.ext.backend.FixtureAdapter``. If you are writing a new adapter, please look at the implementation of the FixtureAdapter and BaseAdapter to follow the defined API style.
