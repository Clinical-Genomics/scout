# Technology
Scout sits on a technology stack that is built on and around Python. When Python isn't enough, we have made calculated descisions to integrate with additional tools.


## Server
A choice of Python servers comes down to Django, Tornado, and Flask. They are all capable options and we probably could've have gone either way.

Internally, we had more experience using **Flask** in the past and this was also the choice we settled for. It feature a very Pythonic API, has a large and growing user base, lots of actively developed extensions, and uses Jinja2 which is the best templating engine around. Flask covers all necessary requirements but the nail in the coffin was reading [these comments](https://news.ycombinator.com/item?id=2705770).


## Database
We use **MongoDB**. It's a popular NoSQL database, meaning no migrations and simple development. MongoDB simplifies filter queries and database loading through "upserts".

### Database interface/ODM
**MongoEngine** is used for some of the documents in the data store. Using an ODM has the benefit of dealing with a cleaner interface to the database which increases code readability. It also supports Flask-Admin and Flask-WTForms plugins.

To optimize query execution, parts of the database will require extensive customization. For working with these collections, we will use drop into the raw **pymongo** API.


## Frontend
Most data will be rendered server side. However, everyone needs a JavaScript abstraction layer these days and jQuery often isn't enough. To componentalize and avoid binding data into the DOM we use a simple MVVM framework called [Vue.js][vue].

### Stylesheets
**SCSS** preprocessing is the closest thing to a standard (besided CSS) and allows fast libsass compilation. Compared to raw CSS it will increse readability and enable simple modularization of the code base.

### Scripts
The scripts will be written in either **JavaScript** or **CoffeeScript** (CS). CS is more readable, requires less boilerplate, and makes it easier to write quality JavaScript code. We do enforce that authors first learn the basics of JavaScript before picking up CoffeeScript.

### Build pipeline
**Gulp** is the build tool. It brings readable config files and fast rebuilds. It handles compilation of all frontend code, both during development and in preparation of deployment (minify etc.). This means we will also use **Node.js** which, besides Rails, is standard in the industry. It simply offers too many benefits during development to give up for any Python native solution.

Gulp is reposible for:

  - compiling CoffeeScript and SCSS files
  - minifing and optimizing the assets for production
  - enabling live reload and style injection using **BrowserSync**

The build system will be tightly integrated with the Flask server setup to avoid adding more complexity than necessary (one extra process).


[vue]: http://vuejs.org/
