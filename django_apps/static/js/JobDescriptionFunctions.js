//hide some elements on startup
var myCurrent_page;
var myChoosedJob_id = "";

/*	application	version	options	setupporject	div	id */
var dialogInputs = ["ApplicationDetails","VersionDetails","SetupProjectDetails","OptionsDetails","overviewDialogP"];
var cloneInputs = ["ApplicationClone","VersionClone","SetupProjectClone","OptionsClone","overviewCloneP"];
var editInputs = ["ApplicationEdit","VersionEdit","SetupProjectEdit","OptionsEdit","overviewEditP"];

String.prototype.fulltrim=function(){
	return this.replace(/(?:(?:^|\n)\s+|\s+(?:$|\n))/g,'').replace(/\s+/g,' ');
}


var opts = {
	lines: 13, // The number of lines to draw
	length: 7, // The length of each line
	width: 4, // The line thickness
	radius: 10, // The radius of the inner circle
	rotate: 0, // The rotation offset
	color: '#000', // #rgb or #rrggbb
	speed: 1, // Rounds per second
	trail: 60, // Afterglow percentage
	shadow: false, // Whether to render a shadow
	hwaccel: false, // Whether to use hardware acceleration
	className: 'spinner', // The CSS class to assign to the spinner
	zIndex: 2e9, // The z-index (defaults to 2000000000)
	top: 'auto', // Top position relative to parent in px
	left: 'auto' // Left position relative to parent in px
};
  
