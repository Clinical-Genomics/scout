# Breaking changes - migration instructions for major and semi-major releases

Initial setup should always be smooth, but you do not have to reinstall
from scratch when a new release is out. Essentially always it is safe to go to a new
patch or minor version with your current setup. This is one of the beautiful things with
using a document database and REST interfaces. Occasionaly, especially when interaction
with other components change, a few steps will have to be taken. We will try to detail
them here.

A quick revert to an older version is mostly possible. There are however often foreseen
or unforeseen issues with reverting to older release versions,
especially if external data has been loaded or cases and events have been added. We try not to
make it too difficult to revert in a stage environment,
but we always believe the way is forward, and do not actively test the effects of reverting.

## Migrating to version 4.21
### Optional configuration of multiple loqusdb instances
The documentation for [loqusdb integration](./loqusdb_integration.md) has been updated to
reflect the new configuration options. See also PR #1984 and issue #1921.
