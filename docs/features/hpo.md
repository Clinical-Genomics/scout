# HPO phenotypes

For every case you have the opportunity to add related HPO phenotype terms to describe the phenotype of the patient(s). This structured data can then be used in some interesting ways. You access all these features from the case page.

## HPO gene panel

Every HPO term is linked to a set of genes. It it interesting to see which genes that overlap with your phenotype terms. To generate such a list, locate the "HPO panel" button. You can optionally select which terms to include by using the check boxes next to the HPO terms.

By default only genes matching _every_ selected HPO term is returned. This setting can be customized by entering the minimum number of HPO terms a gene is required to overlap.

> The panel is only stored until a user regenerates the panel!

The generated panel will show up just below under "HPO gene panel".

## Phenomizer diseases

The second option is to use the same HPO terms as input to the [Phenomizer][phenomizer] service. This will use you selected phenotypes to look up possible OMIM diseases. You will be presented with all hits on a new page where you can select which diseases to proceed with.

Phenomizer associates a P-value with each disease which tells you something about the likelihood of each disease match. You can also see which genes are associated with every disease in the last column.

When you've made your selection, click "Select" at the bottom of the table. Scout will then store all the associated genes and list them in the "HPO gene panel" list on the "case" page.


[phenomizer]: http://compbio.charite.de/phenomizer/
