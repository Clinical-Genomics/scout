# Institutes

Scout was made as a centralized tool where multiple users from different customers could work against the same instance.
Institutes is a way to separate sensitive information from the users.
Each [case](cases.md) has to have a institute as owner.
A [user](users.md) belongs to an institute and in that way restricted to see only the cases owned by that institute.
So one instance of scout can have one or many institutes. Each institute could be the owner of multiple cases and have
multiple users attached. Each institute has to have a unique identifier, `institute_id`.

## Settings
From the Settings page, users and admins can set the institute display name, Sanger order email recipients, default
coverage cutoff for reports, default frequency cutoff for the institutes clinical variants filter.

In the menu "Gene panels available for filtering", users can check zero or more of the institutes panels to always be
available as panel options on the variantS filter. Note that all cases may not have been processed bioinformatically to
return variants from all genes in the clinical setting. If so the search will still return a message saying the gene
was not among the clinical genes for the case. Consider opening the case for research or ordering a rerun.

New phenotype groups can be added from this page. Such custom phenotype groups can then be selected from the case page.

Available patient cohorts can be edited. Select or deselect existing ones, or type new free text labels to create new
cohorts.

Users with admin privileges can also select the LoqusDB instance to use for local observations from a menu of those
configured on Scout startup - see [admin guide - loqusdb](../admin-guide/loqusdb_integration.md).

## Causatives

The causatives page lists all variants marked causative for the institutes cases. Use arrows to sort by column, and
the buttons to copy a simplified version or export to Excel.


