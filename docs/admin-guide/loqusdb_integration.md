# Loqusdb integration

[Loqusdb][loqus] is a tool to keep track of local observation of genomic variants. Local frequencies/observations has been shown to add value to the analysis of genomic data both for rare disease and cancer. Scout integrates with loqusdb by fetching data from a given instance of loqusdb via the CLI. Please note that loqusdb version >= 2.5 needs to be installed.

## Setup

To avoid dependency conflicts loqusdb should be installed in an environment separate from scout.
Install loqudb according to the instructions on the package homepage. This can be done using the same environment or another virtual environment, also the same mongodb process can be used for the loqus database however if large datasets(1000s of whole genomes) are expected it is preferable to keep loqusdb and scout in separate instances. 


### Config Parameters

* `id`: Id of configuration. Defaults to "default". Mandatory when configuring multiple instances.
* `binary_path`: Path to LoqusDB binary. Mandatory. 
* `config_path` is alternative if not connecting to the default (which is `port=27017`, `host=localhost`). Optional.


### Configure One LoqusDB

In the config `config.py` give the connection information like:

```python
#connection details for LoqusDB MongoDB database
LOQUSDB_SETTINGS = dict(
    binary_path='/path/to/bin/loqusdb',
    config_path=<path/to/loqus/config>
)
```



### Configure Multiple LoqusDB

It is possible to configure LoqusDB per Institute.

1. Edit config.py
To configure a separate LoqusDB give it reference "id". If needed configure an (optional) config_path. An entry with id "default" should always exist.

```
    LOQUSDB_SETTINGS = [
        {"binary_path": "/path/to/bin/loqusdb", "id": "default", "config_path":"loqus.cfg"},
        {"binary_path": "/path/to/bin/loqusdb", "id": "foo", "config_path":"bar.cfg"}
    ]
```

2.1 Configure Institute via Scout Browser
Go to sidebar 'Settings'. Find 'LoqusDB id' and enter the configured id from 
config.py. Click Save. Your configuration is now active.

![Screenshot 2020-07-10 at 12 52 16](https://user-images.githubusercontent.com/1150065/87147271-9ea50600-c2ac-11ea-9f66-333b37783d52.png)

URL for institute settings: `http://localhost:5000/overview/<institute>/settings`


2.2 Configure Institute via Command Line

    $ scout update institute  <institute> --loqusdb_id <loqusdb_id>




## Result
Now scout will display if the variant has been seen in other cases and also will link to these if they exists in the same scout instance.

Whenever a user clicks on a variant scout will query loqusdb for that variant and display the information given if the loqusdb settings are used as above. There will also be links to the other accessable cases where the variant can be found. A maximum of 10 cases will be displayed, however the total number of observations will be visible in numbers.

[loqus]: https://github.com/moonso/loqusdb




