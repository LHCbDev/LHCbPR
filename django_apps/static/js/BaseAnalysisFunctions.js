function getValue(child, dataObj) {
	var myvalue = {};
	if(child.is(":input")) {
    	if(child.attr("type") == "text" || child.attr("type") == "textarea"){
			dataObj[child.attr("id") ] = escape($.trim(child.val()));
			return;
		}
		else if(child.attr("type") == "radio" || child.attr("type") == "checkbox"){
			dataObj[child.attr("id") ] = child.is(":checked") ;
			return;
		}
		else if(child.is("select")){
			dataObj[child.attr("id")] = escape($.trim(child.val()));
			return;
		}
	}
}

function walk(children, dataObj) {
	if (typeof children == "undefined" || children.size() === 0) {
			return;
	}
	children.each(function(){
		var child = $(this);
		if(child.is("select")){
			getValue(child, dataObj);
			return;
		}
		else if (child.children().size() > 0) {
			walk(child.children(), dataObj);
		}
		getValue(child, dataObj);
	});
}

function objToArray(obj){
	var myArray = []
	for(var key in obj) {
    	if(obj.hasOwnProperty(key))
        	myArray.push(key+"="+obj[key]);
	}
	return myArray;
}

function isEmpty(map) {
	for(var key in map) {
		if (map.hasOwnProperty(key)) {
			return false;
		}
	}
	return true;
}

var request_method = "GET";

function collectRequestData(){
	dataObj = {}
	walk($("#users_html").children(), dataObj);

	return dataObj;
}

function checkRequestData(requestData) {
	/* no implemented, its up to the user */
}

function sendRequest(){
	/* this func can be overriden by the user in order to have manually collected
	his request data */
	var requestData = collectRequestData();

	if(requestData == null){
		alert("collectRequestData method must return a javascript object!");
		return;
	}
	
	requestData["options"] = getSelectedChilds("Options").join(",");
	requestData["versions"] = getSelectedChilds("Version").join(",");
	requestData["platforms"] = getSelectedChilds("Platform").join(",");
	requestData["hosts"] = getSelectedChilds("Host").join(",");	
	
	/* here is the errors checking, the errors can be a list
	 with the problematic fields or an object with the format :
	problematic field : cause of problem */
	var errors = checkRequestData(requestData)
	if(errors != null){
		if(errors instanceof Array ){
			if(errors.length != 0){
				var errorStr = "Invalid fields:\n\n";
				for (var i=0;i<errors.length;i++){
					errorStr+= errors[i]+"\n";
				}
				alert(errorStr);
				return;
			}
		}
		else if(!isEmpty(errors)){
			var errorStr = "Invalid fields:\n\n";	
			for(var key in errors) {
    			if(errors.hasOwnProperty(key))
        			errorStr += key+": "+errors[key]+"\n";
			}
			alert(errorStr);
			return
		}
	}

	/* requestUrl be will provided from the base analysis template  */
	if (request_method == "GET"){
		$("#results").mask("Requesting...");
		var requestDataArray = objToArray(requestData);
		$("#results").load(requestUrl+"?"+requestDataArray.join("&"));
	}
	else if(request_method == "POST"){
		$("#results").mask("Requesting...");
		$("#results").load(requestUrl, requestData);
	}
	else{
		alert("Invalid request method, request_method variable must be POST or GET , not "+request_method+" !");
	}
	return;
}

function showHide( button_id, box_id )
{
     $(document).ready(function() {
		// check visibility
		if ($("#"+box_id).is(":hidden")) {
			// it's hidden - show it
				$("#"+box_id).slideDown("slow");
				$("#"+button_id).find('span').removeClass('ui-icon-plusthick');
				$("#"+button_id).find('span').addClass('ui-icon-minusthick');
		} else {
			// it's not hidden - slide it down
				$("#"+box_id).slideUp("slow");
				$("#"+button_id).find('span').removeClass('ui-icon-minusthick');
				$("#"+button_id).find('span').addClass('ui-icon-plusthick');
			}
		});
}

function CheckBoxClear(id){
    $('#'+id+' li label :checked').each(function () {
            $(this).removeAttr('checked');
      });
}

function getSelectedChilds(id){
	var sdValues = [];
    $('#'+id+' li label :checked').each(function () {
            sdValues.push($(this).attr('value'));
      });
	return sdValues;
}
