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
  min(resstr.data) AS str_data, \
  max(resint2.data) AS id_data \
    FROM lhcbpr_job j, \
  lhcbpr_jobresults r, \
  lhcbpr_jobattribute att, \
  lhcbpr_resultfloat attd, \
  lhcbpr_resultint resint, \
  lhcbpr_resultstring resstr, \
  lhcbpr_resultint resint2 \
    WHERE j.id = r.job_id \
    AND r.jobattribute_id = att.id \
    AND attd.jobresults_ptr_id (+) = r.id \
    AND resint.jobresults_ptr_id (+) = r.id \
    AND resstr.jobresults_ptr_id (+) = r.id \
    AND resint2.jobresults_ptr_id (+) = r.id \
    AND att ."+' "GROUP" ' +"in ( 'Timing', 'TimingTree', 'TimingCount', 'TimingID')"
    
    jobids = []
    for id in job_ids_list:
        jobids.append("j.id = {0}".format(id))
    
    tree_query += 'and ( '+ ' or '.join(jobids) +' ) GROUP BY att.name;'
    
    return tree_query