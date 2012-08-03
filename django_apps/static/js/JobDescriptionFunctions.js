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
  
$(document).ready(function () {
	$("#overlay").hide();
    $("#alertDialog").hide();
	$("#editPlatformsHandlers").hide();
	$("#Platform").hide();
	$("#SetupProject").hide();
	$("#dialog").hide();
	$("#cloneDialog").hide();
	$("#editDialog").hide();
	$("#dialogClose").click(function () {$("#dialog").dialog("close");});
	$("#goBackToDialog").click(function () { 
				openWindow(myChoosedJob_id); 	
				$("#pagebody").mask("Loading...");
				$("#cloneDialog").dialog("close");
			});
	$("#goBackToDialogEdit").click(function () { 
				openWindow(myChoosedJob_id); 	
				$("#pagebody").mask("Loading...");
				$("#editDialog").dialog("close");
			});
	$("#RunInDialog").click(function () { run(); });
	$("#UploadResultsInDialog").click(function () { uploadResults(); });
	$("#CloneInDialog").click(function () { openCloneWindow(myChoosedJob_id); $("#pagebody").mask("Loading..."); });
	$("#EditInDialog").click(function () { openEditWindow(myChoosedJob_id); $("#pagebody").mask("Loading..."); });
	$("#commitEdit").click(function() { checkUpdate();});
	$("#overviewDialog").hide();
	$("#overviewButtonClone").click(function () {
		// check visibility
		if ($("#overviewClone").is(":hidden")) {
			// it's hidden - show it
				$("#overviewClone").slideDown("slow");
				$(this).find('span').removeClass('ui-icon-arrowthick-1-s');
				$(this).find('span').addClass('ui-icon-arrowthick-1-n');
		} else {
			// it's not hidden - slide it down
				$("#overviewClone").slideUp("slow");
				$(this).find('span').removeClass('ui-icon-arrowthick-1-n');
				$(this).find('span').addClass('ui-icon-arrowthick-1-s');
			}
		});
	$("#overviewButtonEdit").click(function () {
		// check visibility
		if ($("#overviewEdit").is(":hidden")) {
			// it's hidden - show it
				$("#overviewEdit").slideDown("slow");
				$(this).find('span').removeClass('ui-icon-arrowthick-1-s');
				$(this).find('span').addClass('ui-icon-arrowthick-1-n');
		} else {
			// it's not hidden - slide it down
				$("#overviewEdit").slideUp("slow");
				$(this).find('span').removeClass('ui-icon-arrowthick-1-n');
				$(this).find('span').addClass('ui-icon-arrowthick-1-s');
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

		
		$("#commitClone").click(function () { 
			$version = $.trim($("#VersionClone").val().fulltrim());
			$options_content = $.trim($("#OptionsClone").val());
			$options_descr = $.trim($("#OptionsDClone").val());
			$setup_content = $.trim($("#SetupProjectClone").val());
			$setup_descr = $.trim($("#SetupProjectDClone").val());
			$application = $.trim($("#ApplicationClone").val());
			
			if ($version == "" || $options_content == "" || $options_descr == ""){
				myAlert("All fields must be filled (except the SetupProjects fields which can be empty)!","","Attention","");
				return;
			}
	
			if (($setup_content == "" && $setup_descr != "") || ($setup_content != "" && $setup_descr == "")){
				myAlert("ASetupProject fields must be both filled or both empty!","","Attention","");
				return;
			}
	
			var platforms = getSelectedChildsOne("platformsClone");
			if (platforms.length == 0){
				myAlert("At least one platform must be checked!","","Attention","");
				return;
			}

			var handlers = getSelectedChildsOne("handlersClone");
			if (handlers.length == 0){
				myAlert("At least one handler must be checked!","","Commit message","");
				return;
			}

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
						myAlert("Job description already exists","","Attention","");
					else 
						myAlert("Job added (dummy function, doesn't really saves the new object)","","Attention","");
      			}
    		});/* /ajax*/
 		});/* /commitClone function*/
		

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

function getSelectedChildsOne(id){
	//nodes = document.getElementById(id).children;
	nodes = document.getElementById(id).getElementsByTagName("input");
	var sdValues = [];
	for(i=0; i<nodes.length; i+=1) {
			sdValues.push(nodes[i].value);
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
		box.appendChild(myLi);
	}
	return;
}

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
					myInput.value = jsondata.platforms[i];
					myInput.setAttribute('readOnly','readonly');
					myInput.setAttribute('disabled','true');	
					
					myInput.setAttribute('checked','checked');
						
					mybox.appendChild(myInput);
					mybox.appendChild(document.createTextNode(jsondata.platforms[i]));
					mybox.appendChild(document.createElement("br"));
					
			}
			for(var i = 0; i < jsondata.handlers.length; i++){
					myInput = document.createElement("input");
					myInput.type = "checkbox";	
					myInput.value = jsondata.handlers[i];
					myInput.setAttribute('readOnly','readonly');
					myInput.setAttribute('disabled','true');	
					
					myInput.setAttribute('checked','checked');
						
					myboxHandlers.appendChild(myInput);
					myboxHandlers.appendChild(document.createTextNode(jsondata.handlers[i]));
					myboxHandlers.appendChild(document.createElement("br"));
					
			}
			myChoosedJob_id = job_id;
				$("#overviewDialog").hide();
			
				$("#pagebody").unmask();

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
					myInput.value = jsondata.platforms[i];
					myInput.setAttribute('readOnly','readonly');
					myInput.setAttribute('disabled','true');
					
					myInput.setAttribute('checked','true');
					
					mybox.appendChild(myInput);
					mybox.appendChild(document.createTextNode(jsondata.platforms[i]));
					mybox.appendChild(document.createElement("br"));		
			}
			for(var i = 0; i < jsondata.handlers.length; i++){
					myInput = document.createElement("input");
					myInput.type = "checkbox";	
					myInput.value = jsondata.handlers[i];
					myInput.setAttribute('readOnly','readonly');
					myInput.setAttribute('disabled','true');
					
					myInput.setAttribute('checked','true');
					
					myboxHandler.appendChild(myInput);
					myboxHandler.appendChild(document.createTextNode(jsondata.handlers[i]));
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

			$("#pagebody").unmask();

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
					myInput.setAttribute('readOnly','readonly');
					myInput.setAttribute('disabled','true');
					myInput.value = jsondata.platforms[i];
					
					myInput.setAttribute('checked','true');
					
					mybox.appendChild(myInput);
					mybox.appendChild(document.createTextNode(jsondata.platforms[i]));
					mybox.appendChild(document.createElement("br"));		
			}
			for(var i = 0; i < jsondata.handlers.length; i++){
					myInput = document.createElement("input");
					myInput.type = "checkbox";
					myInput.setAttribute('readOnly','readonly');
					myInput.setAttribute('disabled','true');
					myInput.value = jsondata.handlers[i];
					
					myInput.setAttribute('checked','true');
					
					myboxHandler.appendChild(myInput);
					myboxHandler.appendChild(document.createTextNode(jsondata.handlers[i]));
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
			
			$("#pagebody").unmask();
			
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

//mybox_id is the container of the original platforms/handlers
function openPanel(id, service,mybox_id){
	if (service == "platforms"){
		$("#editPlatformsHandlers").attr('title','Platforms edit panel');
		$("#availableTitle").text("Available platforms");
		$("#requestedTitle").text("Requested platforms");
	}
	else if(service == "handlers"){
		$("#editPlatformsHandlers").attr('title','Handlers edit panel');
		$("#availableTitle").text("Available handlers");
		$("#requestedTitle").text("Requested handlers");
	}
	$.ajax({
    	'url' : '/django/lhcbPR/editPanel',
		'type' : 'GET',
		'data' : {
		'service' : service,
		'jobDescription_id' : id, 
		},
    	'success' : function(data) {
			var jsondata = $.parseJSON(data);
			removeAllChilds("requestedAttributes");
			var mybox = document.getElementById("requestedAttributes");
			
			requested = getSelectedChildsOne(mybox_id);
			for(var i = 0; i < requested.length; i++)
			{	
				var myLi = document.createElement("li");
				myLi.appendChild(document.createTextNode(requested[i]));
				//extra function click
				myLi.setAttribute('id', requested[i]);
				myLi.setAttribute('class','ui-widget-content');
				mybox.appendChild(myLi);
			}
			removeAllChilds("availableAttributes");
			var mybox2 = document.getElementById("availableAttributes");
			
			/* check which requested exist also in available */
			var available = [];
			var exists = 0;
			for (var y = 0; y < jsondata.available.length; y++){
				for (var k = 0; k < requested.length; k++){
					if (jsondata.available[y] == requested[k]){
						exists = 1;
						break;
					}
				}
				if (exists == 0){
					available.push(jsondata.available[y]);
				}
				exists = 0;
			}
			
			for(var i = 0; i < available.length; i++)
			{	
					var myLi = document.createElement("li");
					myLi.appendChild(document.createTextNode(available[i]));
					//extra function click
					myLi.setAttribute('id', available[i]);
					myLi.setAttribute('class','ui-widget-content');
					mybox2.appendChild(myLi);
			}
			//open dialog if success
			$("#editPlatformsHandlers").dialog({
    			resizable: false,
    			height:560,
    			width: 532,
   				modal: true,
				buttons: {
						"Ok": function() {
							var newAttributes =  getListValues("requestedAttributes");
							mybox = document.getElementById(mybox_id);	
							removeAllChilds(mybox_id);	
								
							for(var i = 0; i < newAttributes.length; i++){
								myInput = document.createElement("input");
								myInput.type = "checkbox";	
								myInput.value = newAttributes[i];
								myInput.setAttribute('readOnly','readonly');
								myInput.setAttribute('disabled','true');	
									
								myInput.setAttribute('checked','checked');
						
								mybox.appendChild(myInput);
								mybox.appendChild(document.createTextNode(newAttributes[i]));
								mybox.appendChild(document.createElement("br"));	
							}
							$(this).dialog("close");
						},
						"Cancel": function() {
							$(this).dialog("close");
						}
					}
			});
      	}
    });
}

function getListValues(id){
	nodes = document.getElementById(id).children;
	var sdValues = [];
	for(i=0; i<nodes.length; i+=1) {
		sdValues.push(nodes[i].id);
	}
	return sdValues;
}

function myAlert(message1,message2,title, icon){
	$("#alertDialogIcon").attr('class','');
	$("#alertDialogIcon").addClass('ui-icon');
	
	if ( icon == "" ){
		$("#alertDialogIcon").addClass('ui-icon-alert');
	}
	else{
		$("#alertDialogIcon").addClass(icon);
	}
	
	$("#alertDialog").attr('title',title);
	$("#alertMessage").text(message1);
	$("#alertMessage2").text(message2);
	$( "#alertDialog" ).dialog({
			modal: true,
			width : 350,
			buttons: {
				Ok: function() {
					$( this ).dialog( "close" );
				}
			}
	});
}
