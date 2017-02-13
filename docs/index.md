# Scout

Analyze VCFs quicker and easier.

--------------

## Introduction

Scout is a web-based **visualizer for VCF files** intended for a clinical audience. Analysis of genomics data generates massive amounts of information. Our tool bridges the gap between the raw output and something that anyone with genetic background can use to analyze and filter out interesting variants involved in rare inherited diseases. Scout also leverages it's centralized database to enable team collaboration through user comments, prioritization and customizable sharing of cases.

## Getting Started

The general work flow when you work in Scout look something like this:

### Log in to access your institute's data

Each user can belong to one or more "institutes" which is used to determine what data you are allowed to see. We rely on [Google OAuth][google-signin] to facilitate the authentication by using Google accounts.

### Review the status of ongoing cases

This view provides a high level overview of all your institutes cases. You can see who is assigned a case, whether new data has recently been uploaded, the type of sequencing etc.

### More to come...

## Contributing
See [Development](development).


[google-signin]: https://developers.google.com/identity/
