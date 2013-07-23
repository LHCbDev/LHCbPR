def get_data_query(requestData, app_name, job_list):
    select_statements = [
         'opt.description as OPTIONS',
         'plat.cmtconfig as PLATFORM',
         'h.hostname as HOST',
         'apl.appversion as VERSION',
         'att.name as NAME',
         'ROUND(AVG(rf.data), 2) AS AVERAGE',
         'ROUND(STDDEV(rf.data), 2) AS STDDEV',
         'count(*) as ENTRIES'
    ]
    from_statements = [
         'lhcbpr_job j',
         'lhcbpr_jobresults r',
         'lhcbpr_jobattribute att',
         'lhcbpr_platform plat',
         'lhcbpr_jobdescription jobdes', 
         'lhcbpr_application apl',
         'lhcbpr_options opt',
         'lhcbpr_host h'
    ]
    where_statements = [
         'j.id = r.job_id',
         'j.jobdescription_id = jobdes.id',
         'jobdes.application_id = apl.id',
         'jobdes.options_id = opt.id',
         'r.jobattribute_id = att.id',
         'rf.jobresults_ptr_id = r.id',
         'j.platform_id = plat.id',
         'j.host_id = h.id',
         'j.success = 1'
    ]
    group_statements = [
         'apl.appversion',
         'opt.description',
         'plat.cmtconfig',
         'att.name',
         'h.hostname'
    ]
    
    from_statements.append('lhcbpr_resultfloat rf')
    
    query_results    = ' SELECT ' + ' , '.join(select_statements)
    query_results   += ' FROM '   + ' , '.join(from_statements)
    query_results   += ' WHERE '  + ' and '.join(where_statements)

    secondpart_query = ""
    # Loop over job list
    if not job_list[0][0] == "":
        jobs_temp = []
        for j in job_list:
            jobs_temp.append("j.id = {0}".format(j[0]))
        secondpart_query += ' AND ( '+' OR '.join(jobs_temp)+' )'
        
    # Loop over Hosts
    #hosts = requestData['hosts'].split(',')
    #if not hosts[0] == "":
        #host_temp = []
        #for h in hosts:
            #host_temp.append("h.id = {0}".format(h))
        #secondpart_query += ' AND ( '+' OR '.join(host_temp)+' )'
        
    # Loop over Options
    #options = requestData['options'].split(',')
    #if not options[0] == "":
        #options_temp = []
        #for opt in options:
            #options_temp.append("opt.id = {0}".format(opt))
        #secondpart_query += ' AND ( '+' OR '.join(options_temp)+' )'

    # Loop over Versions
    #versions = requestData['versions'].split(',')
    #if not versions[0] == "":
        #versions_temp = []
        #for ver in versions:
            #versions_temp.append("apl.id = {0}".format(ver))
        #secondpart_query += ' AND ( '+' OR '.join(versions_temp)+' )'

    # Loop over Platforms
    #platforms = requestData['platforms'].split(',')
    #if not platforms[0] == "":
        #platforms_temp = []
        #for p in platforms:
            #platforms_temp.append("plat.id = {0}".format(p))
        #secondpart_query += ' AND ( '+' OR '.join(platforms_temp)+' )'

    grps = requestData['grps'].split(',')
    group_statements.append('att."GROUP"')
    secondpart_query += ' AND att."GROUP" = \'{0}\''.format(grps[0])
    
    # Add the second part of the query which contains the filtering
    query_results += secondpart_query
    query_results += ' GROUP BY ' + ' , '.join(group_statements)
    
    return query_results

