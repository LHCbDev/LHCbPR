var tableFilters = [ "options", "versions", "hosts", "platforms" ];

function prefillAll(){
    jQuery.each(prefillData, function(key, value){
        if( jQuery.inArray(key, tableFilters) == -1 ){
            var myelement = jQuery("#"+key);
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
        jQuery("#execute_query").trigger("click");
}

jQuery.fn.prefill = function (){
    var myelement = $(this);
    var key = myelement.attr('id');
    if( jQuery.inArray(key, tableFilters) == -1  && prefillData.hasOwnProperty(key)){
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

jQuery.fn.prefillBox = function(){
    var key = jQuery(this).attr('id');
    if( prefillData.hasOwnProperty(key) ){
        var values = prefillData[key].split(",");
        
    	jQuery('#'+key+' li label input').each(function () {
	        if( jQuery.inArray( jQuery(this).val() , values) > -1){
                jQuery(this).attr('checked', 'checked');
            }
    	});
    }
}


