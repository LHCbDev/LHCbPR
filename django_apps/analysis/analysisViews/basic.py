from django.db.models import Q
from django.http import HttpResponseNotFound
from django.shortcuts import render_to_response   
from django.template import RequestContext

from lhcbPR.models import Job, JobResults, Application
from tools.viewTools import makeCheckedList, getSplitted 

def render(request, app_name):
    """From the url is takes the requested application(app_name) , example:
    /django/lhcbPR/jobDescriptions/BRUNEL ==> app_name = 'BRUNEL' 
    and depending on the app_name it returns the available versions, options, setupprojects"""
    
    applicationsList = list(Job.objects.filter(success=True).values_list('jobDescription__application__appName',flat=True).distinct())
    myauth = request.user.is_authenticated()
    
    apps = Application.objects.filter(appName__exact=app_name)
    if not apps:
        return HttpResponseNotFound("<h3>Page not found, no such application</h3>")     
    
    #atrs = map(str, JobResults.objects.filter(job__jobDescription__application__appName__exact=app_name).values_list('jobAttribute__name', flat=True).distinct())
    atrs =  JobResults.objects.filter(job__jobDescription__application__appName=app_name,job__success=True).filter(Q(jobAttribute__type='Int') | Q(jobAttribute__type='Float')).values_list('jobAttribute__name','jobAttribute__type').distinct()
    
    options = map(str, Job.objects.filter(jobDescription__application__appName=app_name,success=True).values_list('jobDescription__options__description', flat=True).distinct())
        
    versions_temp = map(str, Job.objects.filter(jobDescription__application__appName=app_name,success=True).values_list('jobDescription__application__appVersion', flat=True).distinct())
    versions = reversed(sorted(versions_temp, key = getSplitted))

    platforms = map(str, Job.objects.filter(jobDescription__application__appName=app_name,success=True).values_list('platform__cmtconfig', flat=True).distinct())
    platforms.sort()
     
    hosts = map(str, Job.objects.filter(jobDescription__application__appName=app_name,success=True).values_list('host__hostname', flat=True).distinct())
    hosts.sort()
    
    if 'options' in request.GET:
        optionsList = makeCheckedList(options, request.GET['options'].split(','))
    else:
        optionsList = makeCheckedList(options)
    if 'versions' in request.GET:
        versionsList = makeCheckedList(versions, request.GET['versions'].split(','))
    else:
        versionsList = makeCheckedList(versions)
    if 'platforms' in request.GET:
        platformsList = makeCheckedList(platforms, request.GET['platforms'].split(','))
    else:
        platformsList = makeCheckedList(platforms)
    if 'hosts' in request.GET:
        hostsList = makeCheckedList(hosts, request.GET['hosts'].split(','))
    else:
        hostsList = makeCheckedList(hosts)  
    
    dataDict = { 'attributes' : atrs,
                'platforms' : platformsList,
                'hosts' : hostsList,
                'options' : optionsList,
                'versions' : versionsList,
                'active_tab' : app_name ,
                'myauth' : myauth, 
                'user' : request.user, 
                'applications' : applicationsList,
               }
      
    return render_to_response('lhcbPR/analyse/analyseBasic.html', 
                  dataDict,
                  context_instance=RequestContext(request))