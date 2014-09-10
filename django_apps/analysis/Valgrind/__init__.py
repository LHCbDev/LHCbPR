"""

Memcheck report

"""

title = 'Memcheck Report'

import json
from django.db import connection
from django.http import Http404
from lhcbPR.models import  Application, JobDescription, Job
from lhcbPR.models import Options, JobResults, JobAttribute, ResultFloat, ResultFile
from django.db.models import Q
from tools.viewTools import getSplitted

#
# Projects for which to display this analysis
#
################################################################################
def isAvailableFor(app_name):
    ''' Available for all applications, this is teh Valgrind memory check '''
    return True


#
# render method 
#
################################################################################
def render(**kwargs):
    """From the url is takes the requested application(app_name) , example:
    /django/lhcbPR/jobDescriptions/BRUNEL ==> app_name = 'BRUNEL' 
    and depending on the app_name it returns the available versions, options, setupprojects"""
    app_name = kwargs['app_name']

    apps = Application.objects.filter(appName__exact=app_name)
    if not apps:
        return Http404     

    mygroup = 'Valgrind'
    options = Options.objects.filter(jobdescriptions__application__appName=app_name,
                                     jobdescriptions__jobs__jobresults__jobAttribute__group=mygroup,
                                     jobdescriptions__jobs__success=True,).distinct().order_by('description')
    versions_temp = Application.objects.filter(jobdescriptions__jobs__success=True, appName=app_name,
                                               jobdescriptions__jobs__jobresults__jobAttribute__group=mygroup).distinct()
    versions = sorted(versions_temp, key = lambda ver : getSplitted(ver.appVersion), reverse = True)
    return {'options':options, 'versions':versions}


def analyse(**kwargs):
    """ Analyze the brunel versions 
    """

    #print kwargs

    requestData = kwargs['requestData']
    app_name = kwargs['app_name']
    
    # Result dictionary
    res = dict()
    appInfo = []
    
    # Now looking up the Brunel Version objects
    versions = requestData['versions'].split(",")
    options = requestData['options'].split(",")
    appversions = [Application.objects.get(pk=k) for k in versions]

    # JobDescription objects
    for optionId in options:
        for av in appversions:
            info = getMemcheckInfo(av, optionId)
            appInfo.append(info)

    res['results'] = appInfo
    return res


def getMemcheckInfo(app, optionId):
    '''
    Returns the information from the Brunel jobs for an application
    '''
    appInfo = {}
    
    # Looking up options info
    opt = Options.objects.get(pk=optionId)
    
    # Now getting the Job Description
    jd = JobDescription.objects.get(options=optionId, application=app)
    jobs = Job.objects.filter(jobDescription=jd)
    alljobs = []
    for j in jobs:
        jinfo = {}
        jinfo['id'] = j.id
        jinfo['time_start'] = j.time_start 
        jinfo['time_end'] = j.time_end
        jres = []

        for jr in JobResults.objects.filter(job=j,jobAttribute__group="Valgrind"):
            jrestmp = {}
            jrestmp['name'] = jr.jobAttribute.name
            jrestmp['type'] = jr.jobAttribute.type
            jrestmp['group'] = jr.jobAttribute.group

            if  jr.jobAttribute.type == "Float":
                rf = ResultFloat.objects.get(pk=jr.id)
                jrestmp['value'] = rf.data
            if  jr.jobAttribute.type == "File":
                rf = ResultFile.objects.get(pk=jr.id)
                jrestmp['value'] =  rf.file
            jres.append(jrestmp)

        jinfo['jobresults'] = jres
        alljobs.append(jinfo)
      
    appInfo['jobs'] = alljobs
    appInfo['version'] = app.appVersion
    appInfo['application'] = app.appName
    appInfo['options'] = opt.description
    return appInfo
