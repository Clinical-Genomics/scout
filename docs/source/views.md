# Views
Scout can logically be separated into a number of views with different responsibility and purpose. The core views include cases, case, variants, and variant.

This document describes each view, it's purpose, it's function, and how it's intended to be used.



## Index
This is the default view that all users who aren't logged in will arrive at. This page is usually called a "spash page". It's main purpose is to introduce potentially new users to the website. It's important that it provides a clear call to action, commonly a big button for signing in/up.

### Introduction
There should be a short section introducing Scout; what it is and intended usecase. A series of screenshots along with some brief words about the product should be fine.

### Sign up
When in comes to Scout, new users will have to apply for an account. We will require the team leader for each institute to sign off that a new user should be added to their Scout institute. We also give new users their separate @clinicalgenomics.se accounts to use for logging into Scout. This will make the signup process different from most web services. It would be nice to give new users some way of applying for a new account that might interface with a backend ticketing service or send an email to the administrators.

### Sign in
We have chosen to use Google OAuth for the signup process. This means that you click on a button on the first page which launches the OAuth procedure. When the user is returned to Scout, she will see her welcome page.

> Should we still regularly discard the authentication token in (short) intervals?

### Branding
Scout needs a somewhat strong brand. It should have personality and be clearly stated on the splash page. We will present the logo, name of the product, and a one sentence tagline.

We should call out all the people/institutes involved in the project. It makes sense to add the SciLifeLab (Clinical Genomics) and Karolinska Hospital logos. There should also be a link to the open source project in the footer.



## Menu & Navigation
The navigation menu will persist in some form across all pages of the site (apart from the index page).

### Sign in status
Because the user logged in, it's important to clearly display this. Commonly a user avatar along with the name (or username) is present in the upper right corner as part of the navigation.

### Site navigation
Links should be displayed in some form that allows simple navigation between the main (non-dynamic) pages.

### Common actions
This part of the menu could be responsive to what page we are currently on.

### Bread crumbs
It common that as a user drills into a page, the path to this is shown somewhere on the page. This could replace a title section of a page is it makes sense. This would offload the navigation solution.



## Welcome page
This is the first page a user sees when she first logs in from the index page. This view is normally personalized to the user that just logged in. She might for example be presented with an overview of recent activity.

### Institute selection
A user can belong to multiple institutes. Each institutes defines what cases can be viewed by the user. It makes sense to present this information as early as possible since many users will only ever belong to one institute making this selection void.



## Profile & Settings
It's not clear whether a user profile page is nessesary. However, we still need to devote some part of the site to user level settings. It seems only natural to combine these two scopes into one view.

### User details
Scout collects some data when the user first logs in like name and location. To make this data collection transparent, it should be shown on this page.



## Cases
Cases displays the list of open (?) cases for any particular institute. Each item links to the detailed view for that case. A quick link to get straight to the list of all variants is also displayed. To help users know which cases have recently been added/updated, a "last updated" date is also displayed.


## Case
This is the detailed view of one individual case.

### User stories
1. The user has looked through the clinical variants without finding anything. She visits the case page and requests to have the research list opened. She is presented with a confirmation screen that explains that she is reponsible to have acquired an informed consent. When clicking confirm/agree 1. an email is sent to the administrators, 2. the case is updated with a flag in the database, 3. a new event is logged to the case specific activity feed.

2. The user easily find and clicks on the variants link and is taken directly to the list of variants for the current case.

3. The user reads through the manually curated wiki-style briefing report about the current case. She is quickly caught up on the case.

4. A user haven't visisted the case for a while. She scrolls through the activity feed and finds out that two coworkers have investigated the case since then and added comments mentioning two of the related variants. She finds the topic interesting and decides to contribute a commen of her own into the case feed.

> How should we handle comments on different levels? Does a comment on a variant generate an event in the case log of does it show up in two places?
> How are we going to handle tagging comments as "finding", "action", "conclusion"? Perhaps we should just stick with something more general; tags + category etc.

5. A user has made and verified a new discovery about the disease causing variant. She visits the variant page and marks it as disease causing. When she returns to the case page, the variant is clearly filled in as the disease causing variant and a new button is activated asking if the case is solved.

> I'm still working on the wording for that last story.
