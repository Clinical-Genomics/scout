# Pages
Scout can be logically separated into a number of pages with different responsibility and purpose. The core pages include institues, cases, case, variants, and variant.

This document describes each page, it's purpose, function, and intended use.

----------

## Index
The "landing page". This is your default view where all users who aren't logged in will arrive at. It's main purpose is to introduce potentially new users to the website. It also allows you to sign in.

### Sign up
New users have to apply for access prior to logging in the first time. The team leaders for each institute are required to sign off on new users.

### Sign in
We have chosen to use Google OAuth for the signup process. This means that you click on a button on the first page which launches the OAuth process. When the user is returned, you will see your customized welcome page.

We also use separate ``@clinicalgenomics.se`` accounts to be able to enforce 2-factor authentication.

----------

## Welcome page
This is the first page a you see after logging in. Notice your first name in the upper right corner. You can also access the list of institutes you belong to.

### Institute selection
Users can belong to multiple institutes. Each institutes defines what cases can be viewed by the user. If you only belong to a single institute you will be redirected automatically to [Cases](cases.md).


### Cases page

An overview of the [cases](cases.md) that belongs to an institute and status for the cases.

### Variants page

A list of the [variants](variants.md) with some relevant information. Variants are grouped into SNVs, SVs, and STRs. Variants can have a separate clinical and research list. A cancer / somatic variant view is also available.

### Detailed variant page

When choosing a [variant](variants.md) the detailed variant information is displayed

### Gene Panels

Page to investigate and manipulating [gene panels](panels.md).

### Managed variants

Managed variants allows users to add variants of interest to follow. Variants can be added manually or loaded from a csv file. Managed variants are always loaded if encountered during VCF file parsing,
and will be highlighted on the [case page](cases.md) as well as on the [variant page](variants.md). The list of managed variants shown on the managed variants page can be filtered. Mark the variant category -
snv, sv, cancer and cancer_sv are managed separately. No links to actual observations or cases are found from the Managed variants page.

A valid managed variants `.csv` file can look like this:
```
chromosome;position;end;reference;alternative;category;sub_category;description
14;76548781;76548781;CTGGACC;G;snv;indel;IFT43 indel test
17;48696925;48696925;G;T;snv;snv;CACNA1G intronic test
7;124491972;124491972;C;A;snv;snv;POT1 test snv
```
