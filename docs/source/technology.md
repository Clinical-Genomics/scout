# Technology
Scout sits on a technology stack that is built around Python.


## Server
The server running the application is **Flask**. It's very Pythonic, has a large and growing user base, lots of actively developed extensions, and uses Jinja2 which is the best templating engine around. In short, it meets all the necessary requirements for a great Python server. The nail in the coffin was  reading [these comments](https://news.ycombinator.com/item?id=2705770).


## Database
We've opted to use **MongoDB**. It's the most popular NoSQL database, meaning no migrations and simple installation. MongoDB will allow us to define filter queries easily and make use of "upserts" that will simplify our loading script.

### Database interface/ODM
We use **MongoEngine** for some of the documents in the data store. Using an ODM has the benefit of dealing with a cleaner interface to the database which increases code readability. It also allows us to use the Flask-Admin and Flask-WTForms plugins.

Some parts of the database will likely be to customized to fit cleanly into any ODM solution. For working with these collections, we will use the raw **pymongo** API. The breaking point is basically everything included in the database adapter can use whatever MongoDB API whereas anything outside of said adapter will use MongoEngine.


## Frontend
We will be focusing on server side rendered templates. However, everyone needs a JavaScript abstraction layer these days. Some are fine with jQuery and other opt for something more encompassing like Ember.js. For this project we look to the future and use a **Polymer** based approach. This also means that we only plan to target the most recent version of all major browsers.

The main benefit of Polymer is that it will let us decide what regions will be made interactive and what regions won't. Polymer also ties in nicely with material design which will influence the interface a lot.

### Stylesheets
We use **SCSS** preprocessing. It's the closest thing to a standard (besided CSS) and allows us to use fast libsass compilation. Compared to raw CSS it will increse readability and enable simple modularization of the code base.

### Scripts
The scripts we write will be in CoffeeScript. It is more readable, requires less boilerplate, and makes it easier to write quality JavaScript code. We do enforce that contributors first learn the basics of JavaScript before picking up CoffeeScript.

### Build pipeline
We use gulp as the build tool to get a readable config file and fast rebuilds. It will handle compilation of all frontend code, both before deployment (minify etc.) and during development. This means we will also use **Node.js** which, besides Rails, is standard in the industry. It simply offers too many benefits for development to give up for any Python native solution.

Gulp will:

  - vulcanize Polymer elements into a single file ready to be included by Flask/Jinja,
  - comile SCSS files both for custom Polymer elements and the global site styles,
  - compile CoffeeScript both for custom Polymer elements and the global site scripts,
  - minify and optimize the assets in production,
  - enable live reloading and style injection through a proxy Flask server using BrowserSync,
  - integrate with bower to download dependencies

The build system will be tightly integrated with the Flask server setup to avoid adding more complexity than necessary.
