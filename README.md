# Scout

## Roadmap
We are trying to build Scout piece by piece. This is the prioritized order we are planning on implementing those pieces.

- [ ] Prepare real world representation of demo data
- [ ] Release a first draft of the working interface (core functionality)
- [ ] Make sure that the package is installable
- [ ] Take in a first round of feedback from close collaborators
- [ ] Add functionality for user management and comments
- [ ] Implement more of less MIP/Clinical Genomics specific functionality
	- Access rights connected with cases/families. "Admin" users should be able to view any case.


## Quickstart

Run the following commands to bootstrap your development environment.

```bash
# it's always a good idea to work in a virtual environment
$ mkvirtualenv scout
$ workon scout
$ git clone https://github.com/Clinical-Genomics/scout.git
$ cd scout
$ pip install -r requirements/dev.txt
```

This doesn't mean that everything will work just like that. You also need some Google OAuth keys and other secret stuff. The config should be stored in a config file:

```
/scout
	/instance
		scout-dev.cfg  <-- put config here!
	/scout
```

When you have the instance folder in place you can start Flask like so:

```bash
$ python manage.py -c "$(pwd)/instance/scout.cfg" vagrant
```


## Running the tests

To run all tests, run:

```bash
$ python manage.py test
```