$(document).ready(function () {
    $("#Platform").hide();
	$("#SetupProject").hide();
	$("#dialog").hide();
	$("#cloneDialog").hide();
	$("#editDialog").hide();
	$("#dialogClose").click(function () {$("#dialog").dialog("close");});
	$("#goBackToDialog").click(function () { 
				openWindow(myChoosedJob_id); 	
				$("#cloneDialog").dialog("close");
			});
	$("#goBackToDialogEdit").click(function () { 
				openWindow(myChoosedJob_id); 	
				$("#editDialog").dialog("close");
			});
	$("#RunInDialog").click(function () { run(); });
	$("#UploadResultsInDialog").click(function () { uploadResults(); });
	$("#CloneInDialog").click(function () { openCloneWindow(myChoosedJob_id); });
	$("#EditInDialog").click(function () { openEditWindow(myChoosedJob_id); });
	$("#commitClone").click(function () { checkCommit(); });
	$("#commitEdit").click(function() { checkUpdate();});
	$("#overviewDialog").hide();
	$("#overviewButtonClone").click(function () {
		// check visibility
		if ($("#overviewClone").is(":hidden")) {
		// it's hidden - show it
				$("#overviewClone").slideDown("normal");
				$("#overviewImageClone").attr('src','/static/images/arrow_upHelp.gif');
				
		} else {
			// it's not hidden - slide it down
				$("#overviewClone").slideUp("normal");
				$("#overviewImageClone").attr('src','/static/images/arrow-downHelp.png');
			}
		});
	$("#overviewButtonEdit").click(function () {
		// check visibility
		if ($("#overviewEdit").is(":hidden")) {
		// it's hidden - show it
				$("#overviewEdit").slideDown("normal");
				$("#overviewImageEdit").attr('src','/static/images/arrow_upHelp.gif');
				
		} else {
			// it's not hidden - slide it down
				$("#overviewEdit").slideUp("normal");
				$("#overviewImageEdit").attr('src','/static/images/arrow-downHelp.png');
			}
		});
	$("#overviewButton").click(function () {
		// check visibility
		if ($("#overviewDialog").is(":hidden")) {
			// it's hidden - show it
				$("#overviewDialog").slideDown("slow");
				$(this).find('span').removeClass('ui-icon-arrowthick-1-s');
				$(this).find('span').addClass('ui-icon-arrowthick-1-n');
		} else {
			// it's not hidden - slide it down
				$("#overviewDialog").slideUp("slow");
				$(this).find('span').removeClass('ui-icon-arrowthick-1-n');
				$(this).find('span').addClass('ui-icon-arrowthick-1-s');
			}
		});

	$("#help").hide();
	$("#helpButton").click(function () {
		// check visibility
		if ($("#help").is(":hidden")) {
		// it's hidden - show it
				$("#help").slideDown("normal");
				$("#helpImage").attr('src','/static/images/arrow_upHelp.gif');
		} else {
			// it's not hidden - slide it down
				$("#help").slideUp("normal");
				$("#helpImage").attr('src','/static/images/arrow-downHelp.png');
			}
		});

/* $("#commitClone").click(function () { 
	$version = $.trim($("#VersionClone").val().fulltrim());
	$options_content = $.trim($("#OptionsClone").val());
	$options_descr = $.trim($("#OptionsDClone").val());
	$setup_content = $.trim($("#SetupProjectClone").val());
	$setup_descr = $.trim($("#SetupProjectDClone").val());
	$application = $.trim($("#ApplicationClone").val());

	$.ajax({
    	'url' : '/django/lhcbPR/commitClone',
		'type' : 'GET',
		'data' : {
		'application' : $application,
		'version' : $version, 
		'setupproject' : $setup_content,
		'setupprojectD' : $setup_descr,
		'options' : $options_content,
		'optionsD' : $options_descr,	
		},
    	'success' : function(data) {
			 var jsondata = $.parseJSON(data);
			if (jsondata.exists)
				alert("Job description already exists");
			else 
				alert("Job added (dummy function, doesn't really saves the new object)");
      	}
    });
 });
*/

});
function checkUpdate(){
	version = document.getElementById("VersionEdit").value.fulltrim();
	options_content = document.getElementById("OptionsEdit").value.fulltrim();
	options_descr = document.getElementById("OptionsDEdit").value.fulltrim();
	setup_content = document.getElementById("SetupProjectEdit").value.fulltrim();
	setup_descr = document.getElementById("SetupProjectDEdit").value.fulltrim();
	
	if (version == "" || options_content == "" || options_descr == ""){
		alert("All fields must be filled (except the SetupProjects fields which can be empty)!");
		return;
	}
	
	var platforms = getSelectedChildsOne("platformsEdit");
	if (platforms.length == 0){
		alert("At least one platform must be checked!")
		return;
	}
	var handlers = getSelectedChildsOne("handlersEdit");
	if (handlers.length == 0){
		alert("At least one handler must be checked!")
		return;
	}

	var xmlhttp;    
	if (window.XMLHttpRequest){
		// code for IE7+, Firefox, Chrome, Opera, Safari
  		xmlhttp=new XMLHttpRequest();
  	}
	else{
		// code for IE6, IE5
  		xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  	}

	// when the response comes do...
	xmlhttp.onreadystatechange=function()
	{
  		if (xmlhttp.readyState==4 && xmlhttp.status==200)
		{
			var jsondata = JSON.parse(xmlhttp.responseText);
			if (jsondata.updated)
				alert("Job description updated successfully(dummy function, doesn't really updates the new object)");
    	}	
  	}
	
	application = document.getElementById("ApplicationClone").value.fulltrim();
	// send the request the to server
	xmlhttp.open("GET", "/django/lhcbPR/commitClone?application="+application+"&version="+version+"&setupproject="
	+setup_content+"&setupprojectD="+setup_descr+"&options="+options_content+"&optionsD="+options_descr
	+"&platforms="+escape(platforms.join(","))+"&handlers="+escape(handlers.join(","))+"&update=", true);
	xmlhttp.send();
	
	return;
}

function checkCommit(){
	version = document.getElementById("VersionClone").value.fulltrim();
	options_content = document.getElementById("OptionsClone").value.fulltrim();
	options_descr = document.getElementById("OptionsDClone").value.fulltrim();
	setup_content = document.getElementById("SetupProjectClone").value.fulltrim();
	setup_descr = document.getElementById("SetupProjectDClone").value.fulltrim();
	
	if (version == "" || options_content == "" || options_descr == ""){
		alert("All fields must be filled (except the SetupProjects fields which can be empty)!");
		return;
	}
	
	if ((setup_content == "" && setup_descr != "") || (setup_content != "" && setup_descr == "")){
		alert("SetupProject fields must be both filled or both empty!");
		return;
	}
	
	var platforms = getSelectedChildsOne("platformsClone");
	if (platforms.length == 0){
		alert("At least one platform must be checked!")
		return;
	}
	var handlers = getSelectedChildsOne("handlersClone");
	if (handlers.length == 0){
		alert("At least one handler must be checked!")
		return;
	}

	var xmlhttp;    
	if (window.XMLHttpRequest){
		// code for IE7+, Firefox, Chrome, Opera, Safari
  		xmlhttp=new XMLHttpRequest();
  	}
	else{
		// code for IE6, IE5
  		xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  	}

	// when the response comes do...
	xmlhttp.onreadystatechange=function()
	{
  		if (xmlhttp.readyState==4 && xmlhttp.status==200)
		{
			var jsondata = JSON.parse(xmlhttp.responseText);
			if (jsondata.exists)
				alert("Job description already exists");
			else 
				alert("Job added (dummy function, doesn't really saves the new object)");
    	}	
  	}
	
	application = document.getElementById("ApplicationClone").value.fulltrim();
	// send the request the to server
	xmlhttp.open("GET", "/django/lhcbPR/commitClone?application="+application+"&version="+version+"&setupproject="
	+setup_content+"&setupprojectD="+setup_descr+"&options="+options_content+"&optionsD="+options_descr
	+"&platforms="+escape(platforms.join(","))+"&handlers="+escape(handlers.join(",")), true);
	xmlhttp.send();
	
	return;
}

