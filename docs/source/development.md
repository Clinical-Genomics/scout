# Development

## Core developers

- Robin Andeer (RA)
- Måns Magnusson (MM)
- Henrik Stranneheim (HS)
- Mats Dahlberg (MD)


## Flask structure
Blueprints separate as much logic as possible from the central Flask server. This includes views, templates, and static assets but not yet Flask extensions.


## Fixtures data
The default fixtures adapter is implemented in ``chanjo.ext.backend.FixtureAdapter``. If you are writing a new adapter, please look at the implementation of the ``FixtureAdapter`` and ``BaseAdapter`` to follow the defined API style.
