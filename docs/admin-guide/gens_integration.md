# Gens integration

[Gens][gens] is a interactive webbased tool to visualize copy number profiles in wgs data. It display the normalized read depth and alternative allele frequency in relation to transcripts, variants and previously annoated marker pannels.

## Setup

To avoid dependency conflicts Gens should be installed in an environment separate from scout.
Install Gens according to the instructions on the [tool homepage][gens]. This can be done using the same environment or a virtual environment.

### Config Parameters

* `GENS_HOST`: The IP or hostname of the server where Gens is hosted.
* `GENS_PORT`: Port number where gens is hosted (optional).

### Configure Gens integration

In the config `config.py` give the connection information like:

```python
GENS_HOST = 127.0.0.1
GENS_PORT = 5001
```

## Result
Now scout will display a button called "GENS" or "Show CN profile" in the case view and in the variant view for structural variants.

[gens]: https://github.com/Clinical-Genomics-Lund/gens
