/**
 * This function fetches an image from disk and displays it in a specified div
 * @param {string} imageUrl - The URL of the image to fetch
 * @param {string} divId - The ID of the div to display the image in
 */
  function fetchAndDisplayImage(imageUrl, divId, width=none, height=none) {
		fetch(imageUrl)
		 .then(response => response.blob())
		 .then(blob => {
				 const img = document.createElement("img");
				 img.src = URL.createObjectURL(blob);
				 if (width) {
				 	img.style.width = width+'px';
				 }
				 if (height) {
				 	img.style.height = height+'px';
				 }
				 // Display the image in the specified div
				 const div = document.getElementById(divId);
				 div.appendChild(img);
		})
		.catch(error => console.error(error));
}
