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
Users can belong to multiple institutes. Each institutes defines what cases can be viewed by the user. If you only belong to a single institute you will be redirected automatically to "Cases".

----------

## Cases
This page displays the list of active cases for a particular institute. Each item links to the detailed view for that case. You can filter the list by typing into the search box above the list.

A quick link to get straight to the list of all clinical variants is also displayed. To indicate what cases have recently been added/updated, a "last updated" date is also displayed.

Sometimes you will also see a cyan colored dot to the left of the case ID. This is an indicator that there's been some recent activity in the case such as a new comment.

Your name will be tagged for each case that is assigned to you. For cases that are assigned to other people you will see a tag "ASSIGNED".

----------

## Case
This is the detailed view of one individual case. The intended use is to give a consise overview of the family under investigation and show recent activity related to the case.

### Pinned variants
There's a list of "Strong candidates" on the page. This list is curated by the collaborators and consists of "pinned" variants from the variants list. This feature can be used to mark variants of particular interest that you might want to highlight to other users (See more under "Variant".)

### Misc.
The case page also displays a simple wiki-style synopsis on the current case that can be used to communicate information on the case to collaborators.

The "Activity" feed is a reverse chronological list of events and comments related to the case. Examples of events include comments, status updates, assignments, Sanger sequencing orders etc.

### Actions
There are a few actions you can take on this page.

**Adopt case**: By clicking the button next to "Adopt" you can assign yourself to a case unless someone else has already done so. If you have assigned yourself to a case you can click your name to "unassign".

The case can be moved to "Research" which means all variants will be made visible for the entire exome. Clicking "Open research" will notify the administrators of the site. The user agrees that she is reponsible to have acquired an informed consent relevant for this action. This will also be logged as a new event in the case log.

**Edit case synopsis**: The case sysnopsis can be edited in a format known as [Markdown][markdown]. Just click "EDIT" to open the editor view. When you are finished click "SAVE" to save changes or "CANCEL" to abort.

**Comment**: You can leave comments in the activity log by writing a message in the input box next to the feed. Click "COMMENT" to submit the comment.

----------

## Variants
The big list of variants. This page serves as an overview of all data and annotations for a single case. It's meant to allow you to skim through many variants ordered by the ranking.

The first couple of columns are meant to give you a sense of place in the overall ranked list. The "Rank" column is especially useful after applying various filters.

Hovering over both "1000 Genomes" (frequency) and "CADD score" (severity) columns will reveal additional metrics in a popup.

Hovering over "Inheritance models" will pop up a list of all possible compounds if the variants follows this pattern.

At the bottom of the list you will find a button to load the next batch of variants in the list. To return to the previous batch of variants, just press the browser back button.

It's also possible to filter the variants using a number of different criteria. Open the filters panel by clicking the "filter" icon in the top right. Here you can fill in form and click "Filter variants" to update the list. This is also the place where you switch gene lists.

----------

## Variant
This is the most complex view with a lot of related data presented to the user in a compact way. A lot of thought went into the design of the layout so here it the imagined workflow.

### Toolbar
Two options are added to the right side of the menu:

  - Send Sanger email to an institute related email address.
  - Pin the current variant as interesting so that it shows up in the case view.
  - Mark variant as causative. This is only to be used when a variant is confirmed to be causative - it will set the case to "solved" automatically.

### Fixed header
Introduces the basic facts of the variant that the user is often referring back to. As an example you need to refer back to the chromosome when assessing possible inheritance models.

### Summary
This is the first a user looks at when assesing the variant.

  - Rank score/CADD score
  - Disease gene model, possible inheritance models, OMIM model
  - Frequencies
  - CLINSIG number

### Details
Depending on the first assessment, this section represents what a user digs deeper into.

  - Predicted protein changes
  - Severities
  - Conservation

  => "Matrix" with highlighted cells (significant numbers)

### GT Call

### Compounds
Only interesting when the compound inheritance pattern is required, the list can be very long - best to put it far down the page.

[markdown]: https://help.github.com/articles/markdown-basics/
