var searchTerm = document.getElementById('search_term');
var sel = document.getElementById('search_type');

var selectHelper = {
  "Case or individual name": {
      "placeholder" : "example:18201",
      "prefix": "case:"
  },
  "HPO term": {
      "placeholder" : "HP:0001166",
      "prefix" : "exact_pheno:"
  },
  "Search synopsis" : {
      "placeholder" : "example:epilepsy",
      "prefix" : "synopsis:"
  },
  "Gene panel" : {
      "placeholder" : "example:NMD",
      "prefix" : "panel:"
  },
  "Case status": {
      "placeholder" : "example:active",
      "prefix" : "status:"
  },
  "Phenotype group" : {
      "placeholder" : "HP:0001166",
      "prefix" : "pheno_group:"
  },
  "Patient cohort" : {
    "placeholder" : "pedhep",
    "prefix" : "cohort:"
  },
  "Similar case" : {
    "placeholder" : "18201",
    "prefix" : "similar_case:"
  },
  "Similar phenotype" : {
    "placeholder" : "example:HP:0001166,HP:0001250,..",
    "prefix" : "similar_pheno:"
  },
  "Pinned gene": {
    "placeholder" : "example:POT1",
    "prefix" : "pinned:"
  },
  "Causative gene": {
    "placeholder" : "example:POT1",
    "prefix" : "causative:"
  },
  "Assigned user": {
    "placeholder" : "example:Kent",
    "prefix" : "user:"
  }
};

$(document).ready(function(){
  searchTerm.placeholder=selectHelper[sel.value]["placeholder"];
});

document.getElementById("search_type").onchange = function() {
  // modify placeholder of text input according to the type of search
  searchTerm.placeholder=selectHelper[sel.value]["placeholder"];
  searchTerm.value="";
};

function appendSearchSuffix(){
  // adds a suffix to the search term to help adapter to execute right query
  searchTerm.value=selectHelper[sel.value]["prefix"]+String(searchTerm.value);
}

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
