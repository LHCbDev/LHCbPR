import json
from django.db import connection
from django.http import Http404
from lhcbPR.models import JobAttribute, Application
from django.db.models import Q   
from tools.viewTools import getSplitted

title = 'Timing comparison'

def render(**kwargs):
    app_name = kwargs['app_name']
    
    apps = Application.objects.filter(appName__exact=app_name)
    if not apps:
        return Http404     
    
    #we don't need any extra data in our render.html so we return an empty dictionary
    return {}

def analyse(**kwargs):
    requestData = kwargs['requestData']
    app_name = kwargs['app_name']
    
    myversions = requestData['versions'].split(',')
    
    if not len(myversions) == 2:
        return { 'template' : 'analysis/error.html', 'errorMessage' : 'Please provide only 2 versions.' }
    
    #get the names of the versions by their id(a single get by primary key, quite fast)
    verObj1 = Application.objects.get(pk=myversions[0])
    verObj2 = Application.objects.get(pk=myversions[1])
    
    verName1 = verObj1.appVersion
    verName2 = verObj2.appVersion 
    
    myquery = """    
  SELECT NVL(t.algname, 'None') algname,
      NVL(ROUND(t.oldavg                         - t.newavg,2),0) timediff,
      NVL(ROUND(DECODE(t.oldavg, 0, 0, (t.oldavg - t.newavg)/t.oldstd),2), 0) nbsigmas,
      NVL(ROUND(t.oldavg,2), 0) first_avg,
      NVL(ROUND(t.oldstd,2), 0) first_std,
      NVL(ROUND(t.oldct,2), 0) first_ct,
      NVL(ROUND(t.newavg,2), 0) second_avg,
      NVL(ROUND(t.newstd,2), 0) second_std,
      NVL(ROUND(t.newct,2), 0) second_ct
FROM
  (SELECT data1.algname,
    data1.algavg oldavg,
    data1.algstd oldstd,
    data1.ct oldct,
    data2.algavg newavg,
    data2.algstd newstd,
    data2.ct newct
  FROM
    (SELECT jatt1.name algname,
      AVG(res1.data) algavg,
      stddev(res1.data) algstd,
      COUNT(*) ct
    FROM lhcbpr_jobdescription jdesc1,
      lhcbpr_job j1,
      lhcbpr_jobresults jres1,
      lhcbpr_jobattribute jatt1,
      lhcbpr_resultfloat res1,
      lhcbpr_options opts
    WHERE jdesc1.application_id = {0}
    AND j1.jobdescription_id   = jdesc1.id
    AND j1.platform_id         = {1}
    AND j1.success             = 1
    AND jres1.job_id           = j1.id
    AND jres1.jobattribute_id  = jatt1.id
    AND jatt1."GROUP"          = 'Timing'
    AND res1.jobresults_ptr_id = jres1.id
    AND jdesc1.options_id = opts.id
    AND opts.id = {2}
    GROUP BY jatt1.name
    ) data1
  FULL OUTER JOIN
    (SELECT jatt1.name algname,
      AVG(res1.data) algavg,
      stddev(res1.data) algstd,
      COUNT(*) ct
    FROM lhcbpr_jobdescription jdesc1,
      lhcbpr_job j1,
      lhcbpr_jobresults jres1,
      lhcbpr_jobattribute jatt1,
      lhcbpr_resultfloat res1,
      lhcbpr_options opts
    WHERE jdesc1.application_id = {3}
    AND j1.jobdescription_id   = jdesc1.id
    AND j1.platform_id         = {4}
    AND j1.success             = 1
    AND jres1.job_id           = j1.id
    AND jres1.jobattribute_id  = jatt1.id
    AND jatt1."GROUP"          = 'Timing'
    AND res1.jobresults_ptr_id = jres1.id
    AND jdesc1.options_id = opts.id
    AND opts.id = {5}
    GROUP BY jatt1.name
    ) data2
  ON data1.algname = data2.algname
  ) t
ORDER BY t.oldavg - t.newavg
""".format(myversions[0], requestData['platforms'], requestData['options'],
           myversions[1], requestData['platforms'], requestData['options'])


    #return {'template' : 'analysis/error.html', 'errorMessage' : myquery}
    myqueryentries = """
    SELECT distinct jatt1.name algname,
      res1.data entries
    FROM lhcbpr_jobdescription jdesc1,
      lhcbpr_job j1,
      lhcbpr_jobresults jres1,
      lhcbpr_jobattribute jatt1,
      lhcbpr_resultint res1,
      lhcbpr_options opts
    WHERE ( jdesc1.application_id = {0} or jdesc1.application_id = {1} )
    AND j1.jobdescription_id   = jdesc1.id
    AND j1.platform_id         = {2}
    AND j1.success             = 1
    AND jres1.job_id           = j1.id
    AND jres1.jobattribute_id  = jatt1.id
    AND jatt1."GROUP"          = 'TimingCount'
    AND res1.jobresults_ptr_id = jres1.id
    AND jdesc1.options_id = opts.id
    AND opts.id = {3}
    """.format(myversions[0], myversions[1], requestData['platforms'], requestData['options'])
    #return { 'template' : 'analysis/error.html', 'errorMessage' : myqueryentries}
    #establish connection
    cursor = connection.cursor()
     
    algorithm_entries = {}
    cursor.execute(myqueryentries)
    
    #get one results from the cursor
    result = cursor.fetchone()
    
    while not result == None:
        # algname_count , entries
        algorithm_entries[str(result[0])] = int(result[1])
        result = cursor.fetchone()
                
    #then execute the next query_results to fetch the results
    cursor.execute(myquery)
    
    results_list = []

    result = cursor.fetchone()
    
    first_ct = int(result[5])
    second_ct = int(result[8])
    
    while not result == None:
        try:
            entries_temp = algorithm_entries[result[0]+'_count']
        except:
            entries_temp = 0
        
        #how they come from the database
        # algname, timediff, nbsigmas, first_avg, first_std, first_ct, second_avg, second_std, second_ct
        #how they will be printed
        #algname, timediff, nbsigmas, entries, first_avg, first_std, second_avg, second_std
        results_list.append([ str(result[0]), float(result[1]), float(result[2]), entries_temp ,float(result[3]), 
                             float(result[4]), float(result[6]), float(result[7])] )
        result = cursor.fetchone()

    if not results_list:
        return { 'template' : 'analysis/error.html' , 'errorMessage' : 'Your selections produced no results'}
    
    return { 'results' : json.dumps(results_list),
             'columns_names' :  json.dumps(['Algname', 'TimeDiff', 'nbsigmas', 'Entries', verName1+'_avg',
                                            verName1+'_std', verName2+'_avg', verName2+'_std' ]),
            'cts' : json.dumps([['Version', 'Total count'], [verName1, first_ct], [verName2, second_ct]])
             }
#for the moment we just keep it for the BRUNEL
def isAvailableFor(app_name):
    
    if app_name in [ 'BRUNEL', 'MOORE', 'GAUSS', 'DAVINCI' ]:
        return True
    
    return False