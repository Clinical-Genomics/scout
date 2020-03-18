// Check here for documentation : https://www.interactive-biosoftware.com/doc/alamut-visual/2.8/programmatic-access.html

function httpGetLoadBam(region, bamFile) {

	alert(region);
	alert(bamFile);
	/*
	var xmlHttp = null;
	xmlHttp = new XMLHttpRequest();
	var bamXmlHttp = null;
	bamXmlHttp = new XMLHttpRequest();

	if (xmlHttp) {
		xmlHttp.open( "GET", "https://localhost:10000/show?request="+region+"&synchronous=true", true );
		xmlHttp.send(null);
		xmlHttp.onreadystatechange=function() {
			if (xmlHttp.readyState==4) {
				bamXmlHttp.open( "GET", "https://localhost:10000/show?request=BAM%3C"+bamFile, true );
				bamXmlHttp.send(null);
			}
		}
	}
	*/
}
