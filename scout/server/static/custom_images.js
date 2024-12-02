const imgMaxWidth = window.innerWidth*0.7;
const imgMaxHeight = window.innerHeight*0.7;

function calculateAspectRatioFit(srcWidth, srcHeight, maxWidth, maxHeight) {
    let ratio = Math.min(maxWidth / srcWidth, maxHeight / srcHeight);
    return [srcWidth*ratio, srcHeight*ratio];
}

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
				 if (width > imgMaxWidth || height > imgMaxHeight) {
				 		const resized_pixels = calculateAspectRatioFit(width, height, imgMaxWidth, imgMaxHeight);
				 		width = resized_pixels[0];
				 		height = resized_pixels[1];
				 }
				 if (width) {
				 	img.style.width = width+'px';
				 }
				 if (height) {
				 	img.style.height = height+'px';
				 }
				 // Add the image to a link and add the link to the div
				 const link = document.createElement('a');
				 link.appendChild(img);
				 link.href = img.src;
				 link.setAttribute('target', "_blank");
				 const div = document.getElementById(divId);
				 div.appendChild(link);
		})
		.catch(error => console.error(error));
}
