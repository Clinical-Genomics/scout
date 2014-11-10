# Development

## Core developers

- Robin Andeer (RA)
- Mats Dahlberg (MD)
- Henrik Stranneheim (HS)
- Måns Magnusson (MM)


## Flask structure
As much as possible, we try to separate code into logical Blueprints. I've also set up an experiment to futher componentalize blueprints. Now, blueprint-specific extensions are defined inside the blueprint and initialized in a custom ``init_blueprint`` function.

The Blueprint is now responsible for templates, (static files), Flask extensions, and views. One extension is the admin blueprint where I haven't worked out a way of overwriting templates inside the blueprint package.


## Fixtures data
Flask defaults to using fixtures in the form of JSON documents (that are also meant to be used for testing.) The content in ``tests/fixtures/{families,variants}.json`` should reflect how variants and families will be delivered from either of the backend adapters.

The default fixtures adapter is implemented in ``chanjo.ext.backend.FixtureAdapter``. If you are writing a new adapter, please look at the implementation of the FixtureAdapter and BaseAdapter to follow the defined API style.
