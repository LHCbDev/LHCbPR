import json, logging
from django.db import connection, transaction
from django.http import HttpResponse, Http404
from lhcbPR.models import JobAttribute, Application,  JobResults
from django.db.models import Q   
from tools.viewTools import getSplitted, subService as service
from query_builder import get_queries

logger = logging.getLogger('analysis_logger')     

def render(**kwargs):
    """From the url is takes the requested application(app_name) , example:
    /django/lhcbPR/jobDescriptions/BRUNEL ==> app_name = 'BRUNEL' 
    and depending on the app_name it returns the available versions, options, setupprojects"""
    app_name = kwargs['app_name']
    
    apps = Application.objects.filter(appName__exact=app_name)
    if not apps:
        raise Http404  
    
    #Q(jobAttribute__type='Integer') | 
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
            
    
    dataDict = {#filter (lambda a : a != "", groups.keys())
                'atrs' : json.dumps(atrs),
                'atrGroups' : atrGroups,
                #get the reversed dictionaries
                'groups' : json.dumps(dict((v,k) for k, v in groups.iteritems())),
                'types' : json.dumps(dict((v,k) for k, v in types.iteritems()))  
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
        return { 'errorMessage' : 'No results produced from you choices', 'template' : 'analysis/error.html' }
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
    remoteservice = service()
    #in case it does not connect return an error
    if not remoteservice.connect():
        logger.error('Could not connect to remote service')
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
    except Exception, e:
        logger.exception()
        return {'errorMessage' : 'An exception occurred please try again later',
                'template' : 'analysis/error.html' }
        #return {'errorMessage' : 'An error occurred with the root analysis process, please try again later',
        #        'template' : 'analysis/error.html' }
    error = False
    return { 'results' : json.dumps(answerDict['results']) , 'histogram' : json.dumps(doHistogram), 
                'separately_hist' : json.dumps(doSeparate), 'bins' : answerDict['bins'] }
