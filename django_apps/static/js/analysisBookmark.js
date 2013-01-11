var tableFilters = [ "options", "versions", "hosts", "platforms" ];

function prefillAll(){
    $.each(prefillData, function(key, value){
        if( $.inArray(key, tableFilters) == -1 ){
            var myelement = $("#"+key);
            if(myelement.is(":input")) {
            	if(myelement.attr("type") == "text" || myelement.attr("type") == "textarea"){
            		myelement.val(value);
            	}
            	else if(myelement.attr("type") == "radio" || myelement.attr("type") == "checkbox"){
                    if(value == "true"){
                        myelement.attr('checked','checked');     		
                    }
            	}
            	else if(myelement.is("select")){
            		myelement.val(value);
            	}
            }
        }
   });
}

function trigger(){
    if (prefillData['trigger'] == "true")
        $("#execute_query").trigger("click");
}

$.fn.prefill = function (){
    var myelement = $(this);
    var key = myelement.attr('id');
    if( $.inArray(key, tableFilters) == -1  && prefillData.hasOwnProperty(key)){
        var value = prefillData[key];
        if(myelement.is(":input")) {
        	if(myelement.attr("type") == "text" || myelement.attr("type") == "textarea"){
        		myelement.val(value);
        	}
        	else if(myelement.attr("type") == "radio" || myelement.attr("type") == "checkbox"){
                if(value == "true"){
                    myelement.attr('checked','checked');     		
                }
        	}
        	else if(myelement.is("select")){
        		myelement.val(value);
        	}
        }
    }
}

$.fn.prefillBox = function(){
    var key = $(this).attr('id');
    if( prefillData.hasOwnProperty(key) ){
        var values = prefillData[key].split(",");
        
    	$('#'+key+' li label input').each(function () {
	        if( $.inArray( $(this).val() , values) > -1){
                $(this).attr('checked', 'checked');
            }
    	});
    }
}


