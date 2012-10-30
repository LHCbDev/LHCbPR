from django.db import connection, transaction
from django.conf import settings
from django.http import HttpResponse 
from lhcbPR.models import HandlerResult, Host, JobDescription, Requested_platform, Platform, Application, Options, SetupProject, Handler, JobHandler, Job, JobResults, ResultString, ResultFloat, ResultInt, ResultBinary
import json, socket
import tools.analysis_engine as engine
import tools.socket_service as service

def get_queries(request):
    select_statements = ['apl.appversion as Version' , 'opt.description as Options' ]
    from_statements = [ 'lhcbpr_job j', 'lhcbpr_jobresults r', 'lhcbpr_jobattribute att', 
                     'lhcbpr_jobdescription jobdes', 'lhcbpr_application apl', 'lhcbpr_options opt' , 'lhcbpr_resultfile rf' ]
    where_statements = [ 'j.id = r.job_id',  'j.jobdescription_id = jobdes.id', 'jobdes.application_id = apl.id',
                    'jobdes.options_id = opt.id', 'r.jobattribute_id = att.id', 
                    'rf.jobresults_ptr_id = r.id' , 'j.success = 1' ]
    
    secondpart_query = ""
    use_host = False
    #check first which query to make , to join the host table or not
    hosts = request.GET['hosts'].split(',')
    if not hosts[0] == "":
        host_temp = []
        for h in hosts:
            host_temp.append("h.hostname = '"+h+"'")
        
        secondpart_query += ' AND ( '+' OR '.join(host_temp)+' )'
        #use the query which joins also the host table
        use_host = True
    
    use_platform = False
    platforms = request.GET['platforms'].split(',')
    if not platforms[0] == "":
        platforms_temp = []
        for p in platforms:
            platforms_temp.append("plat.cmtconfig = '"+p+"'")
        
        secondpart_query += ' AND ( '+' OR '.join(platforms_temp)+' )'
        use_platform = True
    
    
    if not request.GET['group_host'] == "true":
        if use_host:
            from_statements.append('lhcbpr_host h')
            where_statements.append('j.host_id = h.id')
    else:
        select_statements.append('h.hostname as Host')
        from_statements.append('lhcbpr_host h')
        where_statements.append('j.host_id = h.id')
        
    if not request.GET['group_platform'] == 'true':
        if use_platform:
            from_statements.append('lhcbpr_platform plat')
            where_statements.append('j.platform_id = plat.id')
    else:
        select_statements.append('plat.cmtconfig as Platform')
        from_statements.append('lhcbpr_platform plat')
        where_statements.append('j.platform_id = plat.id')
        
    query_results = 'select '+' , '.join(select_statements)+' ,rf. "FILE" from '+' , '.join(from_statements)+' where '+' and '.join(where_statements)
    query_groups = 'select distinct '+' , '.join(select_statements)+' from '+' , '.join(from_statements)+' where '+' and '.join(where_statements)
              
    options = request.GET['options'].split(',')
    if not options[0] == "":
        options_temp = []
        for opt in options:
            options_temp.append("opt.description = '"+opt+"'")
        
        secondpart_query += ' AND ( '+' OR '.join(options_temp)+' )'
    versions = request.GET['versions'].split(',')
    if not versions[0] == "":
        versions_temp = []
        for ver in versions:
            versions_temp.append("apl.appversion = '"+ver+"'")
        
        secondpart_query += ' AND ( '+' OR '.join(versions_temp)+' )'
        
    #now we finished generating the filtering in the query attributes
    #we know finalize the queries
    application_attribute= " and apl.appname='{0}'".format(request.GET['appName'])
    query_results += application_attribute
    query_groups += application_attribute
    
    #add the second part of the query which contains the filtering
    query_results += secondpart_query
    query_groups += secondpart_query
    
    return query_groups, query_results

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
        return HttpResponse(json.dumps({ 'error' : False , 'results' : [] }))
            
    #then execute the next query_results to fetch the results
    cursor.execute(query_results)
    #fixing the request in order to send it properly through socket
    #can not serialize straightforward the request as it is
    requestDict = {
                'atr_name' : request.GET['atr'].split(',')[0],
               'atr_path' : request.GET['atr'].split(',')[1], 
               'description' : [col[0] for col in cursor.description],
               'path_to_files' : settings.MEDIA_ROOT
               #'nbins' : request.GET['nbins'],
               #'xlow' : request.GET['xlow'],
               #'xup' : request.GET['xup'],
               }
    #initialize our remote service
    remoteservice = remoteService()
    #in case it does not connect return an error
    if not remoteservice.connect():
        return HttpResponse(json.dumps({'error' : True , 
                'errorMessage' : 'Connection with remote service for analysis failed!'}))
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
        #remoteservice.finish()
        #return HttpResponse()
        #after we finish sending our data we wait for the response(answer)
        answerDict = remoteservice.recv()
    except Exception:
        remoteservice.finish()
        return HttpResponse(json.dumps({'error' :True , 'errorMessage' : 'An error occurred with the root analysis process, please try again later'}))
    
    return HttpResponse(json.dumps({ 'error' : False , 'results' : answerDict['results'] }))