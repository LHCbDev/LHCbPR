"""
This the timing analysis page, more documentation will come
"""

title = 'Timing analysis'

import json, socket, os, random
from django.db import connection
from django.http import HttpResponse   
from lhcbPR.models import Host, Platform, Application, Options, JobResults
from django.conf import settings

from tools.viewTools import getSplitted 
from query_builder import get_query_groups, get_tree_query


class GroupDict(dict):
    def __getitem__(self, key):
        if key not in self:
            self[key] = []
        return dict.__getitem__(self, key)       

def render(**kwargs):
    app_name = kwargs['app_name']
    
    options = map(str, JobResults.objects.filter(job__jobDescription__application__appName=app_name,
                jobAttribute__group='TimingTree',
                job__success=True).values_list('job__jobDescription__options__description', flat=True).distinct())
    
    if not options:
        return { "template" : "analysis/error.html", "errorMessage" : "No proper timing results to generate tree timing analysis" }
    
    
    options = Options.objects.filter(jobdescriptions__jobs__success=True,jobdescriptions__application__appName=app_name,
                                     jobdescriptions__jobs__jobresults__jobAttribute__group='TimingTree').distinct().order_by('description')
        
    versions_temp = Application.objects.filter(jobdescriptions__jobs__success=True, appName=app_name,
                                               jobdescriptions__jobs__jobresults__jobAttribute__group='TimingTree').distinct()
    versions = sorted(versions_temp, key = lambda ver : getSplitted(ver.appVersion), reverse = True)
    
    platforms = Platform.objects.filter(jobs__success=True,jobs__jobDescription__application__appName=app_name,
                                             jobs__jobresults__jobAttribute__group='TimingTree').distinct().order_by('cmtconfig')
     
    hosts = Host.objects.filter(jobs__success=True,jobs__jobDescription__application__appName=app_name,
                                     jobs__jobresults__jobAttribute__group='TimingTree').distinct().order_by('hostname')
    
    dataDict = {
                'platforms' : platforms,
                'hosts' : hosts,
                'options' : options,
                'versions' : versions,
               }
      
    return dataDict

def makeTreeMap(node_name, finalnodes, lastparent, node_data, node_childs):     
    current_node = node_name
    finalnodes.append([ node_name, lastparent, node_data[node_name] ])
    
    if node_name in node_childs:
        lastparent = current_node
        for child in node_childs[node_name]:
            makeTreeMap(child, finalnodes, lastparent, node_data, node_childs)
    else:
          return

def analyse(**kwargs):
    #return {}
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
    
    #return { 'template' : 'analysis/error.html' , 'errorMessage' : tree_query }
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
    
    myitems = node_childs.iteritems()
    
    for parent, childs in myitems:
        child_list = childs
        node_childs[parent] = sorted(child_list, key = lambda mykey : node_ids[mykey])
    
    if requestData['treeMap'] == "true":
        treeList = []
        treeList.append(['Algorithm', 'Parent', 'Time'])
        
        makeTreeMap(root, treeList, None, node_data, node_childs)
        
        return {'template' : 'analysis/timing/analyseTreeMap.html' , 'treeData' : json.dumps(treeList), 'perDict' : json.dumps({}), 'tooltip' : "false"}
       
    from TimingTree import TimingTree
    
    tree = TimingTree(root, node_data, node_childs, node_entries, node_ids)
    
    if requestData['singleLevel'] == "true":
        actualTimeTree, perTotalDict = tree.getActualTimeTree()
        
        return {'template' : 'analysis/timing/analyseTreeMap.html' , 'treeData' : json.dumps(actualTimeTree), 'perDict' : json.dumps(perTotalDict), 'tooltip' : "true"}
    
    if settings.HOSTNAME == 'alamages':
        timing_path = 'static/images/histograms/timing{0}{1}{2}.csv'.format(random.randint(1, 100), random.randint(1, 100),random.randint(1, 100))
    else:
        timing_path = 'static/timingJson/timing{0}{1}{2}.csv'.format(random.randint(1, 100), random.randint(1, 100),random.randint(1, 100))
    
    #this was previously used to generate the tree using easyui
    jsonTree = tree.getHierarchicalJSON()
    #jsonTree = tree.getjqGrid()
    csv = tree.getFullCSV()
    
    #csv = tree.getActualTimeTree()
    f = open(os.path.join(settings.PROJECT_PATH, timing_path), 'w')
    f.write(csv)
    f.close()
    
    #return { 'template' : 'analysis/pre.html' , 'pre' : jsonTree }
    
    dataDict = {
                'csv_url' : settings.ROOT_URL+timing_path,
                'data' : jsonTree,
                'jobs_num' : len(job_ids),
                'description' : description_dict
               }
    
    return dataDict
    
def isAvailableFor(app_name):
    if app_name in [ 'BRUNEL', 'GAUSS', 'MOORE' ]:
        return True
    
    return False