//hide some elements on startup
var myCurrent_page;
var myChoosedJob_id = "";
String.prototype.fulltrim=function(){
	return this.replace(/(?:(?:^|\n)\s+|\s+(?:$|\n))/g,'').replace(/\s+/g,' ');
}

$(document).ready(function () {
    $("#Platform").hide();
	$("#PlatformButton").css('background-image','url(https://alamages.cern.ch/bf_button_fon_right_plus.png)');
	$("#SetupProject").hide();
	$("#SetupProjectButton").css('background-image','url(https://alamages.cern.ch/bf_button_fon_right_plus.png)');
	$("#dialog").hide();
	$("#cloneDialog").hide();
	$("#dialogClose").click(function () {$("#dialog").dialog("close");});
	$("#dialogCloneClose").click(function () { $("#cloneDialog").dialog("close"); });
	$("#goBackToDialog").click(function () { 
				openWindow(myChoosedJob_id); 	
				$("#cloneDialog").dialog("close");
			});
	$("#RunInDialog").click(function () { run(); });
	$("#UploadResultsInDialog").click(function () { uploadResults(); });
	$("#CloneInDialog").click(function () { openCloneWindow(myChoosedJob_id); });
	$("#commitClone").click(function () { alert("Commit new jobDescription id under construction..."); });
	$("#help").hide();
	$("#helpButton").click(function () {
		// check visibility
		if ($("#help").is(":hidden")) {
		// it's hidden - show it
				$("#help").slideDown("normal");
				$("#helpImage").attr('src','https://alamages.cern.ch/arrow_upHelp.gif');
		} else {
			// it's not hidden - slide it down
				$("#help").slideUp("normal");
				$("#helpImage").attr('src','https://alamages.cern.ch/arrow-downHelp.png');
			}
		});
		
});

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
				$("#"+button_id).css('background-image','url(https://alamages.cern.ch/bf_button_fon_right.png)');
		} else {
			// it's not hidden - slide it down
				$("#"+box_id).slideUp("slow");
				$("#"+button_id).css('background-image','url(https://alamages.cern.ch/bf_button_fon_right_plus.png)');
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
	//$("#"+myId).empty();
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

function addJobs(myId,box,apps){
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
	box = document.getElementById("Jobs");

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
			mybox = document.getElementById("platformsDetails");
	
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
			myChoosedJob_id = job_id;
				$("#dialog").dialog({
    				resizable: false,
    				height: 700,
    				width: 800,
   					modal: true
				});
    	}	
  	}
	// send the request the to server
	xmlhttp.open("GET", "https://alamages.cern.ch/django/lhcbPR/getJobDetails?job_id="+job_id, true);
	xmlhttp.send();
	
	return;
}

function openCloneWindow(job_id){
	box = document.getElementById("Jobs");

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
			mybox = document.getElementById("platformsClone");
	
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
			$( "#VersionClone" ).autocomplete({
				source: jsondata.versionsClone	
			});
			$( "#OptionsClone" ).autocomplete({
				source: jsondata.optionsClone	
			});
			$( "#OptionsDClone" ).autocomplete({
				source: jsondata.optionsDClone	
			});
			$( "#SetupProjectClone" ).autocomplete({
				source: jsondata.setupClone	
			});
			$( "#SetupProjectDClone" ).autocomplete({
				source: jsondata.setupDClone	
			});
			
			$("#cloneDialog").dialog({
    			resizable: false,
    			height: 700,
    			width: 600,
   				modal: true
			});
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