def get_jobs_query(requestData):
    select_statements = [
         'distinct j.ID'
    ]
    from_statements = [
         'lhcbpr_job j',
         'lhcbpr_jobresults r',
         'lhcbpr_jobattribute att',
         'lhcbpr_platform plat',
         'lhcbpr_jobdescription jobdes', 
         'lhcbpr_application apl',
         'lhcbpr_options opt',
         'lhcbpr_host h'
    ]
    where_statements = [
         'j.id = r.job_id',
         'j.jobdescription_id = jobdes.id',
         'jobdes.application_id = apl.id',
         'jobdes.options_id = opt.id',
         'r.jobattribute_id = att.id',
         'j.platform_id = plat.id',
         'j.host_id = h.id',
         'j.success = 1'
    ]
    group_statements = [
         'j.id'
    ]
    
    query    = ' SELECT ' + ' , '.join(select_statements)
    query   += ' FROM '   + ' , '.join(from_statements)
    query   += ' WHERE '  + ' and '.join(where_statements)

    secondpart_query = ""
    # Loop over Hosts
    hosts = requestData['hosts'].split(',')
    if not hosts[0] == "":
        host_temp = []
        for h in hosts:
            host_temp.append("h.id = {0}".format(h))
        secondpart_query += ' AND ( '+' OR '.join(host_temp)+' )'
        
    # Loop over Options
    options = requestData['options'].split(',')
    if not options[0] == "":
        options_temp = []
        for opt in options:
            options_temp.append("opt.id = {0}".format(opt))
        secondpart_query += ' AND ( '+' OR '.join(options_temp)+' )'

    # Loop over Versions
    versions = requestData['versions'].split(',')
    if not versions[0] == "":
        versions_temp = []
        for ver in versions:
            versions_temp.append("apl.id = {0}".format(ver))
        secondpart_query += ' AND ( '+' OR '.join(versions_temp)+' )'

    # Loop over Platforms
    platforms = requestData['platforms'].split(',')
    if not platforms[0] == "":
        platforms_temp = []
        for p in platforms:
            platforms_temp.append("plat.id = {0}".format(p))
        secondpart_query += ' AND ( '+' OR '.join(platforms_temp)+' )'

    # Add the second part of the query which contains the filtering
    query += secondpart_query
    query += ' ORDER BY ' + ' , '.join(group_statements)
    
    return query

def get_tree_query(job_list, group):
    query = "SELECT \
        opt.description as OPTIONS, \
        plat.cmtconfig as PLATFORM, \
        h.hostname as HOST, \
        apl.appversion as VERSION, \
        att.name AS atr_name, \
        ROUND(AVG(attd.data), 3) AS float_data_avg, \
        ROUND(stddev(attd.data), 3) AS float_data_sdv, \
        count(*) as ENTRIES, \
        avg(resint.data) AS int_data, \
        min(resstr.data) AS str_data, \
        max(resint2.data) AS id_data \
        FROM lhcbpr_job j, \
        lhcbpr_jobresults r, \
        lhcbpr_jobattribute att, \
        lhcbpr_resultfloat attd, \
        lhcbpr_resultint resint, \
        lhcbpr_resultstring resstr, \
        lhcbpr_resultint resint2, \
        lhcbpr_application apl, \
        lhcbpr_jobdescription jobdes, \
        lhcbpr_host h, \
        lhcbpr_platform plat, \
        lhcbpr_options opt \
        WHERE j.id = r.job_id \
        AND apl.id = jobdes.application_id \
        AND jobdes.id = j.jobdescription_id \
        AND h.id = j.host_id \
        AND plat.id = j.PLATFORM_ID \
        AND opt.id = jobdes.OPTIONS_ID \
        AND r.jobattribute_id = att.id \
        AND attd.jobresults_ptr_id (+) = r.id \
        AND resint.jobresults_ptr_id (+) = r.id \
        AND resstr.jobresults_ptr_id (+) = r.id \
        AND resint2.jobresults_ptr_id (+) = r.id "

    if   group == 'Timing':
        query += "AND att.\"GROUP\" in ( 'Timing', 'TimingTree', 'TimingCount', 'TimingID')"
    elif group == 'TaskTiming':
        query += "AND att.\"GROUP\" in ( 'TaskTiming', 'TimingTree', 'TimingCount', 'TimingID')"
    else:
        query += "AND att.\"GROUP\" in ( '"
        query += group
        query += "')"

    jobs = []
    for id in job_list:
        jobs.append("j.id = {0}".format(id))

    query += ' and ( ' + ' or '.join(jobs) + ' ) ' 
    query += ' GROUP BY att.name, apl.appversion, h.hostname, opt.description, plat.cmtconfig'
    query += ' ORDER BY att.name'

    return query
