var searchTerm = document.getElementById('search_term');
var sel = document.getElementById('search_type');

var selectHelper = {
  "case:": "example:18201",
  "exact_pheno:": "example:HP:0001166",
  "synopsis:" : "example:epilepsy",
  "panel:" : "example:NMD",
  "status:": "example:active",
  "pheno_group:" : "example:HP:0001166",
  "cohort:" : "example:pedhep",
  "similar_case:" : "example:18201",
  "similar_pheno:" : "example:HP:0001166,HP:0001250,..",
  "pinned:": "example:POT1",
  "causative:": "example:POT1",
  "user:": "example:Kent",
};

document.getElementById("search_type").onchange = function() {
  searchTerm.placeholder=selectHelper[sel.value];
  searchTerm.value="";
};

$(function () {
  $('[data-toggle="tooltip"]').tooltip();
  $('table').stickyTableHeaders({
    fixedOffset: $(".navbar-fixed-top")
  });
});

function updateArgs(caseGroup, sortItem, sortOrder) {
  sort_items = ['sort=status', 'sort=analysis_date', 'sort=track', 'order=asc', 'order=desc'];
  //modifying the sorting of cases
  let searchList = window.location.search.split('&');
  if(!searchList[0]){
    //fix url if sorting is the only param
    searchList[0] = '?';
  }
  //remove all sort params
  searchList = searchList.filter(f => !sort_items.includes(f))
  //add specific sort param
  searchList.push(sortItem);
  searchList.push("order="+sortOrder)

  sort_link = document.getElementById( caseGroup.concat('_',sortItem.split('=')[1]));
  const url = window.location.href.split('?')[0].concat(searchList.join('&'));
  sort_link.href = url;
  //submit link
  sort_link.submit();
}
