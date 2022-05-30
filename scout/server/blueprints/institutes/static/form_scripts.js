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
