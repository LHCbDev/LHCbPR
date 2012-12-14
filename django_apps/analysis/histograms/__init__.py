"""
In this histogram analysis the "attribute" represents a title of a histogram inside the collected Gauss root files. The user can choose a histogram(attribute) and by clicking on the "retrieve results"
he will get the sum of  histograms for each logical group(options-version...) the user defined.

If the user leaves the selection checkboxes(options,version..) blank the page will generate the sum of histograms for all the available logical groups , may take long time)

A logical group is defined by a combination of options - version - platform(optional) - host(optional) , so the user can define for which versions, options etc he wants to see the sum(summary) of the histograms.

The page is still under construction, this is a demo(not the finished version)
"""

title = 'Histogram analysis'

import json, socket
from django.db import connection, transaction
from django.http import HttpResponse 
from lhcbPR.models import Host, Platform, Application, Options, JobResults
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponseNotFound

import tools.socket_service as service
from query_builder import get_queries
from tools.viewTools import getSplitted 

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
    if not app_name == 'GAUSS':
        return HttpResponseNotFound("<h3>Histogram analysis is not yet supported for {0} application</h3>".format(app_name))
    
    if not JobResults.objects.filter(job__jobDescription__application__appName=app_name,jobAttribute__type='File').count() > 0:
        return HttpResponse('<h3>Not root files were saved</h3>')  
    
    #atrs = map(str, JobResults.objects.filter(job__jobDescription__application__appName__exact=app_name).values_list('jobAttribute__name', flat=True).distinct())
    atrs =  [ (k, v) for k, v in settings.HISTOGRAMSGAUSS.iteritems() ]
    
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
               }
      
    return dataDict

def analyse(**kwargs):
    requestData = kwargs['requestData']
    app_name = kwargs['app_name']
    #if request.method == 'GET' and 'hosts' in request.GET and 'jobdes' in request.GET and 'platforms' in request.GET and 'atr' in request.GET:
    #fetch the right queries depending on user's choices no the request
    query_groups, query_results = get_queries(requestData, app_name)
    
    #return {'template' : 'analysis/debug.html', 
    #        'query_groups' : query_groups , 'query_results' : query_results }
    
    #establish connection
    cursor = connection.cursor()
    
    #execute query_groups get the logical groups of the data
    cursor.execute(query_groups)
    logical_data_groups = cursor.fetchall()
    
    if len(logical_data_groups) == 0: 
        return {'errorMessage' : 'No results found for your choices.',
                'template' : 'analysis/error.html' }
    if len(logical_data_groups) < 2:
        if requestData['hist_divided'] == 'true':
            return {'errorMessage' : 'Your choices produce less than 2 results!\nCan not divide 1 histogram.',
                'template' : 'analysis/error.html' }
    if len(logical_data_groups) > 2:
        if requestData['hist_divided'] == 'true':
            return {'errorMessage' : 'Your choices produce more than 2 results!\nCan not divide more than 2 histograms.',
                'template' : 'analysis/error.html' }
    if len(logical_data_groups) > 3:
        if requestData['hist_imposed'] == 'true':
            return {'errorMessage' : 'Your choices produce more than 3 results!\nCan not impose more than 3 histograms.',
                'template' : 'analysis/error.html' }
    
    if requestData['hist_separated'] == 'true':
        hist_separated = True
    else:
        hist_separated = False
    if requestData['hist_imposed'] == 'true':
        hist_imposed = True
    else:
        hist_imposed = False
    if requestData['hist_divided'] == 'true':
        hist_divided = True
    else:
        hist_divided = False
    if requestData['hist_divided_reversed'] == 'true':
        hist_divided_reversed = True
    else:
        hist_divided_reversed = False
        
          
    #then execute the next query_results to fetch the results
    cursor.execute(query_results)
    #fixing the request in order to send it properly through socket
    #can not serialize straightforward the request as it is
    requestDict = {
                'atr_name' : requestData['atr'].split(',')[0],
               'atr_path' : requestData['atr'].split(',')[1], 
               'description' : [col[0] for col in cursor.description],
               'path_to_files' : settings.MEDIA_ROOT,
               'hist_separated' : hist_separated,
               'hist_imposed' : hist_imposed,
               'hist_divided' : hist_divided,
               'hist_divided_reversed' : hist_divided_reversed,
               'hist_options' : settings.HISTOGRAMSGAUSSOPTIONS 
               }
    #initialize our remote service
    remoteservice = remoteService()
    #in case it does not connect return an error
    if not remoteservice.connect():
        return {'errorMessage' : 'Connection with remote service for analysis failed!',
                'template' : 'analysis/error.html' }
        
    try:
        remoteservice.send('histograms_service')
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
        remoteservice.finish()
        return {'errorMessage' : 'An error occurred with the root analysis process, please try again later',
                'template' : 'analysis/error.html' }
    
    return { 'results' : json.dumps(answerDict['results']), 'hist_separated' : json.dumps(hist_separated),
            'hist_imposed' : json.dumps(hist_imposed), 'hist_divided' : json.dumps(hist_divided),
            'host_divided_reversed' : json.dumps(hist_divided_reversed) }
    
def isAvailableFor(app_name):
    if app_name in ['GAUSS']:
        return True
    
    return False