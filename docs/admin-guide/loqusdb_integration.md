# Loqusdb integration

[Loqusdb][loqus] is a tool to keep track of local observation of genomic variants. Local frequencies/observations has been shown to add value to the analysis of genomic data both for rare disease and cancer. Scout integrates with loqusdb by fetching data from a given instance of loqusdb via the CLI.

## Setup

Install loqudb according to the instructions on the package homepage. This can be done using the same environment or another virtual environment, also the same mongodb process can be used for the loqus database however if large datasets(1000s of whole genomes) are expected it is preferable to keep these separate. In the config `config.py` give the connection information like:

```python
#connection details for LoqusDB MongoDB database
LOQUSDB_SETTINGS = dict(
    binary_path='/path/to/bin/loqusdb',
    config_path=<path/to/loqus/config>
)
```
where the `binary_path` is mandatory and `config_path` is alternative if not connecting to the default (which is `port=27017`, `host=localhost`)

Now scout will display if the variant has been seen in other cases and also will link to these if they exists in the same scout instance.


[loqus]: https://github.com/moonso/loqusdb
