function populateCytobands(cytobands){
  var chromPosPattern = new RegExp("^([0-9]{1,2}|[X|T|MT]{1,2})");
  var chrom = document.forms["filters_form"].elements["chrom"].value;
  var chromPos = document.forms["filters_form"].elements["chrom_pos"].value;
  var chromosome = "";
  console.log("Populate cytobands")
  if(chrom==="" && chromPos===""){
    startElem.value = "";
    endElem.value = "";
    return //only reset cytoband select element
  // Set the selected chromosome name
  } else if (chrom!=="" && chromPos!==""){
    chromosome = chromPos.match(chromPosPattern)[0];
  } else if (chrom==="" && chromPos!==""){
    chromosome = chromPos.match(chromPosPattern)[0];
  } else {
    chromosome = chrom;
  }
  
  var chrom_cytobands = cytobands[chromosome]["cytobands"]; // chromosome-specific cytobands

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
// Verify the format of Chromosome position
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
    // Validate Chromosome position form
    //Expected format: <chr number>:<start>-<end>[+-]?<padding>
    var chrom_pos = document.forms["filters_form"].elements["chrom_pos"].value.replaceAll(',', '')
    const chromPosPattern = new RegExp("^([0-9]{1,2}|[X|T|MT]{1,2}):([0-9]+)-([0-9]+)([+-]{1}[0-9]+)?$");
    if(chrom_pos) {
        if (!chromPosPattern.test(chrom_pos)) {
            alert("Invalid format of chromosome position, expected format <chr number>:<start>-<end>[+-]?<padding>");
            return false;
        }
        var _, chr, start, end, sign, padding;
        [_, chr, start, end, padding] = chromPosPattern.exec(chrom_pos);
        if (Number(start) < 0 || Number(end) < 0) {
            alert("Invalid coordinates, coordinates must be greater than zero");
            return false;
        } else if (Number(start) > Number(end)) {
            alert("Invalid coordinates, end coordinate must be greater than start");
            return false;
        } else if (Number(padding) < 1) {
            alert("Padding must be greater than zero!")
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
        updateCoordinateFields(event.target)
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


// Update chromosome position
function updateCoordinateFields(element) {
  const chrom = document.forms["filters_form"].elements["chrom"];
  const chromPos = document.forms["filters_form"].elements["chrom_pos"];
  const cytoStart = document.forms["filters_form"].elements["cytoband_start"];
  const cytoEnd = document.forms["filters_form"].elements["cytoband_end"];
  const chromPosPattern = "^([0-9]{1,2}|[X|T|MT]{1,2})(?::([0-9]+)?(?:-([0-9]+)?)?)?";
  // parse chromosome position info
  let chrName, startPos, endPos;
  try {
    [_, chrName, startPos, endPos] = chromPos.value.replaceAll(',', '').match(chromPosPattern);
    console.log(`Parsing ChrPos: ${chrName}, start: ${startPos}-${endPos}`)
  } catch (err) {
    console.log('ChrPos empty')
  }
  // update elements
  if (element === chrom) {
    // if alterations in chromosome input field triggered the event
    chromPos.value = element.selectedOptions[0].value;
  } else if (element === cytoStart) {
    // If the cytoband changed
    chromPos.value = updateChromPos(chrName, cytoStart.value, endPos);
  } else if (element === cytoEnd) {
    // If the cytoband changed
    chromPos.value = updateChromPos(chrName, startPos, cytoEnd.value);
  } else {
    // update start, end input fields
    chrom.querySelector(`[value="${chrName}"]`).toggleAttribute('selected');
    if (startPos != null) {
      document.forms["filters_form"].elements["start"].value = startPos;
    }
    if (endPos != null) {
      document.forms["filters_form"].elements["end"].value = endPos;
    }
  }
}


// Update chromosome position field
function updateChromPos(chrName="", start, end) {
  let results = chrName == null ? "" : chrName;
  if ([start, end].some(pos => pos !== null)){
    start = start == null ? "" : start
    end = end == null ? "" : end
    results = `${results}:${start}-${end}`
  }
  return results
}
