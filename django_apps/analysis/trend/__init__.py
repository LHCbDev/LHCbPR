import json, socket, math
from django.db import connection, transaction
from django.http import HttpResponse 
from lhcbPR.models import JobAttribute, Host, Platform, Application, Options,  JobResults
from django.db.models import Q
from django.http import HttpResponseNotFound
from django.shortcuts import render_to_response   
from django.template import RequestContext

from tools.viewTools import makeCheckedList, getSplitted, makeQuery
import tools.socket_service as service
from query_builder import get_queries

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
    
    apps = Application.objects.filter(appName__exact=app_name)
    if not apps:
        return HttpResponseNotFound("<h3>Page not found, no such application</h3>")     
    
    #Q(jobAttribute__type='Integer') | 
    atrsTemp =  JobResults.objects.filter(job__jobDescription__application__appName=app_name,job__success=True).filter(Q(jobAttribute__type='Float'))
    atrs = atrsTemp.values_list('jobAttribute__id','jobAttribute__name','jobAttribute__type').distinct()
    atrGroups = atrsTemp.values_list('jobAttribute__group', flat=True).distinct()

    options = Options.objects.filter(jobdescriptions__jobs__success=True,jobdescriptions__application__appName=app_name).distinct()
        
    versions_temp = Application.objects.filter(jobdescriptions__jobs__success=True, appName=app_name).distinct()
    versions = sorted(versions_temp, key = lambda ver : getSplitted(ver.appVersion), reverse = True)
    
    platforms_temp = Platform.objects.filter(jobs__success=True,jobs__jobDescription__application__appName=app_name).distinct()
    platforms = sorted(platforms_temp, key = lambda plat : plat.cmtconfig)
     
    hosts_temp = Host.objects.filter(jobs__success=True,jobs__jobDescription__application__appName=app_name).distinct()
    hosts = sorted(hosts_temp, key = lambda host : host.hostname)
    
    dataDict = { 'attributes' : atrs,
                'platforms' : platforms,
                'hosts' : hosts,
                'options' : options,
                'versions' : versions, 
                'atrGroups' : filter (lambda a: a != "", atrGroups)  
               }
      
    return dataDict

def analyse_1(**kwargs):
    requestData = kwargs['requestData']
    app_name = kwargs['app_name']
    
    #if request.method == 'GET' and 'hosts' in request.GET and 'jobdes' in request.GET and 'platforms' in request.GET and 'atr' in request.GET:
    #fetch the right queries depending on user's choices no the request
    query_groups, query_results = get_queries(requestData, app_name)
    
    #establish connection
    cursor = connection.cursor()
                
    #then execute the next query_results to fetch the results
    cursor.execute(query_results)
    cursor_description = cursor.description
    
    groups = GroupDict()

    result = cursor.fetchone()
    while not result == None:
        group = tuple(result[:-4])
        groups[group].append(tuple(result[-4:]))
        
        result = cursor.fetchone()
    
    trends = []
    for g,values in groups.iteritems():
        dataDict = {}
        datatable_temp = []
        for res in values:
            # -3(version), -2(average value), -1(std)
            datatable_temp.append([ res[-4], float(res[-3]), float(res[-3])-float(res[-2]), float(res[-3])+float(res[-2]), 'info' , 'entries: {0}'.format(int(res[-1])) ])
        datatable = sorted(datatable_temp, key = lambda t : getSplitted(t[0]))
        dataDict['description'] = dict(zip([col[0] for col in cursor.description[:-4]], g))
        dataDict['platform'] = dataDict['description']['PLATFORM']
        dataDict['datatable'] = datatable
        
        trends.append(dataDict)
        
    return { 'trends': json.dumps(trends) }

def analyse(**kwargs):
    requestData = kwargs['requestData']
    app_name = kwargs['app_name']
    
    #if request.method == 'GET' and 'hosts' in request.GET and 'jobdes' in request.GET and 'platforms' in request.GET and 'atr' in request.GET:
    #fetch the right queries depending on user's choices no the request
    query_groups, query_results = get_queries(requestData, app_name)
    
    #establish connection
    cursor = connection.cursor()
                
    #then execute the next query_results to fetch the results
    cursor.execute(query_results)
    cursor_description = cursor.description
    
    groups = GroupDict()

    result = cursor.fetchone()
    while not result == None:
        group = tuple(result[:-4])
        groups[group].append(tuple(result[-4:]))
        
        result = cursor.fetchone()
    
    trends = []
    for g,values in groups.iteritems():
        dataDict = {}
        datatable_temp = []
        for res in values:
            # -4(version), -3(average value), -2(std), -1 entries
            error = float(res[-2]) /  math.sqrt( float(res[-1]) ) 
            version = res[-4]
            down_value = float(res[-3]) - float(res[-2])
            down_error = float(res[-3]) - error
            up_error = float(res[-3]) + error
            up_value = float(res[-3]) + float(res[-2])
            
            datatable_temp.append([ version, down_value, down_error, up_error, up_value, 'Average: {0}, -+{1}'.format(res[-3],res[-2]) ])
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
        
        dataDict['description'] = dict(zip([col[0] for col in cursor.description[:-4]], g))
        dataDict['platform'] = dataDict['description']['PLATFORM']
        dataDict['datatable'] = datatable
        
        trends.append(dataDict)
        
    return { 'trends': json.dumps(trends) }

def filterAtrs(**kargs):
    dataDict = kargs['requestData']
    app_name = kargs['app_name']
    
    query_groups = "SELECT distinct att.id ,att.name, att.type FROM lhcbpr_job j ,\
    lhcbpr_jobresults r , lhcbpr_jobattribute att , lhcbpr_jobdescription jobdes ,\
    lhcbpr_application apl WHERE j.id = r.job_id AND j.jobdescription_id   = jobdes.id\
    AND jobdes.application_id = apl.id AND r.jobattribute_id = att.id\
    AND ( att.type = 'Float' ) AND j.success = 1\
    AND apl.appname = '{0}'".format(app_name)
    
    if not dataDict['groups'] == "":
        groups_temp = []
        for group in dataDict['groups'].split(','):
            groups_temp.append('att. "GROUP"='+"'{0}'".format(group))
        query_groups += ' AND ( '+' OR '.join(groups_temp)+' )'
    
    cursor = connection.cursor()
    cursor.execute(query_groups)
    
    optionsHtml = '<label>Choose an attribute: </label><select id="atr"><option value=""></option>'
    
    result = cursor.fetchone()
    while not result == None:
        optionsHtml+=  '<option value="{0},{1}">{2}</option>'.format(result[0],result[2],result[1])
        result = cursor.fetchone()
    
    optionsHtml+= '</select>'
     
    return HttpResponse(optionsHtml)

def isAvailableFor(app_name):
    return True