"""
In this histogram analysis the "attribute" represents a title of a histogram inside the collected Gauss root files. The user can choose a histogram(attribute) and by clicking on the "retrieve results"
he will get the sum of  histograms for each logical group(options-version...) the user defined.

If the user leaves the selection checkboxes(options,version..) blank the page will generate the sum of histograms for all the available logical groups , may take long time)

A logical group is defined by a combination of options - version - platform(optional) - host(optional) , so the user can define for which versions, options etc he wants to see the sum(summary) of the histograms.

The page is still under construction, this is a demo(not the finished version)
"""

title = 'Gauss Target analysis'

import json, logging
from django.db import connection
# from django.http import HttpResponse 
from lhcbPR.models import Job,JobResults,ResultFile
from django.conf import settings
# from django.db.models import Q
# from query_builder import get_queries
# from tools.viewTools import getSplitted , subService as remoteService
from query_builder import get_queries


logger = logging.getLogger('analysis_logger') 

def render(**kwargs):
    app_name = kwargs['app_name']
    
    # if not JobResults.objects.filter(job__jobDescription__application__appName=app_name,jobAttribute__type='File').count() > 0:
    #     return HttpResponse('<h3>Not root files were saved</h3>')  
    
    # #atrs = map(str, JobResults.objects.filter(job__jobDescription__application__appName__exact=app_name).values_list('jobAttribute__name', flat=True).distinct())
    # atrs =  [ (k, v) for k, v in settings.HISTOGRAMSGAUSS.iteritems() ]
    
    # dataDict = { 'attributes' : atrs }
    dataDict = {"args": kwargs}      
    return dataDict

def analyse(**kwargs):
    requestData = kwargs['requestData']
    app_name = kwargs['app_name']
    query_groups, query_results = get_queries(requestData, app_name)
    
    #establish connection
    cursor = connection.cursor()
    
    #execute query_groups get the logical groups of the data
    cursor.execute(query_groups)
    db_result = cursor.fetchall()

    results = []
    for r in db_result:
        job_id = r[0]
        app_version = r[1]

        result = {"app_version": app_version}
        job = Job.objects.get(pk=job_id)
        dbfiles = ResultFile.objects.filter(job=job)
        files = []
        for file in dbfiles:
            files.append(file.file)
        result["files"] = files
        results.append(result)

    return {"results": results} 
    
def isAvailableFor(app_name):
    if app_name in ['GAUSS']:
        return True
    
    return False