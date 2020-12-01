function populateCytobands(cytobands){
  var chrom = document.forms["filters_form"].elements["chrom"].value;
  if(chrom===""){
    startElem.value = "";
    endElem.value = "";
    return //only reset cytoband select element
  }

  var chrom_cytobands = cytobands[chrom]["cytobands"]; // chromosome-specific cytobands

  for (elem of [cytoStart, cytoEnd]) {
    if (elem.options.length > 0){
      elem.options.length = 0; //remove previous select options
    }
    var emptyStart = document.createElement("option");
    emptyStart.textContent = "";
    emptyStart.value = "";
    elem.appendChild(emptyStart); //Add an empty (blank) option to the select
  }

  for(var i = 0; i < chrom_cytobands.length; i++) {
    var opt = chrom_cytobands[i]

    // populate the cytoband start select
    var interval = ["(start:",opt["start"], ")"].join("");
    var optionText = [ chrom, opt["band"], interval ].join(" ");

    // populate the cytoband start select
    var el = document.createElement("option");
    el.textContent = optionText;
    el.value = opt["start"];
    if(startElem.value === el.value){
      el.selected = true;
    }
    cytoStart.appendChild(el);

    var interval = ["(end:",opt["stop"], ")"].join("")
    var optionText = [ chrom, opt["band"], interval ].join(" ");

    var el = document.createElement("option");
    el.textContent = optionText;
    el.value = opt["stop"];
    if(endElem.value === el.value){
      el.selected = true;
    }
    cytoEnd.appendChild(el);
  }
}
// ValidateForm()
// Controll user input fields (start, end) in varaint filter.
//
function validateForm(){
    var start = document.forms["filters_form"].elements["start"].value
    var end = document.forms["filters_form"].elements["end"].value
    if(start || end){
        if(!chrom){
            alert("Chromosome field is required");
            return false;
        }
        else if( !start || !end){
            alert("Both start and end coordinates are required");
            return false;
        }
        else if( (isNaN(start) || isNaN(end)) || Number(end)<Number(start) ){
            alert("Coordinate field not valid");
            return false;
        }
    }
    return true;
}

// syncSearchConstraints(selectorId:HTML-selector, textId:HTML-textfield)
//
// Initialize and synchronize 'startelem' and 'cyto_start', used for setting
// contrsaints when searching variants in cytoband.
function initSearchConstraints(selectorId, textId){
    console.log("init cytoband search: selector and text")
    selectorId.addEventListener("change", function() {
        if(selectorId.options[selectorId.selectedIndex].value === ""){
            textId.value = "";
            return
        }
        // populate textfield
        textId.value = selectorId.options[selectorId.selectedIndex].value
    });
}

function enableDismiss(){
  // before enabling the variant dismiss button
  var selectElem = document.getElementById("dismiss_choices");
  // make sure that user selects at least one dismiss reason
  var selectedOptions = false;
  for (var i = 0; i < selectElem.length; i++) {
      if (selectElem.options[i].selected){
        selectedOptions = true;
        break;
      }
  }
  // make sure that at least one checkbox corresponding to a variant is checked
  var variantCheckboxes = document.getElementsByName("dismiss");
  var checkedVars=false
  for (var i = 0; i < variantCheckboxes.length; i++) {
      if (variantCheckboxes[i].checked){
        checkedVars = true;
        break;
      }
  }
  var btnElem = document.getElementById("dismiss_submit");
  if (selectedOptions & checkedVars) {
    btnElem.disabled = false;
  }
  else{
    btnElem.disabled = true;
  }
}
