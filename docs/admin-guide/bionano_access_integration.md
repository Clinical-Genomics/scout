## BioNano Access Server Integration
Starting from Scout release 4.71 the software can be configured to fetch FSHD reports for individual samples from a BioNano Genomics Access server.
Currently, a single user account is used for accessing all project samples. Depending on your setup, this user may need admin privileges to read all.
We find that a `read_only` user account works well.

### Basic configuration for BioNano Access Integration
Edit Scout config file adding the following parameters:
```
# BioNano Access Server extension
BIONANO_ACCESS = "https://bionano-access.scilifelab.se"
BIONANO_USERNAME = "USER"
BIONANO_PASSWORD = "PASS"
```

The server address `https://bionano-access.scilifelab.se` is an externally available URL

### Adding BioNano Access project and sample to the case config
Scout will look up samples using the BioNano Access project- and sample keys given for the individual.
The preferred way is by case config file, adding `bionano_access` `project` and `sample` fields to the individual (sample):
```
bionano_access:
    project: "230303_customer_projectA1"
    sample: "2023-12345"
```

The `scout update individual` command can alternatively be directly used to update individuals that are already loaded.
```bash
scout update individual -c internal_id -i ADM1059A2 bionano_access.project 230303_customer_projectA1
scout update individual -c internal_id -i ADM1059A2 bionano_access.sample 2023-12345
```

It is advised to give the original (not a copy) project and sample name, as this can cause issues on the API. A copy can still exist
and be used to restrict project read credentials on the Access server web interface appropriately.

Results appear in Scout as a tab for each case, reachable from the case page for cases that have `bionano_access` `project` and `sample` configured for at least one individual.
Results are not cached in Scout, but re-retrieved on page load.