function getSelectedChildsOne(id){
	nodes = document.getElementById(id).children;
	var sdValues = [];
	for(i=0; i<nodes.length; i+=1) {
    	if (nodes[i].checked == true){
			sdValues.push(nodes[i].value);
		}
	}
	return sdValues;
}

function makeOverview(div_id){
	var myArray;
	if (div_id == "dialog")
		myArray = dialogInputs;
	if (div_id == "cloneDialog")
		myArray = cloneInputs;
	if (div_id == "editDialog")
		myArray = editInputs;

	removeAllChilds(myArray[4]);	

	box = document.getElementById(myArray[4]);
	
	box.appendChild(document.createTextNode("SetupProject "+document.getElementById(myArray[0]).value.fulltrim()+" "+document.getElementById(myArray[1]).value.fulltrim()+" "+document.getElementById(myArray[2]).value.fulltrim()));
	box.appendChild(document.createElement("br"));
	box.appendChild(document.createTextNode("gaudirun.py "+document.getElementById(myArray[3]).value.fulltrim()));

	return;
}

function fixInputs(father, child, func,real_name,event){
		var myvalue = $("#"+father).val();
		
			if (window.XMLHttpRequest){
				// code for IE7+, Firefox, Chrome, Opera, Safari
  				xmlhttp=new XMLHttpRequest();
  			}
			else{
				// code for IE6, IE5
  				xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  			}

			// when the response comes do...
			xmlhttp.onreadystatechange=function()
			{
  				if (xmlhttp.readyState==4 && xmlhttp.status==200)
				{
					var jsondata = JSON.parse(xmlhttp.responseText);
					
					if (jsondata.data != ""){
						$("#"+child).val(jsondata.data);
						if (event == "onkeyup")
							$("#"+child).attr("readOnly","readonly");
						else if (event == "onblur")
							$("#"+father).attr("readOnly","readonly");
					}
					else{
						if (event == "onkeyup"){					
    					 		$("#"+child).removeAttr('readOnly');
								$("#"+child).val("");	
						}
					}
					makeOverview("cloneDialog");
					makeOverview("editDialog");
				}
    		}	
			// send the request the to server
			xmlhttp.open("GET", "https://alamages.cern.ch/django/lhcbPR/editRequests?key="+func+"&value="+myvalue.fulltrim()+"&real_name="+real_name, true);
			xmlhttp.send();
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

function removeAllChilds(myId){
	var node= document.getElementById(myId);		
	if ( node.hasChildNodes() ){
   		while ( node.childNodes.length >= 1 ){
       			node.removeChild( node.firstChild );       
    	} 
	}	
	return;
}

function getSelectedChilds(id){
	nodes = document.getElementById(id).children;
	var sdValues = [];
	for(i=0; i<nodes.length; i+=1) {
    	if (nodes[i].children[0].children[0].checked == true){
			sdValues.push(nodes[i].children[0].children[0].value);
		}
	}
	return sdValues;
}

function clearCheckBox(id){
	var checked_existed;
	nodes = document.getElementById(id).children;
	for(i=0; i<nodes.length; i+=1) {
    	if (nodes[i].children[0].children[0].checked == true){
			nodes[i].children[0].children[0].checked = false;
			checked_existed = true;
		}
	}
	//call again the filters
	if (checked_existed)
		doFilter(1);
	return;
}


function addJobs(box,apps){
	//loop over the array which contains the versions
	for(var i = 0; i < apps.length; i++)
	{	
		var myLi = document.createElement("li");
		
		myLi.appendChild(document.createTextNode(apps[i].appName+"  "+apps[i].appVersion+"  "+apps[i].optionsD+"  "+apps[i].setupproject));
			
		//extra function click
		myLi.setAttribute('id', apps[i].pk);
		myLi.setAttribute('class','ui-widget-content');
		//myLi.setAttribute('onclick','return openWindow(this.id);');
		box.appendChild(myLi);
	}
	return;
}


/*function addJobs(myId,box,apps){
	//loop over the array which contains the versions
	for(var i = 0; i < apps.length; i++)
	{
		var hrefObj = document.createElement("a");		
		var liObj = document.createElement("li");
		
		hrefObj.appendChild(document.createTextNode(apps[i].appName+"  "+apps[i].appVersion+"  "+apps[i].optionsD+"  "+apps[i].setupproject));
		liObj.appendChild(hrefObj);

		hrefObj.setAttribute('href','javascript:;');
		hrefObj.setAttribute('id', apps[i].pk);
			
		//extra function click
		hrefObj.setAttribute('onclick','openWindow(this.id)');
		box.appendChild(liObj);
	}
	return;
}
*/

function permalink(){
	var setupprojects = getSelectedChilds("SetupProject");
	var appVersions = getSelectedChilds("Version");
	var options = getSelectedChilds("Options");
	var cmts = getSelectedChilds("Platform");	

	mypermalink = "?page="+myCurrent_page;
	if (appVersions.length >= 1)
		mypermalink+= "&appVersions="+escape(appVersions.join(","));
	if (setupprojects.length >=1)
		mypermalink+= "&SetupProjects="+escape(setupprojects.join(","));
	if (options.length >= 1)
		mypermalink+= "&Options="+escape(options.join(","));
	if (cmts.length >= 1)
		 mypermalink+= "&platforms="+escape(cmts.join(","));
	
	//location.hash = mypermalink;
	document.getElementById("mypermalink").href = window.location.href.split("?")[0]+mypermalink;
	
	return;
}

function openWindow(job_id){
	var xmlhttp;    
	if (window.XMLHttpRequest){
		// code for IE7+, Firefox, Chrome, Opera, Safari
  		xmlhttp=new XMLHttpRequest();
  	}
	else{
		// code for IE6, IE5
  		xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  	}

	// when the response comes do...
	xmlhttp.onreadystatechange=function()
	{
  		if (xmlhttp.readyState==4 && xmlhttp.status==200)
		{
			var jsondata = JSON.parse(xmlhttp.responseText);
			mydialog = document.getElementById("dialog");
			mydialog.title=jsondata.appName+" job description details";
					
			document.getElementById("ApplicationDetails").value = jsondata.appName;
			document.getElementById("VersionDetails").value = jsondata.appVersion;
			document.getElementById("OptionsDetails").value = jsondata.options;
			document.getElementById("OptionsDDetails").value = jsondata.optionsD;
			document.getElementById("SetupProjectDetails").value = jsondata.setupProject;
			document.getElementById("SetupProjectDDetails").value = jsondata.setupProjectD;		
			
			removeAllChilds("platformsDetails");	
			removeAllChilds("handlersDetails");	
			mybox = document.getElementById("platformsDetails");
			myboxHandlers = document.getElementById("handlersDetails");			

			for(var i = 0; i < jsondata.platforms.length; i++){
					myInput = document.createElement("input");
					myInput.type = "checkbox";	
					myInput.value = jsondata.platforms[i].platform;
					myInput.setAttribute('readOnly','readonly');
					myInput.setAttribute('disabled','true');	
					if (jsondata.platforms[i].checked)
							myInput.setAttribute('checked','checked');
						
					mybox.appendChild(myInput);
					mybox.appendChild(document.createTextNode(jsondata.platforms[i].platform));
					mybox.appendChild(document.createElement("br"));
					
			}
			for(var i = 0; i < jsondata.handlers.length; i++){
					myInput = document.createElement("input");
					myInput.type = "checkbox";	
					myInput.value = jsondata.handlers[i].handler;
					myInput.setAttribute('readOnly','readonly');
					myInput.setAttribute('disabled','true');	
					if (jsondata.handlers[i].checked)
							myInput.setAttribute('checked','checked');
						
					myboxHandlers.appendChild(myInput);
					myboxHandlers.appendChild(document.createTextNode(jsondata.handlers[i].handler));
					myboxHandlers.appendChild(document.createElement("br"));
					
			}
			myChoosedJob_id = job_id;
				$("#overviewDialog").hide();
				$("#dialog").dialog({
    				resizable: false,
    				height: 550,
    				width: 860,
   					modal: true,
				});
				//fix overview
				makeOverview("dialog");
    	}	
  	}
	// send the request the to server
	xmlhttp.open("GET", "https://alamages.cern.ch/django/lhcbPR/getJobDetails?job_id="+job_id, true);
	xmlhttp.send();
	
	return;
}

function openEditWindow(job_id){
	if (job_id == "")
		return;

	var xmlhttp;    
	if (window.XMLHttpRequest){
		// code for IE7+, Firefox, Chrome, Opera, Safari
  		xmlhttp=new XMLHttpRequest();
  	}
	else{
		// code for IE6, IE5
  		xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  	}

	// when the response comes do...
	xmlhttp.onreadystatechange=function()
	{
  		if (xmlhttp.readyState==4 && xmlhttp.status==200)
		{
			var jsondata = JSON.parse(xmlhttp.responseText);
			mydialog = document.getElementById("editDialog");
			mydialog.title="Update existing "+jsondata.appName+" job description";
					
			document.getElementById("ApplicationEdit").value = jsondata.appName;
			document.getElementById("VersionEdit").value = jsondata.appVersion;
			document.getElementById("OptionsEdit").value = jsondata.options;
			document.getElementById("OptionsDEdit").value = jsondata.optionsD;
			document.getElementById("SetupProjectEdit").value = jsondata.setupProject;
			document.getElementById("SetupProjectDEdit").value = jsondata.setupProjectD;		
			
			removeAllChilds("platformsEdit");
			removeAllChilds("handlersEdit");	
			mybox = document.getElementById("platformsEdit");
			myboxHandler = document.getElementById("handlersEdit");
	
			for(var i = 0; i < jsondata.platforms.length; i++){
					myInput = document.createElement("input");
					myInput.type = "checkbox";	
					myInput.value = jsondata.platforms[i].platform;
					
					if (jsondata.platforms[i].checked)
							myInput.setAttribute('checked','true');
					
					mybox.appendChild(myInput);
					mybox.appendChild(document.createTextNode(jsondata.platforms[i].platform));
					mybox.appendChild(document.createElement("br"));		
			}
			for(var i = 0; i < jsondata.handlers.length; i++){
					myInput = document.createElement("input");
					myInput.type = "checkbox";	
					myInput.value = jsondata.handlers[i].handler;
					
					if (jsondata.handlers[i].checked)
							myInput.setAttribute('checked','true');
					
					myboxHandler.appendChild(myInput);
					myboxHandler.appendChild(document.createTextNode(jsondata.handlers[i].handler));
					myboxHandler.appendChild(document.createElement("br"));		
			}
			$( "#VersionEdit" ).autocomplete({
				source: jsondata.versionsAll
			});
			$( "#OptionsEdit" ).autocomplete({
				source: jsondata.optionsAll
			});
			$( "#OptionsDEdit" ).autocomplete({
				source: jsondata.optionsDAll
			});
			$( "#SetupProjectEdit" ).autocomplete({
				source: jsondata.setupAll
			});
			$( "#SetupProjectDEdit" ).autocomplete({
				source: jsondata.setupDAll
			});
			$('#VersionEdit').attr('readOnly','readOnly');
			$('#OptionsEdit').attr('readOnly','readonly');
			$('#SetupProjectEdit').attr('readOnly','readonly');
			$('#OptionsDEdit').attr('readOnly','readonly');
			$('#SetupProjectDEdit').attr('readOnly','readonly');

			if (!jsondata.exists){
				$('#VersionEdit').removeAttr('readOnly');
				$('#OptionsDEdit').removeAttr('readOnly');
				$('#SetupProjectDEdit').removeAttr('readOnly');
				removeAllChilds('editMessage');
				document.getElementById("editMessage").appendChild(document.createTextNode("JobDescription doesn't exist in runned jobs"));
			}
			else{
				removeAllChilds("editMessage");
				document.getElementById("editMessage").appendChild(document.createTextNode("Job description exists in runned jobs!"));
			}
			$('#overviewEdit').hide();
			$("#editDialog").dialog({
    			resizable: false,
    			height: 530,
    			width: 860,
   				modal: true
			});
			makeOverview("editDialog");
    	}	
  	}
	// send the request the to server
	xmlhttp.open("GET", "https://alamages.cern.ch/django/lhcbPR/getJobDetails?job_id="+job_id+"&editRequest=", true);
	xmlhttp.send();
	$("#dialog").dialog("close");
	return;
}


function openCloneWindow(job_id){
	if (job_id == "")
		return;

	var xmlhttp;    
	if (window.XMLHttpRequest){
		// code for IE7+, Firefox, Chrome, Opera, Safari
  		xmlhttp=new XMLHttpRequest();
  	}
	else{
		// code for IE6, IE5
  		xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  	}

	// when the response comes do...
	xmlhttp.onreadystatechange=function()
	{
  		if (xmlhttp.readyState==4 && xmlhttp.status==200)
		{
			var jsondata = JSON.parse(xmlhttp.responseText);
			mydialog = document.getElementById("cloneDialog");
			mydialog.title="Add new "+jsondata.appName+" job description";
					
			document.getElementById("ApplicationClone").value = jsondata.appName;
			document.getElementById("VersionClone").value = jsondata.appVersion;
			document.getElementById("OptionsClone").value = jsondata.options;
			document.getElementById("OptionsDClone").value = jsondata.optionsD;
			document.getElementById("SetupProjectClone").value = jsondata.setupProject;
			document.getElementById("SetupProjectDClone").value = jsondata.setupProjectD;		
			
			removeAllChilds("platformsClone");
			removeAllChilds("handlersClone");	
			mybox = document.getElementById("platformsClone");
			myboxHandler = document.getElementById("handlersClone");
	
			for(var i = 0; i < jsondata.platforms.length; i++){
					myInput = document.createElement("input");
					myInput.type = "checkbox";	
					myInput.value = jsondata.platforms[i].platform;
					
					if (jsondata.platforms[i].checked)
							myInput.setAttribute('checked','true');
					
					mybox.appendChild(myInput);
					mybox.appendChild(document.createTextNode(jsondata.platforms[i].platform));
					mybox.appendChild(document.createElement("br"));		
			}
			for(var i = 0; i < jsondata.handlers.length; i++){
					myInput = document.createElement("input");
					myInput.type = "checkbox";	
					myInput.value = jsondata.handlers[i].handler;
					
					if (jsondata.handlers[i].checked)
							myInput.setAttribute('checked','true');
					
					myboxHandler.appendChild(myInput);
					myboxHandler.appendChild(document.createTextNode(jsondata.handlers[i].handler));
					myboxHandler.appendChild(document.createElement("br"));		
			}
			$( "#VersionClone" ).autocomplete({
				source: jsondata.versionsAll
			});
			$( "#OptionsClone" ).autocomplete({
				source: jsondata.optionsAll
			});
			$( "#OptionsDClone" ).autocomplete({
				source: jsondata.optionsDAll
			});
			$( "#SetupProjectClone" ).autocomplete({
				source: jsondata.setupAll
			});
			$( "#SetupProjectDClone" ).autocomplete({
				source: jsondata.setupDAll
			});
			
			$('#OptionsClone').attr('readOnly','readonly');
			$('#SetupProjectClone').attr('readOnly','readonly');
			$('#overviewClone').hide();
			$("#cloneDialog").dialog({
    			resizable: false,
    			height: 530,
    			width: 860,
   				modal: true
			});
			makeOverview("cloneDialog");
    	}	
  	}
	// send the request the to server
	xmlhttp.open("GET", "https://alamages.cern.ch/django/lhcbPR/getJobDetails?job_id="+job_id+"&cloneRequest=", true);
	xmlhttp.send();
	$("#dialog").dialog("close");
	return;
}


function commitJob(job_id){
	var xmlhttp;    
	if (window.XMLHttpRequest){
		// code for IE7+, Firefox, Chrome, Opera, Safari
  		xmlhttp=new XMLHttpRequest();
  	}
	else{
		// code for IE6, IE5
  		xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  	}

	// when the response comes do...
	xmlhttp.onreadystatechange=function()
	{
  		if (xmlhttp.readyState==4 && xmlhttp.status==200)
		{
			var jsondata = JSON.parse(xmlhttp.responseText);
    	}	
  	}
	// send the request the to server
	xmlhttp.open("GET", "https://alamages.cern.ch/django/lhcbPR/commitClone?", true);
	xmlhttp.send();
	
	return;
}

function run(){
	alert("Run function, under construction...");
}
function uploadResults(){
	alert("Upload results function, under construction...");
}
