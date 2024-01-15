
function generateDiseaseTable(data, id) {
    const table = document.getElementById(id)
    const row = table.querySelector("#diagnosis-row")
    const tbody = table.querySelector("tbody")

    //Create a table row for each diagnosis and append to the table
    data.forEach(item => {
        const newRow = generateDiseaseTableRow(item, row)
        tbody.append(newRow)
    })

    //Replace visible content so diagnosis-table ius displayed
    row.remove()
    document.querySelector("#spinner-container").remove()
    table.classList.remove("invisible")
}

function generateDiseaseTableRow(disease, rowTemplate) {

    const { disease_id, disease_nr, description, inheritance, genes, hpo_terms } = disease
    let newNode = rowTemplate.cloneNode(true)
    newNode.removeAttribute("id")

    //Add diagnosis links
    let externalLinkElement = newNode.querySelector("#external-link")
    externalLinkElement.setAttribute("href", `http://omim.org/entry/${disease_nr}`)
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

        inheritanceContainerElement .textContent = "-"
    }

    //Add Genes
    let genesElement = newNode.querySelector("#gene-link")
    let genesContainerElement = newNode.querySelector("#genes-container")
    if (genes.length > 0) {
        genes.forEach(element => {
            let newGenes = genesElement.cloneNode()
            newGenes.removeAttribute("id")
            let internalbaseurl = newGenes.getAttribute("href")
            newGenes.setAttribute("href", internalbaseurl.slice(0, -1) + element)
            newGenes.textContent = element
            genesContainerElement.append(newGenes)
        });
    } else {
        genesContainerElement.querySelector("span").remove()
        genesContainerElement.textContent = "-"
    }

    //Add hpo_terms
    let hpoElement = newNode.querySelector("#hpo-link")
    let hpoContainerElement = newNode.querySelector("#hpo-container")
    //let span = hpoContainerElement.querySelector("span")
    if (hpo_terms.length > 0) {
        hpo_terms.forEach(element => {
            let newHpoLink = hpoElement.cloneNode()
            newHpoLink.removeAttribute("id")
            let internalbaseurl = newHpoLink.getAttribute("href")
            newHpoLink.setAttribute("href", internalbaseurl + element)
            newHpoLink.textContent = element
            hpoContainerElement.append(newHpoLink)
        });
    } else {
        hpoContainerElement.querySelector("span").remove()
        hpoContainerElement.textContent = "-"
    }

    return newNode
}
function displayErrorMsg(msg, id) {
    //Replace spinner with error message
    const spinnerContainer = document.querySelector(`#${id}`)
    spinnerContainer.textContent = msg
}

function initialiseTable(data) {
    //Diagnosis table is turned into a DataTable with copy-buttons, pagination and search bar
    $('#diagnoses_table').DataTable({
        data: data,
        paging: true,
        dom: 'fBrtip',
        buttons: [
            {
                extend: 'excelHtml5',
                title: 'omim_terms'
            },
            'copyHtml5'
        ]
    });
    document.querySelector("#diagnoses_table_filter").classList.add("text-start")
		document.querySelector("#diagnoses_table_wrapper > .dt-buttons").classList.add("m-2")
}

async function loadDiseases() {
    document.getElementById("load-button").remove()
    $('#load-container').html(
        `<div id="spinner-container" >
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden"></span>
            </div>
            Loading all diagnoses, this might take some time...
        </div>`);

    console.log('click')
    const baseUrl = window.location.origin
    console.log(baseUrl)

    try {
        //Fetch data and create table from results
        const response = await fetch(`${'http://localhost:5000'}/api/v1/diagnoses`)
        if (!response.ok) {
            throw new Error('Failed to fetch')
        }
        const { terms } = await response.json()


        generateDiseaseTable(terms, "diagnoses_table")
        initialiseTable()

    } catch (error) {
    console.log(error)

        if (error.toString().includes('Failed to fetch')) {
            //Replace loading spinner with error message if loading fails
            displayErrorMsg("Diagnoses could not be loaded, please try again later", "spinner-container")
        }
    }
}
