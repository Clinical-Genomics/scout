async function fetchDiagnoses(url = null) {
    //fetches all disease_terms
    const base_url = 'http://localhost:5000'
    const myUrl = url || `${base_url}/api/v1/diagnoses`
    try {
        const response = await fetch(myUrl)
        if (!response.ok) {
            throw new Error("Could not fetch diagnoses");
        }
        const data = await response.json()
        const diagnosesArray = data.terms

        return (diagnosesArray)
    } catch (error) {
        console.log(error.message)
        return (error)
    }
}

function generateDiseaseTable(data, id) {
    const table = document.getElementById(id)

    const row = table.querySelector("#diagnosis-row")
    const tbody = table.querySelector("tbody")
    table.classList.remove("d-none")

    data.forEach(item => {
        const newRow = generateAndAddDiseaseTableRow(item, row)
        tbody.append(newRow)
    })

    row.remove()
    //initialiseTable(data)
}
function generateAndAddDiseaseTableRow(disease, rowTemplate) {


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
        let newInheritance = inheritanceElement.cloneNode()
        newInheritance.removeAttribute("id")
        newInheritance.textContent = "-"
        inheritanceContainerElement.append(newInheritance)
    }

    //Add Genes
    let genesElement = newNode.querySelector("#geneLink")
    let genesContainerElement = newNode.querySelector("#genes-container")
    if (genes.length > 0) {
        genes.forEach(element => {
            let newGenes = genesElement.cloneNode()
            newGenes.removeAttribute("id")
            let internalbaseurl = newGenes.getAttribute("href")
            newGenes.setAttribute("href", internalbaseurl.slice(0,-1) + element)
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
    let span= hpoContainerElement.querySelector("span")
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
        hpoContainerElement.textContent = "-"
    }
    return newNode
}
function displayErrorMsg(msg, id) {
    const table = document.getElementById(id)
    while (table.firstChild) {
        table.removeChild(table.lastChild);
    }
    let msgElement = document.createElement('td')
    msgElement.textContent = msg
    table.append(msgElement)
    table.destroy()


}

function initialiseTable(data) {
	console.log("Istarted initialisxing")
    $('#diagnoses_table').DataTable( {
        data:data,
        paging: true,
        dom: 'fBrtip',
        buttons: [
          {
            extend: 'excelHtml5',
            title: 'omim_terms'
          },
          'copyHtml5'
        ]
    } );
}

document.addEventListener("DOMContentLoaded", async function () {
//Runs after dom content has been loaded
    try {
        const data = await fetchDiagnoses(null)

        generateDiseaseTable(data, "diagnoses_table")

    } catch (error) {
        console.log(error)

        displayErrorMsg(error.message, "diagnoses_table")
    } finally{
    	initialiseTable()
    }

})

