# Scout REViewer Service integration

[Scout-REViewer-service][srs] provides a way to integrate [ExpansionHunter][expansion-hunter] [REViewer][reviewer] visualisation for short tandem repeats.

# Installation

Follow the build and installation instructions on available from the [Scout REViewer Service][srs] repository.

```bash
git clone https://github.com/Clinical-Genomics/Scout-REViewer-service.git
```

Production ready Docker and Docker compose installation options are available for testing.
Modify the `.env` file to point to your [ExpansionHunter][expansion-hunter] case files.

The container, once started, will provide an HTTP interface on a selected port.

# Configuration

Point Scout to the [Scout-REViewer-service][srs] URL host and port by editing the following lines in your `scout.config`:

```yaml
# Connection details for Scout REViewer service
# SCOUT_REVIEWER_URL = "http://127.0.0.1:8000/reviewer"
```

# Case configuration files

In your case load configuration file, provide paths to Expansion Hunter individual VCF, realignment bam-let files (not the regular sample full alignment `.cram` files) and if differing from the defaults given in the SRS configuration, reference genome and Expansion Hunter JSON catalog files.
Please see [Load Config File](./load-config.md) for parameter names and details.

[expansion-hunter]: https://github.com/Illumina/ExpansionHunter
[reviewer]: https://github.com/Illumina/REViewer
[srs]: https://github/Clinical-Genomics/Scout-REViewer-service
