async function loadRegions() {
    //Add spinner to show loading is in progress
    $('#load-container').html(
        `<div id="spinner-container" class="d-flex align-items-center">
            <div class="spinner-border text-primary m-3" role="status">
                <span class="visually-hidden"></span>
            </div>
           Loading regions, this might take some time...
        </div>`);

    //Get input value to use in query
    const query = document.querySelector("#region-query").value

    const baseUrl = window.location.origin

	//If it's not the first search, remove the previously generated table
    removePreviousTableIfPresent()
    try {
        //Fetch data and generate table with results

        const response = await fetch(`${baseUrl}/api/v1/regions?query=${query}&build=${document.querySelector("#build").value}`)
        if (!response.ok) {
            throw new Error('Failed to fetch')
        }
        const { regions } = await response.json()

        generateRegionTable(regions, "regions_table")
        initialiseTable()

    } catch (error) {

        if (error.toString().includes('Failed to fetch')) {
            //Replace loading spinner with error message if loading fails
            displayErrorMsg("Regions could not be loaded, please try again", "spinner-container")
        }
    }
}

function generateRegionTable(data, id) {
    const table = document.getElementById(id)
    const row = document.querySelector("#region-row")
    const tbody = table.querySelector(`#${id} tbody`)

    //Create a table row for each region and append to the table
    data.forEach(item => {
        const newRow = generateRegionTableRow(item, row)
        tbody.append(newRow)
    })

    //Remove spinner and show the table if hidden
    document.querySelector("#spinner-container").remove()
    table.removeAttribute("style")
}

function generateRegionTableRow(region, rowTemplate) {

    const { isca_id, build, chromosome, start, end, display_name, haploinsufficiency, triplosensitivity, source } = region
    let newNode = rowTemplate.cloneNode(true)
    newNode.removeAttribute("isca_id")

    //Add links
    let externalLinkElement = newNode.querySelector("#external-link")

    externalLinkElement.setAttribute("href", getExternalLink(source, isca_id))
    externalLinkElement.textContent = `${isca_id}`
    let internalLinkElement = newNode.querySelector("#internal-link")
    let internalbaseurl = internalLinkElement.getAttribute("href")
    internalLinkElement.setAttribute("href", internalbaseurl + isca_id)

    let displayNameElement = newNode.querySelector("#display-name")
    displayNameElement.textContent = `${display_name}`

		let buildElement = newNode.querySelector("#build-cell")
		buildElement.textContent = `${build}`

    let chromosomeElement = newNode.querySelector("#chromosome")
		chromosomeElement.textContent = `${chromosome}`

		let startElement = newNode.querySelector("#start")
		startElement.textContent = `${start}`

	  let endElement = newNode.querySelector("#end")
		endElement.textContent = `${end}`

		let haploinsufficyElement = newNode.querySelector("#haploinsufficiency")
		haploinsufficyElement.textContent = `${haploinsufficiency}`

		let triplosensitivityElement = newNode.querySelector("#triplosensitivity")
		triplosensitivityElement.textContent = `${triplosensitivity}`

    return newNode
}

function displayErrorMsg(msg, id) {
    //Replace spinner with error message
    const spinnerContainer = document.querySelector(`#${id}`)
    spinnerContainer.textContent = msg
}

function getExternalLink(source, id) {
    let link = ''
    if (source.includes("ISCA")) {
        link = `https://search.clinicalgenome.org/kb/gene-dosage/region/${id}`
    }
    return link
}

function initialiseTable(data) {
    //Region table is turned into a DataTable with copy-buttons, pagination and search bar
    $('#regions_table').DataTable({
        data: data,
        paging: true,
        layout: {
					topStart: 'buttons',
					topEnd: {
							search: {
									placeholder: 'Filter further...'
							}
					}
				},
        buttons: [
            {
                extend: 'excelHtml5',
                title: 'regions_search_result'
            },
            'copyHtml5'
        ]
    });
    document.querySelector("#regions_table_wrapper > .dt-buttons").classList.add("mb-2")
}

function removePreviousTableIfPresent() {
    if ($.fn.dataTable.isDataTable('#regions_table')) {$('#regions_table').DataTable().clear().destroy()}
}
