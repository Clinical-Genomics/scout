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


% Refer to cases.md here
% Refer to variants.md
