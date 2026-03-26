function toggleDiv(divName) {
    let div = document.getElementById(divName);
    if (div.style.display === "none") {
        div.style.display = "block";
    } else {
        div.style.display = "none";
    }
}
