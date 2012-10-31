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
    
    if not app_name == 'BRUNEL':
        return HttpResponse("<h3>Sorry this type of analysis is not supported for {0}  application</h3>".format(app_name))
    
    applicationsList = list(Job.objects.filter(success=True).values_list('jobDescription__application__appName',flat=True).distinct())
    myauth = request.user.is_authenticated()     
    
    options = map(str, JobResults.objects.filter(job__jobDescription__application__appName=app_name,
                jobAttribute__group='TimingTree',
                job__success=True).values_list('job__jobDescription__options__description', flat=True).distinct())
    
    if not options:
        return HttpResponse("<h3>No proper timing results to generate tree timing analysis</h3>")
        
    versions_temp = map(str, JobResults.objects.filter(job__jobDescription__application__appName=app_name,
                jobAttribute__group='TimingTree',
                job__success=True).values_list('job__jobDescription__application__appVersion', flat=True).distinct())
    versions = reversed(sorted(versions_temp, key = getSplitted))

    platforms = map(str, JobResults.objects.filter(job__jobDescription__application__appName=app_name,
                    jobAttribute__group='TimingTree',
                    job__success=True).values_list('job__platform__cmtconfig', flat=True).distinct())
    platforms.sort()
     
    hosts = map(str, JobResults.objects.filter(job__jobDescription__application__appName=app_name,
                jobAttribute__group='TimingTree',
                job__success=True).values_list('job__host__hostname', flat=True).distinct())
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
    
    dataDict = {
                'platforms' : platformsList,
                'hosts' : hostsList,
                'options' : optionsList,
                'versions' : versionsList,
                'active_tab' : app_name ,
                'myauth' : myauth, 
                'user' : request.user, 
                'applications' : applicationsList,
               }
      
    return render_to_response('lhcbPR/analyse/analyseTiming.html', 
                  dataDict,
                  context_instance=RequestContext(request))