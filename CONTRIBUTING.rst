Development
-----------

`Install MongoDB <http://tecadmin.net/install-mongodb-on-ubuntu/>`_

Vagrant is used to create a separate and reproducible development environment. 

Two ports are forwarded to the host:

  - 5000 -> 5089 (Flask)
  - 3000 -> 3000 (BrowserSync, needs to be the same on guest/host!)

The development server is Flask (with debug and reload turned on.) Flask will reload the server automatically when changes are made to the code (but not reload the browser.)

When you work on the frontend Gulp+BrowserSync is used and started as a separate process to the Flask server. Gulp will compile assets and put them in a public folder (which is symlinked/connected to Flask "static"). For the finished assets, BrowserSync will inject CSS and auto-reload the browser when nessesary.

CSS
~~~
The preprocessor for CSS used is SCSS and compiled using the node-sass/libsass compiler. The Bourbon library is loaded by default.

Browser support is limited and developers are encouraged to use flexbox instead of relying on something like Bootstrap.

HTML
~~~~
HTML is not preprocessed since it's written as Jinja2 templates.

### Tips
Whenever in doubt, use whatever convention GitHub is using. No more JS than that, be strict about the REST interface conventions:

  /<username>/<repo>/issues/new
