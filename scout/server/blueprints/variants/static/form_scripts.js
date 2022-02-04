/* exported updatedChromSelOptions */
function updatedChromSelOptions() { // eslint-disable-line no-unused-vars
	console.log("updatedChromSelOptions")

  chrom = getSelectedChromosomes()
	if (chrom.length != 1) {
		for (elem of [cytoStart, cytoEnd]) {
			elem.options.length = 0; // remove previous cytoband select options
		}
		// clear start and end values
		startElem.value = null
		endElem.value = null

		return
	}
	return
}

function getSelectedChromosomes() {
	var chrom_select = document.forms["filters_form"].elements["chrom"];

	var chrom = [];

 	// return selected chrs; will never contain All option
  for (var i=0; i < chrom_select.selectedOptions.length; i++) {
		chrom.push(chrom_select.selectedOptions[i].value)
	}
  return chrom
}

/* exported populateCytobands */
function populateCytobands(cytobands) {
  console.log("Populate cytobands")

	var chromosome = "";
	chrom = getSelectedChromosomes();
	if (chrom.length != 1) {
		console.log("More than one chr selected")
		return
	}
	chromosome = chrom[0]

	console.log("Add chr " + chromosome + "("+ typeof (chromosome)+")")
	var chrom_cytobands = cytobands[chromosome]["cytobands"]; // chromosome-specific cytobands

	for (elem of [cytoStart, cytoEnd]) {
		elem.options.length = 0; //remove previous select options

		var emptyStart = document.createElement("option");
		emptyStart.textContent = "";
		emptyStart.value = "";
		elem.appendChild(emptyStart); //Add an empty (blank) option to the select
	}

	for (var i = 0; i < chrom_cytobands.length; i++) {
		var opt = chrom_cytobands[i]

		// populate the cytoband start select
		var interval = ["(start:", opt["start"], ")"].join("");
		var optionText = [chromosome, opt["band"], interval].join(" ");

		// populate the cytoband start select
		var el = document.createElement("option");
		el.textContent = optionText;
		el.value = opt["start"];
		if (startElem.value === el.value) {
			el.selected = true;
		}
		cytoStart.appendChild(el);

		var interval = ["(end:", opt["stop"], ")"].join("")
		var optionText = [chromosome, opt["band"], interval].join(" ");

		var el = document.createElement("option");
		el.textContent = optionText;
		el.value = opt["stop"];
		if (endElem.value === el.value) {
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
    else if (chrom.length > 1) {
    	alert("Start and end coordinates are only applicable with one selected chromosome");
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
// constraints when searching variants in cytoband.
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

/* exported eraseChromPosString */
function eraseChromPosString() {
  // Erase content of chrom_pos field
  document.forms["filters_form"].elements["chrom_pos"].value = "";
}

/* exported updatedChromPosInput */
// Link chromosome position input field with chromosome and cytoband dropdowns.
// Changes in chrom_pos input are reflected in chrom, start and end fields
function updatedChromPosInput() { // eslint-disable-line no-unused-vars
	console.log('Update to chrom pos field detected!')
	var chromSel = document.forms["filters_form"].elements["chrom"];
	var chromPos = document.forms["filters_form"].elements["chrom_pos"];
	var chromPosPattern = "^(?:chr)?([1-9]|1[0-9]|2[0-2]|X|Y|MT)(?::([0-9]+)-([0-9]+)([+-]{1})?([0-9]+)?)?$";
	// parse chromosome position info
	var chrName, startPos, endPos, sign, padding;
	try {
		[_, chrName, startPos, endPos, sign, padding] = chromPos.value.replaceAll(',', '').match(chromPosPattern);
		console.log(`Parsing ChrPos: ${chrName}, coord: ${startPos}-${endPos}, padding: ${sign}${padding}`)
	} catch (err) {
		console.log('ChrPos empty')
		return
	}

	console.log(chrName)
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
	if (chrName != null) {
		// select this chromosome ONLY in chromSel dropdown
  	for (var i = 0; i < chromSel.length; i++) {
  		if (chromSel.options[i].value !== chrName) {
				chromSel.options[i].selected = false;
			} else {
  			chromSel.options[i].selected = true;
			}
		}
	} else {
		console.log(`ChrPos regexp not matching ${chromPos.value} - chrName empty`)
		// select the all chromosomes option ONLY in chromSel dropdown
  	for (var i = 0; i < chromSel.length; i++) {
  		if (chromSel.options[i].value !== "") {
				chromSel.options[i].selected = false;
			} else {
  			chromSel.options[i].selected = true;
			}
		}
	}
}
