import json, socket
from django.db import connection, transaction
from django.http import HttpResponse 
from lhcbPR.models import HandlerResult, Host, JobDescription, Requested_platform, Platform, Application, Options, SetupProject, Handler, JobHandler, Job, JobResults, ResultString, ResultFloat, ResultInt, ResultBinary
from django.db.models import Q
from django.http import HttpResponseNotFound
from django.shortcuts import render_to_response   
from django.template import RequestContext

from tools.viewTools import makeCheckedList, getSplitted 
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
        

def render(request, app_name):
    """From the url is takes the requested application(app_name) , example:
    /django/lhcbPR/jobDescriptions/BRUNEL ==> app_name = 'BRUNEL' 
    and depending on the app_name it returns the available versions, options, setupprojects"""
    
    applicationsList = list(Job.objects.filter(success=True).values_list('jobDescription__application__appName',flat=True).distinct())
    myauth = request.user.is_authenticated()
    
    apps = Application.objects.filter(appName__exact=app_name)
    if not apps:
        return HttpResponseNotFound("<h3>Page not found, no such application</h3>")     
    
    #atrs = map(str, JobResults.objects.filter(job__jobDescription__application__appName__exact=app_name).values_list('jobAttribute__name', flat=True).distinct())
    atrs =  JobResults.objects.filter(job__jobDescription__application__appName=app_name,job__success=True).filter(Q(jobAttribute__type='Int') | Q(jobAttribute__type='Float')).values_list('jobAttribute__name','jobAttribute__type').distinct()
    
    options = map(str, Job.objects.filter(jobDescription__application__appName=app_name,success=True).values_list('jobDescription__options__description', flat=True).distinct())
        
    versions_temp = map(str, Job.objects.filter(jobDescription__application__appName=app_name,success=True).values_list('jobDescription__application__appVersion', flat=True).distinct())
    versions = reversed(sorted(versions_temp, key = getSplitted))

    platforms = map(str, Job.objects.filter(jobDescription__application__appName=app_name,success=True).values_list('platform__cmtconfig', flat=True).distinct())
    platforms.sort()
     
    hosts = map(str, Job.objects.filter(jobDescription__application__appName=app_name,success=True).values_list('host__hostname', flat=True).distinct())
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
    
    dataDict = { 'attributes' : atrs,
                'platforms' : platformsList,
                'hosts' : hostsList,
                'options' : optionsList,
                'versions' : versionsList,
                'active_tab' : app_name ,
                'myauth' : myauth, 
                'user' : request.user, 
                'applications' : applicationsList,
               }
      
    return render_to_response('lhcbPR/analyse/basic/analyseBasic.html', 
                  dataDict,
                  context_instance=RequestContext(request))

def analyse(request):
    #if request.method == 'GET' and 'hosts' in request.GET and 'jobdes' in request.GET and 'platforms' in request.GET and 'atr' in request.GET:
    #fetch the right queries depending on user's choices no the request
    query_groups, query_results = get_queries(request)
    
    #establish connection
    cursor = connection.cursor()
    
    #execute query_groups get the logical groups of the data
    cursor.execute(query_groups)
    logical_data_groups = cursor.fetchall()
    
    if len(logical_data_groups) == 0: 
        return HttpResponse(json.dumps({ 'error' : False , 'results' : [] , 'histogram' : False, }))
    if len(logical_data_groups) > 3:
        if request.GET['histogram'] == "true":
            return HttpResponse(json.dumps({'error' : True , 
                'errorMessage' : 'Your choices returned more than 3 results.Can not generate histograms for more than 3 results!'}))
    
    if request.GET['histogram'] == 'true':
        doHistogram = True
    else:
        doHistogram = False
    if request.GET['separately_hist'] == 'true':
        doSeparate = True
    else:
        doSeparate = False
            
    #then execute the next query_results to fetch the results
    cursor.execute(query_results)
    #fixing the request in order to send it properly through socket
    #can not serialize straightforward the request as it is
    requestDict = {
               'atr' : request.GET['atr'].split(',')[0], 
               'description' : [col[0] for col in cursor.description],
               'nbins' : request.GET['nbins'],
               'xlow' : request.GET['xlow'],
               'xup' : request.GET['xup'],
               'separately_hist' : doSeparate,
               'histogram' : doHistogram 
               }
    #initialize our remote service
    remoteservice = remoteService()
    #in case it does not connect return an error
    if not remoteservice.connect():
        return HttpResponse(json.dumps({'error' : True , 
                'errorMessage' : 'Connection with remote service for analysis failed!'}))
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
        return HttpResponse(json.dumps({'error' :True , 'errorMessage' : 'An error occurred with the root analysis process, please try again later'}))
    
    return HttpResponse(json.dumps({ 'error' : False , 'results' : answerDict['results'] , 'histogram' : doHistogram, 
                                    'separately_hist' : doSeparate, 'bins' : answerDict['bins'] }))