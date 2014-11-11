# Pages
Scout can be logically separated into a number of pages with different responsibility and purpose. The core pages include institues, cases, case, variants, and variant.

This document describes each page, it's purpose, it's function, and it's intended use.

----------

## Index
This is the default view that all users who aren't logged in will arrive at. This page is usually called a "landing page". It's main purpose is to introduce potentially new users to the website. It's allows users to sign in/up.

### Sign up
New users have to apply for access. The team leaders for each institute are required to sign off on new users. Authentication is handled thourgh Google OAuth using separate @clinicalgenomics.se accounts.

### Sign in
We have chosen to use Google OAuth for the signup process. This means that users click on a button on the first page which launches the OAuth process. When the user is returned, she will see her customized welcome page.

> Should we still regularly discard the authentication token in (short) intervals?

----------


## Welcome page
This is the first page a user sees when she first logs in from the index page. This view is normally personalized to the user that just logged in. She is presented with a list of institutes she belongs to.

### Institute selection
A user can belong to multiple institutes. Each institutes defines what cases can be viewed by the user. Some users will only ever belong to one institute making this selection void.

----------


## Cases
This page displays the list of active cases for any particular institute. Each item links to the detailed view for that case. A quick link to get straight to the list of all variants is also displayed. To help users know what cases have recently been added/updated, a "last updated" date is also displayed.

----------


## Case
This is the detailed view of one individual case.

This is where users can request to have the research list opened. It will send an email to the administrators of the site. The user agrees that she is reponsible to have acquired an informed consent for this action. This will also be logged as a new event in the case log.

The case page also displays a simple wiki-style briefing report about the current case that can be used to communicat details on the case to collaborators.

> How are we going to handle tagging comments as "finding", "action", "conclusion"? Perhaps we should just stick with something more general; tags + category etc.

Lastly users can also mark verified disease causing variants. Once a variant has been marked in this fashion, the case can be marked as solved and hence no longer active.
