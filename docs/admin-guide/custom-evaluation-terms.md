## Custom evaluation terms

In scout you can tag a variant with various types of metadata including reasons for the variant being dismissed.

### Default terms

When setting up Scout for the first time a collection of dismissal and manual rank terms are loaded into the database. These are loaded from `scout/resources/variant_dismissal_terms.json` and `scout/resources/variant_manual_rank_terms.json`.

### Adding custom terms

You can add new evaluation terms with the CLI command `scout load evaluation-term`. The command takes several options of which most are optional. Use `scout load evaluation-term --help`
to see which optionas that are mandatory and optional.

If the `rank` is not set the term will be automatically assigned a rank.

### Adding multiple terms

Alternatively you can add multiple terms with the command `scout load batch-evaluation-term` that takes a json file containing multiple **terms** in a array.

A **term** is has the following structure.

``` json
{
  "name": "Name of a term",
  "description": "Verbose description of term",
  "institute": "all",
  "analysis_type": "all",
  "internal_id": "common-public",
  "term_category": "dismissal_term",
  "rank": 2
},
```

Terms needs to be assigned to category which determines how and where they are shown in the GUI. The current categories are `dismissal_term` and `manual_rank`.

The arguments `institute` and `analysis_type` determines when a given term is going to be displayed. For instance a term where `institute == "cust000"` is only going to be shown for cases assigned to institute **cust000**. Likewise are terms with `analysis_type == "cancer"` only going to be displayed for cancer cases. These defaults to **all** which means that it is a generic term for all insitutes and all types of analysis.

The argument "rank" determines the order of terms are shown.
