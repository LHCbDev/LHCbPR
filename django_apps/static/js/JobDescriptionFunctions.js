//hide some elements on startup
var myCurrent_page;
var myChoosedJob_id = "";
$(document).ready(function () {
    $("#Platform").hide();
	$("#PlatformButton").css('background-image','url(https://alamages.cern.ch/bf_button_fon_right_plus.png)');
	$("#SetupProject").hide();
	$("#SetupProjectButton").css('background-image','url(https://alamages.cern.ch/bf_button_fon_right_plus.png)');
	$(document.getElementsByName("{{ active_tab }}tab")).attr('id',   'selected');
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
});

function showHide( button_id, box_id )
{
     $(document).ready(function() {
		// check visibility
		if ($(document.getElementById(box_id)).is(":hidden")) {
			// it's hidden - show it
				$(document.getElementById(box_id)).slideDown("slow");
				$(document.getElementById(button_id)).css('background-image','url(https://alamages.cern.ch/bf_button_fon_right.png)');
		} else {
			// it's not hidden - slide it down
				$(document.getElementById(box_id)).slideUp("slow");
				$(document.getElementById(button_id)).css('background-image','url(https://alamages.cern.ch/bf_button_fon_right_plus.png)');
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
function addJobs(myId,box,apps){
	//loop over the array which contains the versions
	for(var i = 0; i < apps.length; i++)
	{
		var hrefObj = document.createElement("a");		
		var liObj = document.createElement("li");
		
		hrefObj.appendChild(document.createTextNode(apps[i].appName+" "+apps[i].appVersion+" "+apps[i].setupproject+" "+apps[i].options));
		liObj.appendChild(hrefObj);

		hrefObj.setAttribute('href','javascript:;');
		hrefObj.setAttribute('id', apps[i].pk);
			
		//extra function click
		hrefObj.setAttribute('onclick','openWindow(this.id)');
		box.appendChild(liObj);
	}
	return;
}
function doFilter(requested_page){
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
			var jobs = jsondata.jobs;
			var pageInfo = jsondata.page_info;
			removeAllChilds("Jobs"); 
			addJobs("Jobs",box,jobs);
			
			removeAllChilds("pages");
			removeAllChilds("nextprevious");
			myCurrent_page = pageInfo.current_page;
			document.getElementById("pages").appendChild(document.createTextNode("Page "+pageInfo.current_page+" of "+pageInfo.num_of_pages));
			nextPrevious = document.getElementById("nextprevious");
			
			if (pageInfo.current_page > 1){
				Aprevious = document.createElement("a");
				Aprevious.setAttribute('href','javascript:;');
				var functionFilter = "doFilter("+(pageInfo.current_page-1)+")";
				Aprevious.setAttribute('onclick', functionFilter);
				Aprevious.appendChild(document.createTextNode("previous"));
				nextPrevious.appendChild(Aprevious);
				nextPrevious.appendChild(document.createTextNode(" | "));
			}
			if ( pageInfo.current_page < pageInfo.num_of_pages ){
				if (pageInfo.current_page <= 1)
					nextPrevious.appendChild(document.createTextNode(" | "));
				Anext = document.createElement("a");
				Anext.setAttribute('href','javascript:;');
				var functionFilter = "doFilter("+(pageInfo.current_page+1)+")";
				Anext.setAttribute('onclick', functionFilter);
				Anext.appendChild(document.createTextNode("next"));
				nextPrevious.appendChild(Anext);	
			}
			
			//fix the permalink
			permalink();
    	}	
  	}
	var setupprojects = getSelectedChilds("SetupProject");
	var appVersions = getSelectedChilds("Version");
	
	var options = getSelectedChilds("Options");
	var cmts = getSelectedChilds("Platform");	

	// send the request the to server
	xmlhttp.open("GET", "https://alamages.cern.ch/django/lhcbPR/getFilters?page="+requested_page+"&app={{ active_tab }}"+"&appVersions="+escape(appVersions.join(","))+"&SetupProjects="+escape(setupprojects.join(","))+"&Options="+escape(options.join(","))+"&platforms="+escape(cmts.join(",")), true);
	xmlhttp.send();
	
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
					myInput.value = jsondata.platforms[i];
					myInput.setAttribute('readOnly','readonly');
					mybox.appendChild(myInput);
					mybox.appendChild(document.createTextNode(jsondata.platforms[i]));
					mybox.appendChild(document.createElement("br"));
					
			}
			myChoosedJob_id = job_id;
				$("#dialog").dialog({
    				resizable: false,
    				height: 700,
    				width: 950,
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

	$("#dialog").dialog("close");

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
					myInput.value = jsondata.platforms[i];
					
					mybox.appendChild(myInput);
					mybox.appendChild(document.createTextNode(jsondata.platforms[i]));
					mybox.appendChild(document.createElement("br"));
					
			}
				$("#cloneDialog").dialog({
    				resizable: false,
    				height: 700,
    				width: 600,
   					modal: true
				});
    	}	
  	}
	// send the request the to server
	xmlhttp.open("GET", "https://alamages.cern.ch/django/lhcbPR/getJobDetails?job_id="+job_id, true);
	xmlhttp.send();
	
	return;
}
function run(){
	alert("Run function, under construction...");
}
function uploadResults(){
	alert("Upload results function, under construction...");
}