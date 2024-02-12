async function getJson(url) {
    try {
        const baseUrl = window.location.origin
        console.log(`url: ${baseUrl}${url}`)
        //Fetch data
        const response = await fetch(`${baseUrl}${url}`)
        if (!response.ok) {
            throw new Error('Failed to fetch')
        }
        const jsonRes = await response.json()

				let fileName=url.split("/").pop()

        download(fileName, jsonRes)

    } catch (error) {

        if (error.toString().includes('Failed to fetch')) {
            console.log(error)
        }
    }
}

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

document.querySelector("#download_clinvar_json").addEventListener("click",(e)=>{

getJson(e.target.value)

})




