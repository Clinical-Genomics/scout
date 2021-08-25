/* exported populateCytobands */
function populateCytobands(cytobands){
  var chromPosPattern = new RegExp("^(?:chr)?([1-9]|1[0-9]|2[0-2]|X|Y|MT)$");
  var chrom = document.forms["filters_form"].elements["chrom"].value;
  var chromPos = "";
  if (typeof document.forms["filters_form"].elements["chrom_pos"] !== "undefined") {
  	chromPos=document.forms["filters_form"].elements["chrom_pos"].value;
	}

  var chromosome = "";
  console.log("Populate cytobands")
  var matchedChrName = chromPos.match(chromPosPattern)
  if(chrom==="" && chromPos===""){
    startElem.value = "";
    endElem.value = "";
    return //only reset cytoband select element
  // Set the selected chromosome name
  } else if (chrom !== "" && matchedChrName !== null){
    chromosome = matchedChrName[1]
  } else if (chrom === "" && matchedChrName !== null){
    chromosome = matchedChrName[1]
  } else if (chrom == "" && matchedChrName == null) {
    return
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

function validateChromPos(){
  // Validate Chromosome position form
  //Expected format: <chr number>:<start>-<end>[+-]?<padding>
  var chrPosPattern = "^(?:chr)?([1-9]|1[0-9]|2[0-2]|X|Y|MT)(?::([0-9]+)-([0-9]+)([+-]{1}[0-9]+)?)?$";
  var chromoPosField = document.forms["filters_form"].elements["chrom_pos"]
  if (chromoPosField && chromoPosField.vaLue) {
    var chrom_pos = chromoPosField.value.replaceAll(',', '')
    if (!RegExp(chrPosPattern).test(chrom_pos)) {
      alert("Invalid format of chromosome position, expected format <chr number>:<start>-<end>[+-]?<padding>");
      return false;
    }
    var chromPosMatch  = chrom_pos.match(chrPosPattern);
    var start = chromPosMatch[2];
    var end = chromPosMatch[3];
    var padding = chromPosMatch[5];
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
}

/* exported validateForm */
// ValidateForm()
// Control user input fields (start, end) in variant filter.
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
  validateChromPos();
  // Avoid page spinner being stuck on Filter and export variants option
  $(window).unbind('beforeunload');
  return true;
}

/* exported initSearchConstraints */
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

/* exported enableDismiss */
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
  if (selectedOptions & checkedVars) {
    btnElem.disabled = false;
  }
  else{
    btnElem.disabled = true;
  }
}

/* exported eraseChromPosString() */
function eraseChromPosString() {
  // Erase content of chrom_pos field
  document.forms["filters_form"].elements["chrom_pos"].value = "";
}


/* exported updateCoordinateFields */
// Link chromosome position input field with chromosome and cytoband dropdowns.
// Changes to chrom and cytoband dropdowns are reflected in chrom_pos input
// Changes in chrom_pos input are reflected in chrom, start and end fields
function updateCoordinateFields(element) {
  var chrom = document.forms["filters_form"].elements["chrom"];
  var chromPos = document.forms["filters_form"].elements["chrom_pos"];
  var chromPosPattern = "^(?:chr)?([1-9]|1[0-9]|2[0-2]|X|Y|MT)(?::([0-9]+)-([0-9]+)([+-]{1})?([0-9]+)?)?$";
  // parse chromosome position info
  var chrName, startPos, endPos, sign, padding;
  try {
    [_, chrName, startPos, endPos, sign, padding] = chromPos.value.replaceAll(',', '').match(chromPosPattern);
    console.log(`Parsing ChrPos: ${chrName}, coord: ${startPos}-${endPos}, padding: ${sign}${padding}`)
  } catch (err) {
    console.log('ChrPos empty')
  }
  // update elements
  if (element === chrom) {
    // if alterations in chromosome input field triggered the event
    chromPos.value = element.selectedOptions[0].value;
  } else if (element === chromPos && chrName == null) {
    console.log(`ChrPos regexp not matching ${chromPos.value}`)
		chrom.querySelector(`[value=""]`).selected = true;
  } else {
		console.log(chrName)
		chrom.querySelector(`[value="${chrName}"]`).selected = true;
		// set default padding and sign
		padding = padding != null ? padding : 0
		sign = sign != null ? sign : '+'
		// Update start and end input fields
		if (startPos != null) {
			// invert sign expand before starting position
			var newStartPos = eval(`${startPos} ${sign == '+' ? '-' : '+' } ${padding}`);
			newStartPos = newStartPos < 0 ? 0 : newStartPos
			document.forms["filters_form"].elements["start"].value = newStartPos;
		}
		if (endPos != null) {
			var newEndPos = eval(`${endPos} ${sign} ${padding}`);
			newEndPos = newEndPos < 0 ? 0 : newEndPos
			document.forms["filters_form"].elements["end"].value = newEndPos;
		}
	}
}
