async function getJson(url) {
    try {
    //Get base url and fetch data
        const baseUrl = window.location.origin
        const response = await fetch(`${baseUrl}${url}`)
        if (!response.ok) {
            throw new Error('Failed to fetch')
        }
        const jsonRes = await response.json()
				let fileName=url.split("/").pop()
				//Create and download file
        download(fileName, jsonRes)
    } catch (error) {
        if (error.toString().includes('Failed to fetch')) {
            console.log(error)
        }
    }
}

//Function creates a file download from an Object
function download(filename, object){
    const json= JSON.stringify(object)
    let downloadLink=document.createElement('a')
    downloadLink.setAttribute('href','data:application/json;charset=utf-8,' + encodeURIComponent(json))
    downloadLink.setAttribute('download', filename)
    downloadLink.style.display='none'
    document.body.appendChild(downloadLink)
    downloadLink.click()
    document.body.removeChild(downloadLink)
}

//Add eventlistener to button for json download of preClinVar response
document.querySelector("#download_clinvar_json").addEventListener("click",(e)=>{
getJson(e.target.value)
})
