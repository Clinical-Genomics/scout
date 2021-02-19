//
// Toggle visability and disabled status of inputs for individuals table
// 
function toggleIndividualsInput () {
	const indTable = document.querySelector("#individuals-table");
	// Toggle buttons and input fields
	var indTblSampleSelect = indTable.querySelectorAll('.sample-selection'),
		indTblButtons = indTable.querySelectorAll('button'),
		indTblAge = indTable.querySelectorAll('.age-selection'),
		indTblTissueSelect = indTable.querySelectorAll('#tissue-selection'),
		indTblSexSelect = indTable.querySelectorAll('.sex-selector'),
		indTblSexDisplay = indTable.querySelectorAll('.sex-display'),
		indTblPhenotypeDisplay = indTable.querySelectorAll('.phenotype-display'),
		indTblPhenotypeSelect = indTable.querySelectorAll('.phenotype-selector');

	for (i = 0; i < indTblButtons.length; i++ ) {
		// toggle display sample selection
		indTblSampleSelect[i].toggleAttribute('hidden');
		// toggle disability of input fileds
		indTblButtons[i].toggleAttribute('disabled');
		indTblAge[i].toggleAttribute('disabled');
		indTblTissueSelect[i].toggleAttribute('disabled');
		// Select sex
		indTblSexSelect[i].toggleAttribute('hidden');
		indTblSexDisplay[i].toggleAttribute('hidden');
		// toggle input for phenotype
		indTblPhenotypeDisplay[i].toggleAttribute('hidden');
		indTblPhenotypeSelect[i].toggleAttribute('hidden');
	}
}

//
// editMetadata mode
// - disables save button, age and tissue
// - replaces sex with dropdown menues
function toggleEditMetadata(){
	const editButton = document.querySelector('#edit-case-metadata');
	editButton.toggleAttribute('hidden');
	document.querySelector("#toggle-case-rerun").toggleAttribute('hidden');
	document.querySelector("#edit-case-metadata-reset").toggleAttribute('hidden');
	toggleIndividualsInput();  // toggle table fields
}


//
// get edited pedigree data
function getEditedPedigreeData() {
	console.log('Get pedigree data')
	// translation tables
	const sex_tr = {'unknown': 0, 'male': 1, 'female': 2}
	const phenotype_tr = {'unknown': 0, 'unaffected': 1, 'affected': 2}

	const indTable = document.querySelector("#individuals-table > tbody");
	let postData = [];
	// serialize data into json
	for (i = 0; i < indTable.rows.length; i++) {
		let row = indTable.rows[i];
		const sampleIdCheck = row.querySelector("input[type='checkbox']");
		if ( sampleIdCheck.checked ) {
			const selectedSex = row.querySelector('select.sex-selector').selectedOptions[0].value;
			const selectedPhenotype = row.querySelector('select.phenotype-selector').selectedOptions[0].value;
			postData.push({'sample_id': sampleIdCheck.labels[0].innerText,
						   'sex': sex_tr[selectedSex],
						   'phenotype': phenotype_tr[selectedPhenotype],
						  });
		}
	}
	console.log(postData)
	return postData;
}

//
// toggle a reanalysis with an updated pedigree
function forwardPedigreeData() {
	document.querySelector("input#reanalysis-data-container").value = JSON.stringify(getEditedPedigreeData());
	console.log('Setting data to modal')
}
