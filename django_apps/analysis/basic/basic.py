import json, socket
from django.db import connection, transaction
from django.http import HttpResponse 
from lhcbPR.models import JobAttribute, Host, Platform, Application, Options,  JobResults
from django.db.models import Q
from django.http import HttpResponseNotFound
from django.shortcuts import render_to_response   
from django.template import RequestContext

from tools.viewTools import makeCheckedList, getSplitted2, makeQuery
import tools.socket_service as service
from query_builder import get_queries

class remoteService(object):
    def __init__(self):
        self.connection = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
    def connect(self):
        try:
            self.connection.connect(("localhost", 4321))
        except Exception:
            return False
        else:
            return True
    def send(self, data):
        service.send(self.connection, data)
    def recv(self):
        return service.recv(self.connection)
    def finish(self):
        self.connection.close()
        

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
    versions = reversed(sorted(versions_temp, key = getSplitted2))
    
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
    
    #execute query_groups get the logical groups of the data
    cursor.execute(query_groups)
    logical_data_groups = cursor.fetchall()
    
    if len(logical_data_groups) == 0: 
        return { 'error' : json.dumps(False) , 'results' : [] , 'histogram' : False, }
    if len(logical_data_groups) > 3:
        if requestData['histogram'] == "true":
            return {'errorMessage' : 'Your choices returned more than 3 results.Can not generate histograms for more than 3 results!',
                'template' : 'analysis/error.html' }
    
    if requestData['histogram'] == 'true':
        doHistogram = True
    else:
        doHistogram = False
    if requestData['separately_hist'] == 'true':
        doSeparate = True
    else:
        doSeparate = False
            
    #then execute the next query_results to fetch the results
    cursor.execute(query_results)
    #fixing the request in order to send it properly through socket
    #can not serialize straightforward the request as it is
    yo = JobAttribute.objects.get(pk=requestData['atr'].split(',')[0])
    requestDict = {
               'atr' : yo.name, 
               'description' : [col[0] for col in cursor.description],
               'nbins' : requestData['nbins'],
               'xlow' : requestData['xlow'],
               'xup' : requestData['xup'],
               'separately_hist' : doSeparate,
               'histogram' : doHistogram 
               }
    #initialize our remote service
    remoteservice = remoteService()
    #in case it does not connect return an error
    if not remoteservice.connect():
        return { 'errorMessage' : 'Connection with remote service for analysis failed!', 
                'template' : 'analysis/error.html' }
    try:
        #send the name of the function you want to call
        remoteservice.send('basic_service')
        #send to ROOT_service(remote service) histogram info from user's request
        remoteservice.send(requestDict)
        groups = {}
    
        result = cursor.fetchone()
        while not result == None:
            group = tuple(result[:-1])
            if not group in groups:
                groups[group] = len(groups)
                remoteservice.send(('NEWGROUP', groups[group], group))
            remoteservice.send((groups[group], result[-1]))
            result = cursor.fetchone()
        #send a message to stop waiting for other packets    
        remoteservice.send('STAHP')
        #after we finish sending our data we wait for the response(answer)
        answerDict = remoteservice.recv()
    except Exception:
        return {'errorMessage' : 'An error occurred with the root analysis process, please try again later',
                'template' : 'analysis/error.html' }
    error = False
    return { 'results' : json.dumps(answerDict['results']) , 'histogram' : json.dumps(doHistogram), 
                'separately_hist' : json.dumps(doSeparate), 'bins' : answerDict['bins'] }

def filterAtrs(**kargs):
    dataDict = kargs['requestData']
    app_name = kargs['app_name']
    
    filterGroups = Q()
    if not dataDict['groups'] == "": 
        filterGroups = makeQuery('jobAttribute__group__exact',dataDict['groups'].split(','), Q.OR)

    
    atrsTemp =  JobResults.objects.filter(job__jobDescription__application__appName=app_name,job__success=True).filter(Q(jobAttribute__type='Float')).filter(filterGroups)
    atrs = atrsTemp.values_list('jobAttribute__id','jobAttribute__name','jobAttribute__type').distinct()
    
    optionsHtml = '' 
    
    for atr in atrs:
       optionsHtml+=  '<option value="{0},{1}">{2}</option>'.format(atr[0],atr[2],atr[1])
    
       
    return HttpResponse(optionsHtml)