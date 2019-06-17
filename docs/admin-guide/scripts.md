# Scripts folder

## genelist_to_panel.py

Used to print to terminal a gene panel based on a gene list.


## transfer-archive.py

Used to migrate case info from an old archive to a newer one.


## update_files_path.py

Used to change all paths in the database when moving cases's file from one server to another. The scripts checks if cases contain file paths pointing to location in the old server (**--test** option) and updates these paths to new paths on the new machine.

Usage:
 ```bash
python --db_uri mongodb_connection_uri -o /old/path/to/files -n /new/path/to/files
```

options:  
--test : Use this flag to test the function  
-d: Use this flag to create a list of keys where old path is found


## update_variant_panels.py

Update variant panels.
