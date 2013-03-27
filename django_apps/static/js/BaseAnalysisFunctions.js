var request_method = "GET";

function getValue(child, dataObj) {
	var myvalue = {};
	if(child.is(":input")) {
    	if(child.attr("type") == "text" || child.attr("type") == "textarea"){
			//dataObj[child.attr("id") ] = escape(jQuery.trim(child.val()));
			dataObj[child.attr("id") ] = jQuery.trim(child.val());
			return;
		}
		else if(child.attr("type") == "radio" || child.attr("type") == "checkbox"){
			dataObj[child.attr("id") ] = child.is(":checked") ;
			return;
		}
		else if(child.is("select")){
			//dataObj[child.attr("id")] = escape(jQuery.trim(child.val()));
			dataObj[child.attr("id")] = jQuery.trim(child.val());
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

function objToArray(obj, keepNull){
	var myArray = []
	for(var key in obj) {
    	if(obj.hasOwnProperty(key))
            if(obj[key] != "" || keepNull)
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

function collectRequestData(){
	dataObj = {}
	walk(jQuery("#users_html").children(), dataObj);

	return dataObj;
}

function checkRequestData(requestData) {
	/* not implemented, its up to the user */
}

function changeRequestData(requestData){
	/* not implemented, its up to the user, in case you want to change the collected data */
}

function sendRequest(){
	/* this func can be overriden by the user in order to have manually collected
	his request data */
	var requestData = collectRequestData();

	if(requestData == null){
		alert("collectRequestData method must return a javascript object!");
		return;
	}
	
	requestData["options"] = getSelectedChilds("options").join(",");
	requestData["versions"] = getSelectedChilds("versions").join(",");
	requestData["platforms"] = getSelectedChilds("platforms").join(",");
	requestData["hosts"] = getSelectedChilds("hosts").join(",");	
	
	/* here is the errors checking, the errors can be a list
	 with the problematic fields or an object with the format :
	problematic field : cause of problem, 
	also before that call the changeRequestData in order to change 
	the request data if its needed */
	changeRequestData(requestData);
	var errors = checkRequestData(requestData);
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

    jQuery("#results").mask("Requesting...");
    jQuery("#users_plus_filter").mask("Requesting...")
	/* requestUrl be will provided from the base analysis template  */
	if (request_method == "GET"){
		
		var requestDataArray = objToArray(requestData,true);
		$("#results").load(requestUrl+"?"+requestDataArray.join("&"), function(){
            $("#users_plus_filter").unmask();
        });
	}
	else if(request_method == "POST"){
		jQuery("#results").load(requestUrl, requestData, function(){
            jQuery("#users_plus_filter").unmask();
        });
	}
	else{
		alert("Invalid request method, request_method variable must be POST or GET , not "+request_method+" !");
	}
	return;
}

function showHide( button_id, box_id )
{
     jQuery(document).ready(function() {
		// check visibility
		if (jQuery("#"+box_id).is(":hidden")) {
			// it's hidden - show it
				jQuery("#"+box_id).slideDown("slow");
				jQuery("#"+button_id).find('span').removeClass('ui-icon-plusthick');
				jQuery("#"+button_id).find('span').addClass('ui-icon-minusthick');
		} else {
			// it's not hidden - slide it down
				jQuery("#"+box_id).slideUp("slow");
				jQuery("#"+button_id).find('span').removeClass('ui-icon-minusthick');
				jQuery("#"+button_id).find('span').addClass('ui-icon-plusthick');
			}
		});
}

function CheckBoxClear(id){
    jQuery('#'+id+' li label :checked').each(function () {
            jQuery(this).removeAttr('checked');
      });
}

function getSelectedChilds(id){
	var sdValues = [];
    jQuery('#'+id+' li label :checked').each(function () {
            sdValues.push(jQuery(this).attr('value'));
      });
	return sdValues;
}

function getBookmarkUrl(){
    var requestData = collectRequestData();

	/* its up to the user if he wants to implement this function
	in case he wants to change any data in the requestData object*/
	changeRequestData(requestData);

	if(requestData == null){
		alert("collectRequestData method must return a javascript object!");
		return;
	}
	
	requestData["options"] = getSelectedChilds("options").join(",");
	requestData["versions"] = getSelectedChilds("versions").join(",");
	requestData["platforms"] = getSelectedChilds("platforms").join(",");
	requestData["hosts"] = getSelectedChilds("hosts").join(",");

    var requestDataArray = objToArray(requestData,false);

    return requestDataArray.join("&");
}
