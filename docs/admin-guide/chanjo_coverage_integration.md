# Chanjo coverage integration

Scout may be configured to visualize coverage reports produced by [Chanjo][chanjo].
To do so it is necessary to install the python package [Chanjo][chanjo] and its report visualization app, [chanjo-report][chanjo-report].

Both these programs require a database to store samples names, transcript specifications and statistics relative to the trascript coverage for all samples. Note that chanjo can be used as a standalone but chanjo-report needs to have access to the data produced by chanjo to generate coverage reports. **Scout does not require chanjo installed in the path to visualize coverage reports, but it is necessary to install chanjo-report and set up the connection to a database containing coverage data in order to use this fuctionality**.

## Chanjo database ##
Chanjo-report (and chanjo) work with MySQL and SQLite databases. This guide explains how to set up a MySQL database since this database is the one used in production at Clinical Genomics. For a guide on how to install MySQL on your server click [here](https://dev.mysql.com/doc/mysql-getting-started/en/). <br>
Once the database and the administrator user and password are configured, you can create the new database to contain the chanjo structures. To do so, from a terminal type:

```bash
mysql -u admin_user -padmin_password #no space between -p and password
mysql> create database chanjo4_demo;
mysql> exit
```
To create a new empty database download the empty schema `chanjo4_structure.sql` under `scout/demo/resources`. The command to restore the database from this dump file is:
```bash
mysql -u admin_user -padmin_password chanjo4_demo < path/to/chanjo4_structure.sql #no space between -p and password
```

To create instead a demo database containing coverage data for genes in panel1 for the samples used in the demo version of scout, you might download the schema `chanjo4_demo.sql`. This file is present in the folder `scout/demo`, along with the rest of the demo data. The syntax to create the database is the same as above.

Chanjo database consists of 3 tables:
- **sample**:

| Field      | Type         | Null | Key | Default | Extra |
|------------|--------------|------|-----|---------|-------|
| id         | varchar(32)  | NO   | PRI | NULL    |       |
| group_id   | varchar(128) | YES  | MUL | NULL    |       |
| source     | varchar(256) | YES  |     | NULL    |       |
| created_at | datetime     | YES  |     | NULL    |       |
| name       | varchar(128) | YES  |     | NULL    |       |
| group_name | varchar(128) | YES  |     | NULL    |&nbsp; |


- **transcript**:

| Field      | Type        | Null | Key | Default | Extra |
|------------|-------------|------|-----|---------|-------|
| id         | varchar(32) | NO   | PRI | NULL    |       |
| gene_id    | int(11)     | NO   | MUL | NULL    |       |
| gene_name  | varchar(32) | YES  | MUL | NULL    |       |
| chromosome | varchar(10) | YES  |     | NULL    |       |
| length     | int(11)     | YES  |     | NULL    |&nbsp; |


- **transcript_stat**:

| Field             | Type        | Null | Key | Default | Extra          
|-------------------|-------------|------|-----|---------|----------------|
| id                | int(11)     | NO   | PRI | NULL    | auto_increment |
| mean_coverage     | float       | NO   |     | NULL    |                |
| completeness_10   | float       | YES  |     | NULL    |                |
| completeness_15   | float       | YES  |     | NULL    |                |
| completeness_20   | float       | YES  |     | NULL    |                |
| completeness_50   | float       | YES  |     | NULL    |                |
| completeness_100  | float       | YES  |     | NULL    |                |
| threshold         | int(11)     | YES  |     | NULL    |                |
| _incomplete_exons | text        | YES  |     | NULL    |                |
| sample_id         | varchar(32) | NO   | MUL | NULL    |                |
| transcript_id     | varchar(32) | NO   | MUL | NULL    |&nbsp;          |


## chanjo-report ##

This package might be downloaded and installed via `git clone` and using `pip install` command (instructions [here](https://github.com/robinandeer/chanjo-report)), but perhaps the easiest way to make sure that it will serve pages once the app is invoked by scout is to install it with this command:
```bash
pip install scout-browser[coverage]
```
Just make sure that both scout and chanjo-report are installed on the same virtual environment (if you are using one).
Note that chanjo-report requires the package pymysql if it will be connecting to a MySQL database. So if it is not found in the environment you can install it with this command:
```bash
pip install pymysql
```

## Enabling the chanjo coverage integration in scout ##
In order to enable the support for the coverage report visualization in scout the configuration file named `config.py` under `scout/server` must be modified to include the following line:
<pre>
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@host:port/chanjo4_demo'
</pre>
The database URI provided in the line above refers to the MySQL database with the coverage data, so user and password are those used to connect to the database. Default database host and port are `localhost` and `3306` respectively.
If your scout implementation is using another configuration file other than the default `config.py` then the database connection URI must be added to this file instead.

<br>
Once all the above steps are executed you should see the "Coverage report" option on the left side bar under the scout case page. The buttons allow to generate HTML and PDF reports for the case samples.

[chanjo]: https://github.com/Clinical-Genomics/chanjo
[chanjo-report]: https://github.com/robinandeer/chanjo-report
