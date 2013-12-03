import json, math
from django.db import connection
from django.http import HttpResponse 
from lhcbPR.models import Application,  JobResults
from django.db.models import Q
from django.http import Http404

from tools.viewTools import getSplitted
import tools.socket_service as service
from query_builder import get_queries

class GroupDict(dict):
    def __getitem__(self, key):
        if key not in self:
            self[key] = []
        return dict.__getitem__(self, key)

def render(**kwargs):
    app_name = kwargs['app_name']
    
    apps = Application.objects.filter(appName__exact=app_name)
    if not apps:
        raise Http404     
    
    atrsTemp =  JobResults.objects.filter(job__jobDescription__application__appName=app_name,job__success=True).filter(Q(jobAttribute__type='Float'))
    atrs_temp = atrsTemp.values_list('jobAttribute__id','jobAttribute__name','jobAttribute__type','jobAttribute__group').distinct()
    atrs = []
    groups = {}
    types = {}
    for i, at in enumerate(atrs_temp):
        #if type in types
        if not at[2] in types:
            types[at[2]] = len(types)
        
        #if group in groups
        if not at[3] in groups:
            groups[at[3]] = len(groups)
        
        atrs.append([ at[0], at[1], types[at[2]], groups[at[3]] ])
        
        atrGroups = []
        for k, v in groups.iteritems():
            if k != "":
                atrGroups.append([k, v])

    dataDict = {
        'atrs'      : json.dumps(atrs),
        'atrGroups' : atrGroups,
        #get the reversed dictionaries
        'groups'    : json.dumps(dict((v,k) for k, v in groups.iteritems())),
        'types'     : json.dumps(dict((v,k) for k, v in types.iteritems()))  
    }
      
    return dataDict

def analyse(**kwargs):
    requestData = kwargs['requestData']
    app_name    = kwargs['app_name']

    axis = "unknown unit"
    
    #if request.method == 'GET' and 'hosts' in request.GET and 'jobdes' in request.GET and 'platforms' in request.GET and 'atr' in request.GET:
    #fetch the right queries depending on user's choices no the request
    query_results = get_queries(requestData, app_name)

    #establish connection
    cursor = connection.cursor()
                
    #then execute the next query_results to fetch the results
    cursor.execute(query_results)
    cursor_description = cursor.description
    
    groups = GroupDict()

    result = cursor.fetchone()
    while not result == None:
        group = tuple(result[:-4])
        if result[-3] != None and axis == "unknown unit":
            axis  = result[2]
        groups[group].append(tuple(result[-4:]))
        
        result = cursor.fetchone()
    
    trends = []
    for g,values in groups.iteritems():
        dataDict = {}
        datatable_temp = []
        for res in values:
            # -4(version), -3(average value), -2(std), -1 entries
            error = float(res[-2])/ math.sqrt( float(res[-1]) ) 
            version = res[-4]
            down_error = float(res[-3]) - error
            up_error = float(res[-3]) + error
            down_value = float(res[-3]) - float(res[-2])
            up_value = float(res[-3]) + float(res[-2])
            
            datatable_temp.append([ '{0}({1})'.format(version,res[-1]), down_value, down_error, up_error, up_value, 'Average: {0}, -+{1}'.format(res[-3],res[-2]) ])
        datatable_temp2 = sorted(datatable_temp, key = lambda t : getSplitted(t[0]))
        
        saved_index = None
        only_heads = True
        for index, dat in enumerate(datatable_temp2): 
            saved_index = index
            if dat[0].startswith('v'):
                only_heads = False
                break
        
        datatable = []
        if not only_heads:
            datatable.extend(datatable_temp2[saved_index:])
            datatable.extend(datatable_temp2[:saved_index])
        else:
            datatable = datatable_temp2
        
        dataDict['description']  = dict(zip([col[0] for col in cursor.description[:-4]], g))
        dataDict['platform']     = dataDict['description']['PLATFORM']
        dataDict['datatable']    = datatable
      	dataDict['axis']         = axis
        
        trends.append(dataDict)
        
    return { 'trends': json.dumps(trends) }

def isAvailableFor(app_name):
    return True
