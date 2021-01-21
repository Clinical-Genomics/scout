# Backing up Scout
In general it is best practice to follow the mongodb official [recommendations][mongodbbackup] for backing up a database.
For a "light" backup there is a command in scout which works as a wrapper around [`mongodump`][mongodump]. This command was added to ease the process of backing up without including static information. Some of the collections are better to recreate than to backup including genes, transcripts and especially the gigantic variants collection. Please make sure [`mongodump`] is on your `PATH` before running this backup command.

## Backup command

To do an incomplete backup run:

```
scout export database -o <path/to/folder/>
```

This command will backup all non-static collections that saves user input data, namely:

```
        user_collection
        institute_collection
        event_collection
        case_collection
        case_group_collection
        panel_collection
        acmg_collection
        clinvar_submission_collection
        filter_collection
```

The following will not be backed up but can easily be recreated:

```
        hgnc_collection
        hpo_term_collection
        disease_term_collection
        variant_collection
        clinvar_collection
        exon_collection
        transcript_collection
        filter_collection
```

IF a user want to backup the whole database use the flag `--all-collections`, however in that case we recommend to follow mongodbs [recommendations][mongodbbackup] on database backups

## Recreate database

To recreate do the following steps:

1. Use a fully operational instance of scout, either an existing one or create one with `scout setup database`
2. Run command `mongorestore --gzip path/to/dump`. Read docs for [mongorestore][mongorestore] for more information
3. Everything should now be in place except for the variants. Add the variants for a case with `scout upload variants <case_id>`. See `--help` for more info.


[mongodump]: https://docs.mongodb.com/manual/reference/program/mongodump/
[mongorestore]: https://docs.mongodb.com/manual/reference/program/mongorestore/
[mongodbbackup]: https://docs.mongodb.com/manual/core/backups/
