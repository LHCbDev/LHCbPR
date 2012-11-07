import json, socket, os
from django.db import connection, transaction
from django.http import HttpResponse , HttpResponseRedirect
from django.shortcuts import render_to_response   
from django.template import RequestContext
from lhcbPR.models import HandlerResult, Host, JobDescription, Requested_platform, Platform, Application, Options, SetupProject, Handler, JobHandler, Job, JobResults, ResultString, ResultFloat, ResultInt, ResultBinary
from django.db.models import Q
from django.http import HttpResponseNotFound
from django.shortcuts import render_to_response   
from django.template import RequestContext
from django.conf import settings

import tools.socket_service as service
from tools.viewTools import dictfetchall
from tools.viewTools import makeCheckedList, getSplitted 
from query_builder import get_query_groups, get_tree_query

class GroupDict(dict):
    def __getitem__(self, key):
        if key not in self:
            self[key] = []
        return dict.__getitem__(self, key)       

def render(request, app_name):
    """From the url is takes the requested application(app_name) , example:
    /django/lhcbPR/jobDescriptions/BRUNEL ==> app_name = 'BRUNEL' 
    and depending on the app_name it returns the available versions, options, setupprojects"""
    
    if not app_name == 'BRUNEL':
        return HttpResponse("<h3>Sorry this type of analysis is not supported for {0}  application</h3>".format(app_name))
    
    applicationsList = list(Job.objects.filter(success=True).values_list('jobDescription__application__appName',flat=True).distinct())
    myauth = request.user.is_authenticated()     
    
    options = map(str, JobResults.objects.filter(job__jobDescription__application__appName=app_name,
                jobAttribute__group='TimingTree',
                job__success=True).values_list('job__jobDescription__options__description', flat=True).distinct())
    
    if not options:
        return HttpResponse("<h3>No proper timing results to generate tree timing analysis</h3>")
        
    versions_temp = map(str, JobResults.objects.filter(job__jobDescription__application__appName=app_name,
                jobAttribute__group='TimingTree',
                job__success=True).values_list('job__jobDescription__application__appVersion', flat=True).distinct())
    versions = reversed(sorted(versions_temp, key = getSplitted))

    platforms = map(str, JobResults.objects.filter(job__jobDescription__application__appName=app_name,
                    jobAttribute__group='TimingTree',
                    job__success=True).values_list('job__platform__cmtconfig', flat=True).distinct())
    platforms.sort()
     
    hosts = map(str, JobResults.objects.filter(job__jobDescription__application__appName=app_name,
                jobAttribute__group='TimingTree',
                job__success=True).values_list('job__host__hostname', flat=True).distinct())
    hosts.sort()
    
    if 'options' in request.GET:
        optionsList = makeCheckedList(options, request.GET['options'].split(','))
    else:
        optionsList = makeCheckedList(options)
    if 'versions' in request.GET:
        versionsList = makeCheckedList(versions, request.GET['versions'].split(','))
    else:
        versionsList = makeCheckedList(versions)
    if 'platforms' in request.GET:
        platformsList = makeCheckedList(platforms, request.GET['platforms'].split(','))
    else:
        platformsList = makeCheckedList(platforms)
    if 'hosts' in request.GET:
        hostsList = makeCheckedList(hosts, request.GET['hosts'].split(','))
    else:
        hostsList = makeCheckedList(hosts)  
    
    dataDict = {
                'platforms' : platformsList,
                'hosts' : hostsList,
                'options' : optionsList,
                'versions' : versionsList,
                'active_tab' : app_name ,
                'myauth' : myauth, 
                'user' : request.user, 
                'applications' : applicationsList,
               }
      
    return render_to_response('lhcbPR/analyse/timing/analyseTiming.html', 
                  dataDict,
                  context_instance=RequestContext(request))

def analyse(request):
    #if request.method == 'GET' and 'hosts' in request.GET and 'jobdes' in request.GET and 'platforms' in request.GET and 'atr' in request.GET:
    #fetch the right queries depending on user's choices no the request
    query_groups = get_query_groups(request)
    #return HttpResponse(json.dumps({ 'query_groups': query_groups }))
    #establish connection
    cursor = connection.cursor()
    
    #execute query_groups get the logical groups of the data
    cursor.execute(query_groups)
    job_description = [col[0] for col in cursor.description]
    group_dict = GroupDict()
    
    result = cursor.fetchone()
    while not result == None:
        group_dict[ tuple(result[:-1]) ].append(result[-1])
        result = cursor.fetchone()

    if len(group_dict) == 0: 
        return HttpResponse('</h3>Your selections produce no results!</h3>')
    if len(group_dict) > 1:
        return HttpResponse('</h3>Your selection returned more than 1 results , can not generate timing tree!</h3>')
    
    group , job_ids = group_dict.popitem()
    tree_query = get_tree_query(job_ids)
    
    description_dict = dict(zip(job_description, group)) 
    
    cursor.execute(tree_query)
    
    #its row has this format: ATR_NAME , FLOAT_DATA , INT_DATA, STR_DATA, ID_DATA
    # its node of tree we want to generate need the attibute name, its parent and its entries
    root = None
    node_data = {}
    node_entries = {}
    node_ids = {}
    node_childs = GroupDict()
    names = []
    
    result = cursor.fetchone()
    
    flag = False
    while not result == None:
        node_name = result[0]
        if '_parent' in node_name:
            parent = result[3]
            if parent == "None":
                root = node_name[:-7]
            else:
                node_childs[parent].append(node_name[:-7])  # STR_DATA
        elif '_count' in node_name:
            node_entries[node_name[:-6]] = int(result[2]) # INT_DATA
        elif '_id' in node_name:
            node_ids[node_name[:-3]] = int(result[4]) # ID_DATA
        else:
            node_data[node_name] = float(result[1]) # FLOAT_DATA
                    
        result = cursor.fetchone()
        
    from TimingTree import TimingTree
    
    tree = TimingTree(root, node_data, node_childs, node_entries, node_ids)
    
    timing_path = 'static/images/histograms/timing.json'
    settings
    
    yo = tree.getHierarchicalJSON()
    f = open(os.path.join(settings.PROJECT_PATH, timing_path), 'w')
    f.write(yo)
    f.close()
    
    myauth = request.user.is_authenticated()
    applicationsList = list(Job.objects.filter(success=True).values_list('jobDescription__application__appName',flat=True).distinct())
    
    dataDict = {
                'url' : '/'+timing_path,
                'active_tab' : 'BRUNEL' ,
                'myauth' : myauth, 
                'user' : request.user, 
                'jobs_num' : len(job_ids),
                'applications' : applicationsList,
                'description' : description_dict
               }
      
    return render_to_response('lhcbPR/analyse/timing/timingResults.html', 
                  dataDict,
                  context_instance=RequestContext(request))