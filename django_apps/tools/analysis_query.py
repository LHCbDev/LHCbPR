def get_queries(request):
    select_statements = ['apl.appversion as Version' , 'opt.description as Options', 'plat.cmtconfig as Platform' ]
    from_statements = [ 'lhcbpr_job j', 'lhcbpr_jobresults r', 'lhcbpr_jobattribute att', 
                   'lhcbpr_platform plat',  'lhcbpr_jobdescription jobdes', 
                   'lhcbpr_application apl', 'lhcbpr_options opt'  ]
    where_statements = [ 'j.id = r.job_id',  'j.jobdescription_id = jobdes.id', 'jobdes.application_id = apl.id',
                    'jobdes.options_id = opt.id', 'r.jobattribute_id = att.id', 
                    'rf.jobresults_ptr_id = r.id', 'j.platform_id = plat.id' ]
    
    if request.GET['atr'].split(',')[1] == 'Float':
        from_statements.append('lhcbpr_resultfloat rf')
    else:
        from_statements.append('lhcbpr_resultint rf')
    
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
        
    query_results = 'select '+' , '.join(select_statements)+' ,rf.data from '+' , '.join(from_statements)+' where '+' and '.join(where_statements)
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
    platforms = request.GET['platforms'].split(',')
    if not platforms[0] == "":
        platforms_temp = []
        for p in platforms:
            platforms_temp.append("plat.cmtconfig = '"+p+"'")
        
        secondpart_query += ' AND ( '+' OR '.join(platforms_temp)+' )'
        
    #now we finished generating the filtering in the query attributes
    #we know finalize the queries
    application_attribute= " and apl.appname='{0}' and att.name='{1}'".format(request.GET['appName'], request.GET['atr'].split(',')[0])
    query_results += application_attribute
    query_groups += application_attribute
    
    #add the second part of the query which contains the filtering
    query_results += secondpart_query
    query_groups += secondpart_query
    
    return query_groups, query_results