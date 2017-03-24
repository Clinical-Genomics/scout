function init(){
	//alert("In Init");
}

//
// addIconEventMethod
//
function addIconEventMethod(eventType,method){


	// Initialize the event handlers for all rect and circle elements:
	var rectElements = document.getElementsByTagName("rect");
	for(var i=0;i<rectElements.length;i++){
		if(rectElements[i].id)
			rectElements[i].addEventListener(eventType,method,false);
	}
	var circleElements = document.getElementsByTagName("circle");
	for(var i=0;i<circleElements.length;i++){
		if(circleElements[i].id)
			circleElements[i].addEventListener(eventType,method,false);
	}

	var polylineElements = document.getElementsByTagName("polyline");
	for(var i=0;i<polylineElements.length;i++){
		if(polylineElements[i].id)
			polylineElements[i].addEventListener(eventType,method,false);
	}

}

//
// addLineEventMethod
//
function addLineEventMethod(eventType,matingDropLineMethod){

	// Initialize the event handlers for selected line elements:
	var lineElements = document.getElementsByTagName("line");
	for(var i=0;i<lineElements.length;i++){
		if(lineElements[i].className.baseVal=="mating"){
			lineElements[i].addEventListener(eventType,matingDropLineMethod,false);
		}
	}
}
