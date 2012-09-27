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

		$("#commitClone").click(function () { 
			$version = $.trim($("#VersionClone").val());
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
				myAlert("SetupProject fields must be both filled or both empty!","","Attention","");
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
				'platforms' : platforms.join(","),
				'handlers' : handlers.join(","),
				},
    			'success' : function(data) {
			 		var jsondata = $.parseJSON(data);
					if (jsondata.exists)
						myAlert("Job description already exists","","Attention","");
					else{ 
						myAlertCommit("Job added successfully","","Attention","");
						$( "#alertDialog" ).dialog({
							modal: true,
							width : 350,
							buttons: {
								Ok: function() {
								$( this ).dialog( "close" );
								$("#cloneDialog").dialog("close");
								doFilter(1);
								openWindow(jsondata.job_id);
								}
							}
						});
					}
      			}
    		});/* /ajax*/
 		});/* /commitClone function*/

		$("#commitEdit").click(function(){ 
			$version = $.trim($("#VersionEdit").val());
			$options_content = $.trim($("#OptionsEdit").val());
			$options_descr = $.trim($("#OptionsDEdit").val());
			$setup_content = $.trim($("#SetupProjectEdit").val());
			$setup_descr = $.trim($("#SetupProjectDEdit").val());
			$application = $.trim($("#ApplicationEdit").val());
		
			if ($version == "" || $options_content == "" || $options_descr == ""){
				myAlert("All fields must be filled (except the SetupProjects fields which can be empty)!","","Attention","");
				return;
			}
			if (($setup_content == "" && $setup_descr != "") || ($setup_content != "" && $setup_descr == "")){
				myAlert("SetupProject fields must be both filled or both empty!","","Attention","");
				return;
			}
			var platforms = getSelectedChildsOne("platformsEdit");
			if (platforms.length == 0){
				myAlert("At least one platform must be checked!","","Attention","");
				return;
			}
			var handlers = getSelectedChildsOne("handlersEdit");
			if (handlers.length == 0){
				myAlert("At least one handler must be checked!","","Attention","");
				return;
			}

			$.ajax({
    			'url' : '/django/lhcbPR/commitClone',
				'type' : 'GET',
				'data' : {
				'id' : myChoosedJob_id,
				'application' : $application,
				'version' : $version, 
				'setupproject' : $setup_content,
				'setupprojectD' : $setup_descr,
				'options' : $options_content,
				'optionsD' : $options_descr,	
				'platforms' : platforms.join(","),
				'handlers' : handlers.join(","),
				'update' : '',
				},
    			'success' : function(data) {
			 		var jsondata = $.parseJSON(data);
					if (jsondata.updated)
						myAlertCommit("Job description updated successfully","","Attention","");
						$( "#alertDialog" ).dialog({
							modal: true,
							width : 350,
							buttons: {
								Ok: function() {
								$( this ).dialog( "close" );
								$("#editDialog").dialog("close");
								doFilter(1);
								openWindow(jsondata.job_id);
								}
							}
						});
      			}
    		});/* /ajax*/
		});/* commitEdit */

		$("#job_info").click(function(){  });
		
});

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
	$myvalue =  $.trim($("#"+father).val());
	
	$.ajax({
    	'url' : '/django/lhcbPR/editRequests',
		'type' : 'GET',
		'data' : {
		'key' : func,
		'value' : $myvalue,
		'real_name' : real_name
		},
    	'success' : function(data) {
			var jsondata = $.parseJSON(data);
			
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
    });/* /ajax*/
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
		//apps[i].appName
		myLi.appendChild(document.createTextNode(apps[i].appVersion+"  "+apps[i].optionsD+"  "+apps[i].setupproject));
			
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
	$("#job_info").hide();
	if (job_id == "")
		return;
	$.ajax({
    	'url' : '/django/lhcbPR/getJobDetails',
		'type' : 'GET',
		'data' : {
		'job_id' : job_id,	
		},
    	'success' : function(data) {
			var jsondata = $.parseJSON(data);
			mydialog = document.getElementById("dialog");
			mydialog.title=jsondata.appName+" job description details";
					
			$("#ApplicationDetails").attr('value', jsondata.appName);
			$("#VersionDetails").attr('value', jsondata.appVersion);
			$("#OptionsDetails").attr('value', jsondata.options);
			$("#OptionsDDetails").attr('value', jsondata.optionsD);
			$("#SetupProjectDetails").attr('value', jsondata.setupProject);
			$("#SetupProjectDDetails").attr('value', jsondata.setupProjectD);		
			
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
			$("#generatescript").attr('href','/django/lhcbPR/script?pk='+myChoosedJob_id);
			$("#job_info").attr('href','/django/lhcbPR/getRunnedJobs?pk='+myChoosedJob_id);
			
			if(jsondata.runned_job)
				$("#job_info").show();		
	
			$("#dialog").dialog({
    			resizable: false,
    			height: 550,
    			width: 860,
   				modal: true,
			});
			//fix overview
			makeOverview("dialog");
      	}
    });/* /ajax*/
	return;
}

function openEditWindow(job_id){
	if (job_id == "")
		return;
	$.ajax({
    	'url' : '/django/lhcbPR/getJobDetails',
		'type' : 'GET',
		'data' : {
		'job_id' : job_id,
		'editRequest' : ''
		},
    	'success' : function(data) {
			var jsondata = $.parseJSON(data);
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

			if (!jsondata.runned_job){
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
    });/* /ajax*/
	$("#dialog").dialog("close");
	return;
}
function openCloneWindow(job_id){
	if (job_id == "")
		return;

	$.ajax({
    	'url' : '/django/lhcbPR/getJobDetails',
		'type' : 'GET',
		'data' : {
		'job_id' : job_id,
		'cloneRequest' : '',
		},
    	'success' : function(data) {
			var jsondata = $.parseJSON(data);
			mydialog = document.getElementById("cloneDialog");
			mydialog.title="Add new "+jsondata.appName+" job description";
					
			$("#ApplicationClone").attr('value', jsondata.appName);
			$("#VersionClone").attr('value', jsondata.appVersion);
			$("#OptionsClone").attr('value', jsondata.options);
			$("#OptionsDClone").attr('value', jsondata.optionsD);
			$("#SetupProjectClone").attr('value', jsondata.setupProject);
			$("#SetupProjectDClone").attr('value', jsondata.setupProjectD);		
			
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
    });/* /ajax*/
	$("#dialog").dialog("close");
	return;
}

function run(){
	alert("Run function, under construction...");
}
function uploadResults(){
	alert("Upload results function, under construction...");
}

function addHover(selector){
	$("#"+selector).hover(
		function() { $(this).addClass('ui-state-hover'); 
							$(this).css('cursor','pointer');},
		function() { $(this).removeClass('ui-state-hover'); }
	);	
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
			addHover("requestedAttributes li");
			addHover("availableAttributes li");
			//open dialog if success
			$("#editPlatformsHandlers").dialog({
    			resizable: false,
    			height:560,
    			width: 560,
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

function myAlertCommit(message1,message2,title, icon){
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
}
