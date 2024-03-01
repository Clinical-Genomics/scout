async function loadDiseases() {
    //Add spinner to show loading is in progress
    $('#load-container').html(
        `<div id="spinner-container" class="d-flex align-items-center">
            <div class="spinner-border text-primary m-3" role="status">
                <span class="visually-hidden"></span>
            </div>
           Loading matching diagnoses, this might take some time...
        </div>`);

    //Get input value to use in query
    const query = document.querySelector("#search-disease-term").value

    const baseUrl = window.location.origin

    //If it's not the first search, remove the previously generated table
    removePreviousTableIfPresent()
    try {
        //Fetch data and generate table with results
        const response = await fetch(`${baseUrl}/api/v1/diagnoses?query=${query}`)
        if (!response.ok) {
            throw new Error('Failed to fetch')
        }
        const { terms } = await response.json()

        generateDiseaseTable(terms, "diagnoses_table")
        initialiseTable()

    } catch (error) {

        if (error.toString().includes('Failed to fetch')) {
            //Replace loading spinner with error message if loading fails
            displayErrorMsg("Diagnoses could not be loaded, please try again", "spinner-container")
        }
    }
}

function generateDiseaseTable(data, id) {
    const table = document.getElementById(id)
    const row = document.querySelector("#diagnosis-row")
    const tbody = table.querySelector(`#${id} tbody`)

    //Create a table row for each diagnosis and append to the table
    data.forEach(item => {
        const newRow = generateDiseaseTableRow(item, row)
        tbody.append(newRow)
    })

    //Remove spinner and show the table if hidden
    document.querySelector("#spinner-container").remove()
    table.removeAttribute("style")
}

function generateDiseaseTableRow(disease, rowTemplate) {

    const { disease_id, disease_nr, description, inheritance, genes, hpo_terms, source } = disease
    let newNode = rowTemplate.cloneNode(true)
    newNode.removeAttribute("id")

    //Add diagnosis links
    let externalLinkElement = newNode.querySelector("#external-link")

    externalLinkElement.setAttribute("href", getExternalLink(source, disease_nr))
    externalLinkElement.textContent = `${disease_id}`
    let internalLinkElement = newNode.querySelector("#internal-link")
    let internalbaseurl = internalLinkElement.getAttribute("href")
    internalLinkElement.setAttribute("href", internalbaseurl + disease_id)

    //Add descritption
    let descriptionElement = newNode.querySelector("#description")
    descriptionElement.textContent = `${description}`

    //Add inheritance
    let inheritanceElement = newNode.querySelector("#inheritance")
    let inheritanceContainerElement = newNode.querySelector("#inheritance-container")
    if (inheritance.length > 0) {
        inheritance.forEach(element => {
            let newInheritance = inheritanceElement.cloneNode()
            newInheritance.removeAttribute("id")
            newInheritance.textContent = element
            inheritanceContainerElement.append(newInheritance)
        });
    } else {
        inheritanceContainerElement.textContent = "-"
    }

    //Add Genes
    addHpoOrGeneLinks(newNode, "gene", genes)

    //Add hpo_terms
    addHpoOrGeneLinks(newNode, "hpo", hpo_terms)

    return newNode
}

function displayErrorMsg(msg, id) {
    //Replace spinner with error message
    const spinnerContainer = document.querySelector(`#${id}`)
    spinnerContainer.textContent = msg
}

function addHpoOrGeneLinks(parentNode, target, data) {
    let linkElement = parentNode.querySelector(`#${target}-link`)
    let containerElement = parentNode.querySelector(`#${target}-container`)

    if (data.length > 0) {
        data.forEach(item => {
        		let id= item.hgnc_id || item
        		let symbol = item.hgnc_symbol || item
            let newLinkElement = linkElement.cloneNode()
            newLinkElement.removeAttribute("id")
            let baseurl = newLinkElement.getAttribute("href")
            newLinkElement.setAttribute("href", baseurl + id)
            newLinkElement.textContent = symbol
            containerElement.append(newLinkElement)
        });
    } else {
        containerElement.querySelector("span").remove()
        containerElement.textContent = "-"
    }
}

function getExternalLink(source, disease_nr) {
    let link = ''
    if (source == "OMIM") {
        link = `http://omim.org/entry/${disease_nr}`
    } else if (source == "ORPHA") {
        link = `http://www.orpha.net/consor/cgi-bin/OC_Exp.php?lng=en&Expert=${disease_nr}`
    }
    return link
}

function initialiseTable(data) {
    //Diagnosis table is turned into a DataTable with copy-buttons, pagination and search bar
    $('#diagnoses_table').DataTable({
        data: data,
        paging: true,
        dom: 'Brtip',
        buttons: [
            {
                extend: 'excelHtml5',
                title: 'disease_term_search_result'
            },
            'copyHtml5'
        ]
    });
    document.querySelector("#diagnoses_table_wrapper > .dt-buttons").classList.add("mb-2")
}

function removePreviousTableIfPresent() {
    if ($.fn.dataTable.isDataTable('#diagnoses_table')) {$('#diagnoses_table').DataTable().clear().destroy()}
}
