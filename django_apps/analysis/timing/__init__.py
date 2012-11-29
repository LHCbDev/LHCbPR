"""
This the timing analysis page, more documentation will come
"""

title = 'Timing analysis'

import json, socket, os, random
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
from tools.viewTools import makeCheckedList, getSplitted2 
from query_builder import get_query_groups, get_tree_query

class GroupDict(dict):
    def __getitem__(self, key):
        if key not in self:
            self[key] = []
        return dict.__getitem__(self, key)       

def render(**kwargs):
    """From the url is takes the requested application(app_name) , example:
    /django/lhcbPR/jobDescriptions/BRUNEL ==> app_name = 'BRUNEL' 
    and depending on the app_name it returns the available versions, options, setupprojects"""
    app_name = kwargs['app_name']
    
    if not app_name == 'BRUNEL':
        return HttpResponse("<h3>Sorry this type of analysis is not supported for {0}  application</h3>".format(app_name))
    
    options = map(str, JobResults.objects.filter(job__jobDescription__application__appName=app_name,
                jobAttribute__group='TimingTree',
                job__success=True).values_list('job__jobDescription__options__description', flat=True).distinct())
    
    if not options:
        return HttpResponse("<h3>No proper timing results to generate tree timing analysis</h3>")
    
    
    options = Options.objects.filter(jobdescriptions__jobs__success=True,jobdescriptions__application__appName=app_name,
                                     jobdescriptions__jobs__jobresults__jobAttribute__group='TimingTree').distinct()
        
    versions_temp = Application.objects.filter(jobdescriptions__jobs__success=True, appName=app_name,
                                               jobdescriptions__jobs__jobresults__jobAttribute__group='TimingTree').distinct()
    versions = reversed(sorted(versions_temp, key = getSplitted2))
    
    platforms_temp = Platform.objects.filter(jobs__success=True,jobs__jobDescription__application__appName=app_name,
                                             jobs__jobresults__jobAttribute__group='TimingTree').distinct()
    platforms = sorted(platforms_temp, key = lambda plat : plat.cmtconfig)
     
    hosts_temp = Host.objects.filter(jobs__success=True,jobs__jobDescription__application__appName=app_name,
                                     jobs__jobresults__jobAttribute__group='TimingTree').distinct()
    hosts = sorted(hosts_temp, key = lambda host : host.hostname)
    
    dataDict = {
                'platforms' : platforms,
                'hosts' : hosts,
                'options' : options,
                'versions' : versions,
               }
      
    return dataDict

def analyse(**kwargs):
    #if request.method == 'GET' and 'hosts' in request.GET and 'jobdes' in request.GET and 'platforms' in request.GET and 'atr' in request.GET:
    #fetch the right queries depending on user's choices no the request
    requestData = kwargs['requestData']
    app_name = kwargs['app_name']
    
    query_groups = get_query_groups(requestData, app_name)
    #establish connection
    cursor = connection.cursor()
    
    #return { 'template' : 'analysis/debug.html', 'str' : query_groups }
    
    #execute query_groups get the logical groups of the data
    cursor.execute(query_groups)
    job_description = [col[0] for col in cursor.description]
    group_dict = GroupDict()
    
    result = cursor.fetchone()
    while not result == None:
        group_dict[ tuple(result[:-1]) ].append(result[-1])
        result = cursor.fetchone()
        
    #return { 'template' : 'analysis/debug.html', 'str' : group_dict }
    if len(group_dict) == 0: 
        return { 'template' : 'analysis/error.html' , 'errorMessage' : 'Your selections produce no results!' }
    if len(group_dict) > 1:
        resultos = [
                   dict(zip(job_description, key))
                   for key in group_dict.keys()
                   ]
        return { 'template' : 'analysis/render_pre.html', 
                'msg' : 'Your selection returned more than 1 results , can not generate timing tree!\\nAvailable logical groups:',
                'results' : json.dumps(resultos) }
    
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
    
    if settings.HOSTNAME == 'alamages':
        timing_path = 'static/images/histograms/timing{0}{1}{2}.json'.format(random.randint(1, 100), random.randint(1, 100),random.randint(1, 100))
    else:
        timing_path = 'static/timingJson/timing{0}{1}{2}.json'.format(random.randint(1, 100), random.randint(1, 100),random.randint(1, 100))
    
    jsonTree = tree.getHierarchicalJSON()
    f = open(os.path.join(settings.PROJECT_PATH, timing_path), 'w')
    f.write(jsonTree)
    f.close()
    
    dataDict = {
                'url' : '/'+timing_path, # json.dumps(jsonTree)
                'jobs_num' : len(job_ids),
                'description' : description_dict
               }
    
    return dataDict
    
def isAvailableFor(app_name):
    if app_name in [ 'BRUNEL' ]:
        return True
    
    return False