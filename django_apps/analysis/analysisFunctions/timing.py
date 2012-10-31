from django.db import connection, transaction
from django.http import HttpResponse , HttpResponseRedirect
from django.shortcuts import render_to_response   
from django.template import RequestContext
from lhcbPR.models import HandlerResult, Host, JobDescription, Requested_platform, Platform, Application, Options, SetupProject, Handler, JobHandler, Job, JobResults, ResultString, ResultFloat, ResultInt, ResultBinary
import json, socket
import tools.analysis_engine as engine
import tools.socket_service as service
from tools.viewTools import dictfetchall

def get_query_groups(request):
    select_statements = ['apl.appversion as Version' , 'opt.description as Options', 'plat.cmtconfig as Platform' ]
    from_statements = [ 'lhcbpr_job j', 'lhcbpr_jobresults r', 'lhcbpr_jobattribute att', 
                   'lhcbpr_platform plat',  'lhcbpr_jobdescription jobdes', 
                   'lhcbpr_application apl', 'lhcbpr_options opt'  ]
    where_statements = [ 'j.id = r.job_id',  'j.jobdescription_id = jobdes.id', 'jobdes.application_id = apl.id',
                    'jobdes.options_id = opt.id', 'r.jobattribute_id = att.id', 
                    'j.platform_id = plat.id' , 'j.success = 1' , ' att . '+'"GROUP"'+" = 'TimingTree'"]
    
    
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
    
    if not request.GET['group_host'] == "true":
        if use_host:
            from_statements.append('lhcbpr_host h')
            where_statements.append('j.host_id = h.id')
    else:
        select_statements.append('h.hostname as Host')
        from_statements.append('lhcbpr_host h')
        where_statements.append('j.host_id = h.id')
    
    query_groups = 'select distinct '+' , '.join(select_statements)+', j.id as job_id from '+' , '.join(from_statements)+' where '+' and '.join(where_statements)
              
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
    platforms = request.GET['platforms'].split(',')
    if not platforms[0] == "":
        platforms_temp = []
        for p in platforms:
            platforms_temp.append("plat.cmtconfig = '"+p+"'")
        
        secondpart_query += ' AND ( '+' OR '.join(platforms_temp)+' )'
        
    #now we finished generating the filtering in the query attributes
    #we know finalize the queries
    #we add the application name 
    query_groups += " and apl.appname='{0}'".format(request.GET['appName'])
    
    #add the second part of the query which contains the filtering
    query_groups += secondpart_query
    
    return query_groups

def get_tree_query(job_ids_list):
    tree_query = "SELECT att.name AS atr_name, \
  ROUND(AVG(attd.data), 3) AS float_data, \
  avg(resint.data) AS int_data, \
  min(resstr.data) AS str_data \
    FROM lhcbpr_job j, \
  lhcbpr_jobresults r, \
  lhcbpr_jobattribute att, \
  lhcbpr_resultfloat attd, \
  lhcbpr_resultint resint, \
  lhcbpr_resultstring resstr \
    WHERE j.id = r.job_id \
    AND r.jobattribute_id = att.id \
    AND attd.jobresults_ptr_id (+) = r.id \
    AND resint.jobresults_ptr_id (+) = r.id \
    AND resstr.jobresults_ptr_id (+) = r.id \
    AND att ."+' "GROUP" ' +"in ( 'Timing', 'TimingTree', 'TimingCount')"
    
    jobids = []
    for id in job_ids_list:
        jobids.append("j.id = {0}".format(id))
    
    tree_query += 'and ( '+ ' or '.join(jobids) +' ) GROUP BY att.name;'
    
    return tree_query

class GroupDict(dict):
    def __getitem__(self, key):
        if key not in self:
            self[key] = []
        return dict.__getitem__(self, key)       

def analyse(request):
    #if request.method == 'GET' and 'hosts' in request.GET and 'jobdes' in request.GET and 'platforms' in request.GET and 'atr' in request.GET:
    #fetch the right queries depending on user's choices no the request
    query_groups = get_query_groups(request)
    #return HttpResponse(json.dumps({ 'query_groups': query_groups }))
    #establish connection
    cursor = connection.cursor()
    
    #execute query_groups get the logical groups of the data
    cursor.execute(query_groups)
    des = [col[0] for col in cursor.description]
    group_dict = GroupDict()
    
    result = cursor.fetchone()
    while not result == None:
        group_dict[ tuple(result[:-1]) ].append(result[-1])
        result = cursor.fetchone()

    if len(group_dict) == 0: 
        return HttpResponse('</h3>Your selections produce no results!</h3>')
    if len(group_dict) > 1:
        return HttpResponse('</h3>Your selection returned more than 1 results , can not generate timing tree!</h3>')
    
    description , job_ids = group_dict.popitem()
    tree_query = get_tree_query(job_ids)
    
    cursor.execute(tree_query)
    
    #its row has this format: ATR_NAME , FLOAT_DATA , INT_DATA, STR_DATA
    # its node of tree we want to generate need the attibute name, its parent and its entries
    root = None
    node_data = {}
    node_childs = GroupDict()
    node_entries = {}
    
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
        else:
            node_data[node_name] = float(result[1]) # FLOAT_DATA
                    
        result = cursor.fetchone()
        
    from tools.TimingTree import TimingTree
    
    tree = TimingTree(root, node_data, node_childs, node_entries)
    
    #yo = tree.getFlatJSON()
    yo = tree.getHierarchicalJSON()
    f = open('/afs/cern.ch/user/e/ekiagias/workspace/LHCbPR/django_apps/static/images/histograms/timing.json', 'w')
    f.write(yo)
    f.close()
    #return HttpResponse(json.dumps({'aw' : yo}))
    
    myauth = request.user.is_authenticated()
    applicationsList = list(Job.objects.filter(success=True).values_list('jobDescription__application__appName',flat=True).distinct())
    
    dataDict = {
                'url' : '/static/images/histograms/timing.json',
                'active_tab' : 'BRUNEL' ,
                'myauth' : myauth, 
                'user' : request.user, 
                'jobs_num' : len(job_ids),
                'applications' : applicationsList,
               }
      
    return render_to_response('lhcbPR/analyse/timingResults.html', 
                  dataDict,
                  context_instance=RequestContext(request))
    
    #return HttpResponse(yo, mimetype="text/plain")