import json, socket
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
            # -3(version), -2(average value), -1(std)
            datatable_temp.append([ res[-4], float(res[-3]), float(res[-3])-float(res[-2]), float(res[-3])+float(res[-2]), 'info' , 'entries: {0}'.format(int(res[-1])) ])
        datatable = sorted(datatable_temp, key = lambda t : getSplitted(t[0]))
        dataDict['description'] = dict(zip([col[0] for col in cursor.description[:-4]], g))
        dataDict['platform'] = dataDict['description']['PLATFORM']
        dataDict['datatable'] = datatable
        
        trends.append(dataDict)
        
    return { 'trends': json.dumps(trends) }

def filterAtrs(**kargs):
    dataDict = kargs['requestData']
    app_name = kargs['app_name']
    
    filterGroups = Q()
    if not dataDict['groups'] == "": 
        filterGroups = makeQuery('jobAttribute__group__exact',dataDict['groups'].split(','), Q.OR)

    
    atrsTemp =  JobResults.objects.filter(job__jobDescription__application__appName=app_name,job__success=True).filter(Q(jobAttribute__type='Float')).filter(filterGroups)
    atrs = atrsTemp.values_list('jobAttribute__id','jobAttribute__name','jobAttribute__type').distinct()
    
    optionsHtml = '<label>Choose an attribute: </label><select id="atr"><option value=""></option>'
            
    for atr in atrs:
       optionsHtml+=  '<option value="{0},{1}">{2}</option>'.format(atr[0],atr[2],atr[1])
    
    optionsHtml+= '</select>'
     
    return HttpResponse(optionsHtml)

def isAvailableFor(app_name):
    return False