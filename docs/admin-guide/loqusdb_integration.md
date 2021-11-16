# Loqusdb integration

[Loqusdb][loqus] is a tool to keep track of local observation of genomic variants. Local frequencies/observations has been shown to add value to the analysis of genomic data both for rare disease and cancer. Scout currently supports connections to Loqusdb via REST API, using the [loqusdbapi software][loqussbapi] (recommended option), or by fetching data from a given instance of loqusdb via the CLI. Please note that in both cases loqusdb version >= 2.5 needs to be installed.

Once connected with a loqusdb instance, whenever a user clicks on a variant scout will query loqusdb for that variant and display the information given if the loqusdb settings are used as above. There will also be links to the other accessible cases where the variant can be found. A maximum of 10 cases will be displayed, however the total number of observations will be visible in numbers.

One or more instances of loqusdb can be initialized when the Scout server is started by editing the LOQUSDB_SETTINGS in the Scout config file.


## Option 1: setup of a loqusdb instance executable as a binary file

To avoid dependency conflicts loqusdb should be installed in an environment separate from scout.
Install loqudb according to the instructions on the package homepage. This can be done using the same environment or another virtual environment, also the same mongodb process can be used for the loqus database however if large datasets(1000s of whole genomes) are expected it is preferable to keep loqusdb and scout in separate instances.


### Config Parameters

* `id`: Id of configuration. Defaults to "default". Mandatory when configuring multiple instances.
* `binary_path`: Path to LoqusDB binary. Mandatory.
* `config_path` is alternative if not connecting to the default (which is `port=27017`, `host=localhost`). Optional.


## Option 2: connecting to a loqussbapi instance via REST API

Perhaps this option represents the easiest and the long-term supported option to establish a connection and run queries to loqusdb.
Loqusdbapi should be running on a server with host and port reachable by the scout instance. Follow the instructions provided on the package [home page][loqussbapi] to either install it or run it in a Docker container.

## Configuring the loqusdb connections in Scout using the config file

Once a loqusdb instance is created via one one the two options (or both actually, since Scout supports the connection to multiple loqusdb instances), the `LOQUSDB_SETTINGS` parameter in the Scout config file (config.py) should be edited as shown in the following example:

```
LOQUSDB_SETTINGS = {
  "default" : {"binary_path": "/miniconda3/envs/loqus2.5/bin/loqusdb", "config_path": "/home/user/settings/loqus_default.yaml"}, # Example of an executable loqusdb binary file
  "loqus_api" : {"api_url": "http://127.0.0.1:9000"}, # Example or a loqusdb instance reachable via REST API,
  ..
}
```
The example above is showing the LOQUSDB_SETTINGS parameter as a dictionary containing 2 key/values, reflecting 2 eventual instances of loqusdb, one based on the executable binary file (option 1) and one reachable via REST API (option2). To reflect the infrastructure needs, it is possible to set as many connections to loqusdb instances as required.

Please note that the key used to define each of these instances (in this case default and loqus_api) will be later used in Scout to switch among the available instances (Scout at the moment doesn't support using different loqusdb instance at the same time, and it will be only possible to use one at the time for each institute).

Note also that regardless of the number of loqusdb instances (key/values present in the LOQUSDB_SETTINGS file), **one dafault loqusdb instance should be present with key `default`**. This entails that if you are connecting to only one loqusdb instance, then it should be named `default`.

## Switching between loqusdb instances from the institute settings in the Scout browser

This part applies only if more than one loqusdb instance is connected to Scout using the `LOQUSDB_SETTINGS` parameter present in the Scout config file. As mentioned before, **at the moment Scout support one loqusdb connection at the time for each single institute**.
The first time that the Scout browser is launched, all institutes will be set to use the default loqusdb instance. **Configuring a different loqusdb instance than the default one is done at the institute level, and only admin users have the permissions to change these settings**.

### Configuring institute-specific loqusdb instance via institute settings
From the institute page in the Scout browser, go to sidebar 'Settings'. Find 'LoqusDB id' and enter the configured id from
config.py. Click Save. Your configuration is now active.

![Screenshot 2020-07-10 at 12 52 16](https://user-images.githubusercontent.com/1150065/87147271-9ea50600-c2ac-11ea-9f66-333b37783d52.png)


It is additionally possible to configure a loqusdb instance for a given institute using the command line. Example:
```
scout update institute  <institute> --loqusdb_id <loqusdb_id>
```


[loqus]: https://github.com/moonso/loqusdb
[loqussbapi]: https://github.com/Clinical-Genomics/loqusdbapi
