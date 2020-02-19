function httpGetLoadBam(hgvs, bamFile) {
	var xmlHttp = null;
	xmlHttp = new XMLHttpRequest();
	var bamXmlHttp = null;
	bamXmlHttp = new XMLHttpRequest();

	if (xmlHttp) {
		xmlHttp.open( "GET", "http://localhost:10000/show?request="+hgvs+"&synchronous=true", true );
		xmlHttp.send(null);
		xmlHttp.onreadystatechange=function() {
			if (xmlHttp.readyState==4) {
				bamXmlHttp.open( "GET", "http://localhost:10000/show?request=BAM%3C"+bamFile, true );
				bamXmlHttp.send(null);
			}
		}
	}
}
