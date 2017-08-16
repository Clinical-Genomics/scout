## What's new in 3.3?

_Posted: 2 Aug 2017_

Hey Scout-users! It's time for a new update and with quite a few features this time 😃

### ACMG classifications!

The flagship feature addition is the new ACMG classification interface. You can get to it from any variant. It will take you first to a page where you fill in evidence which Scout uses to calculate a classification - you can, however, override this later! We store a history of all classifications for a variant if it's updated later.

Please try it out and get back to us with your feedback!

### New users view

We've added a new views for displaying all users of Scout. You can see name, email, and which institutes they belong to if you need to contact someone. We also introduced a "rank" based on how much you interact with Scout! Check out how you are doing here: [Scout Users](https://clinical-db.scilifelab.se:8083/users).

### More new features:

1. Cases are now listed by status in separate groups - only the latest 100 cases are listed!
2. Upload of gene panel export
3. Dynamic gene panel is back! You can now upload a list of HGNC symbols to do a temporary search
4. Scout will now display exon as well as intron number in the Sanger email
5. You can now filter variants on local observations in the SNV view and they will show up in the popup
6. Scout will now display if a variant is in the PAR region or not
7. You can now update the default gene panels directly in Scout - no need to rerun!
8. We've added labels to the variant tags according to proposed example from CMMS
9. If variant is in an autozygocity block it will now be displayed

## Bug fixes

1. A warning is now displayed is you search for a gene symbol that doesn't exist in Scout
2. When filtering on frequencies, Scout now handles input as "0,04" and "0.04"
3. We will now use coordinates instead of gene identifier when looking for overlapping SV/SNV variants
4. Scout now correctly displays a notice if a variant has been commented on
5. CLINSIG annotations are now properly displayed!
6. We've fixed display of expected inheritance model on variant page

## Future updates

We have prepared additional features which will not immediately show up in Scout but might require e.g. an update to MIP.

1. New cancer view: we've added rudimentary support for display cancer variants in Scout as a separate view much like the SV view.
2. We've added support for displaying information from Peddy such as confirmed parenthood, sex, and predicted ancestry

--------------------------------

Hope you've had a great summer!
