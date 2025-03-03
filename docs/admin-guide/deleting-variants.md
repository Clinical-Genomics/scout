# Deleting Variants

The Scout command line provides instructions to remove variants from one or more cases using the `scout delete variants` command.

## Usage

To view available options, run:

```shell
scout delete variants --help
```

This will display:

```shell
Usage: scout delete variants [OPTIONS]

  Delete variants for one or more cases.

Options:
  -u, --user TEXT                 User running this command (email) [required]
  -c, --case-id TEXT              Case ID (e.g., expertpoodle or helpedgoat)
  -f, --case-file PATH            Path to file containing a list of case IDs
  -i, --institute TEXT            Restrict to cases with the specified institute ID
  --status [prioritized|inactive|active|solved|archived|ignored]
                                  Restrict to cases with the specified status
  --older-than INTEGER            Remove variants from cases older than (months)
  --analysis-type [external|mixed|ogm|panel|panel-umi|unknown|wes|wgs|wts]
                                  Restrict to cases with the specified analysis type
  --rank-threshold INTEGER        Remove only variants with a rank lower than this threshold
  --variants-threshold INTEGER    Remove variants only from cases containing at least this number of variants
  --rm-ctg [cancer|cancer_sv|fusion|mei|outlier|snv|str|sv]
                                  Remove only the specified variant categories
  --keep-ctg [cancer|cancer_sv|fusion|mei|outlier|snv|str|sv]
                                  Keep only the specified variant categories
  --dry-run                       Perform a simulation without removing any variants
  --help                          Show this message and exit.
```

### Parameter Descriptions

| Option                 | Description                                                                                                                                              |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--user (-u)`          | **Required.** The email of the user executing the command. The user must exist in the Scout database.                                                    |
| `--case-id (-c)`       | **Optional.** The case ID (e.g., `expertpoodle` or `helpedgoat`).                                                                                        |
| `--case-file (-f)`     | **Optional.** Path to a file containing a list of case IDs.                                                                                              |
| `--institute (-i)`     | **Optional.** Institute ID. Not required if a case ID is provided.                                                                                       |
| `--status`             | **Optional.** Restrict removal to cases with the specified status (e.g., `solved`).                                                                      |
| `--older-than`         | **Optional.** Remove variants from cases older than the specified number of months (e.g., `12` for cases older than a year).                             |
| `--analysis-type`      | **Optional.** Restrict removal to cases with the specified analysis type.                                                                                |
| `--rank-threshold`     | **Optional.** Remove only variants with a rank lower than this threshold.                                                                                |
| `--variants-threshold` | **Optional.** Remove variants only from cases containing at least this number of variants.                                                               |
| `--rm-ctg`             | **Optional.** Remove only the specified variant categories. Example: `--rm-ctg snv --rm-ctg sv`.                                                         |
| `--keep-ctg`           | **Optional.** Keep only the specified variant categories. Cannot be used together with `--rm-ctg`. Use multiple times to specify more than one category. |
| `--dry-run`            | **Optional.** Runs a simulation, showing an estimate of the number of variants to be removed without actually deleting anything.                                   |

> **Note:** If you are removing variants from Scout for the first time, it is strongly recommended to run a simulation first using the `--dry-run` option.

### Example Command

To simulate the deletion of variants that:

-   Have a rank lower than `5`
-   Belong to cases with `wgs` analysis type
-   Contain at least `100,000` variants
-   Are older than `24` months

Run:

```shell
scout delete variants --loglevel WARNING \
  -u youremail \
  --rank-threshold 5 \
  --analysis-type wgs \
  --variants-threshold 100000 \
  --older-than 24 \
  --dry-run
```
