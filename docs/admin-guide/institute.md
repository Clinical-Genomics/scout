## Institutes

Institutes are objects that group users and cases. Users belong to a institute and in this way permissions to view cases can be handeld. Cases are always "owned" by an institute and thereby grants acces for all users within that institute to view and work with a case. Cases can be shared with other institutes.

Institutes have a unique internal id and a display name that is what the users see when browsing. One or several users can be sanger recipients for a institute which means that when a user is pushing the button "Order Sanger" on the variant page an email is sent to all sanger recipients with relevant information, such as coordinates for a variant.

## Updating institutes

All variables except `'internal_id'` can be updated for a institute. 

Please run `scout update institute` for more information.

## Phenotype Groups

Phenotype groups is a feature on institute level. So each institute can have their own set of phenotype groups.
There is a default set of phenotype groups that all institutes will have access to, those are described in 
`scout.constants.phenotype`. 
To overwrite or add phenotype groups use cli function `scout update groups`.
If specifying groups in a file, use a `csv` file where column one holds HPO-ids on the format `HP:0000001`.
Second column is optional and can include abbreviations for the phenotype groups.



```bash
$scout update groups --help
Usage: scout update groups [OPTIONS] INSTITUTE_ID

  Update the phenotype for a institute. If --add the groups will be added to
  the default groups. Else the groups will be replaced.

Options:
  -p, --phenotype-group TEXT     Add one or more phenotype groups to institute
  -a, --group-abbreviation TEXT  Specify a phenotype group abbreviation
  -f, --group-file FILENAME      CSV file with phenotype groups
  -a, --add                      If groups should be added instead of
                                 replacing existing groups
  --help                         Show this message and exit.
```