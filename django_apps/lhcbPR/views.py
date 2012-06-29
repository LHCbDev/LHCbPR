# Create your views here.
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt    
from django.template import RequestContext

from lhcbPR.models import JobDescription, Requested_platform, Platform, Application, Options
import json, subprocess, sys, configs

#***********************************************
from django.contrib.auth.decorators import login_required
from django.contrib.auth import BACKEND_SESSION_KEY

def test(request):
   
    kwargs = {
    '{0}__{1}__{2}'.format('application', 'appName', 'exact'): 'GAUSS',
    }

    
    versions = { 
                '{0}__{1}__{2}'.format('application', 'appVersion', 'exact'): 'v38r7',
                '{0}__{1}__{2}'.format('application', 'appVersion', 'exact'): 'v39r2'
                }

    q =  Q()
    for k,v in versions.iteritems():
        q.add(Q( **{k : v }),Q.OR)
    
    
    
    #q.add(q2, Q.AND)
      
    jobDes = JobDescription.objects.filter(q)
    
    myobjectlist = []
    for j in jobDes:
        myDict={ 'appName' : j.application.appName,
                 'appVersion' : j.application.appVersion,
                 'options' : j.options.content,
                 'optionsD' : j.options.description,
                 } 
        platforms = Requested_platform.objects.filter(jobdescription__exact=j)
        if platforms:
            for p in platforms:
                myDict['cmtconfig'] = p.cmtconfig.cmtconfig
                myobjectlist.append(myDict)
        else:
            myDict['cmtconfig'] = ""
            myobjectlist.append(myDict)
        
    
    return render_to_response('lhcbPR/jobs.html', 
                            { 'jobs' :  myobjectlist },
                  context_instance=RequestContext(request))
 
def makeList(mylist,key):
    List = []
    for dict in mylist:  
        List.append(dict[key])
    
    return List
       
def index(request):
    myauth = request.user.is_authenticated()
    myDict = { 'myauth' : myauth, 'user' : request.user}
    return render_to_response('lhcbPR/index.html', myDict,
                  context_instance=RequestContext(request))

@login_required(login_url="login")      
def addnew(request):
    myauth = request.user.is_authenticated()
    myDict = { 'myauth' : myauth, 'user' : request.user}
    
    return render_to_response('lhcbPR/addnew.html', myDict,
                  context_instance=RequestContext(request))
    
@login_required(login_url="login")  
def newdata(request):
    applications = Application.objects.values('appName').distinct('appName')
    
    applicationsList = []
    for dict in applications:  
        applicationsList.append(dict['appName'])
    myauth = request.user.is_authenticated()
    myDict = { 'myauth' : myauth, 'user' : request.user, 'applications' : applicationsList }
      
    return render_to_response('lhcbPR/newdata.html', 
                  myDict,
                  context_instance=RequestContext(request))

def handleRequest(request):
    if request.method == 'GET':
        if request.GET['function'] == 'Version':
            appVersions = Application.objects.filter(appName__exact=request.GET['key']).values('appVersion').distinct('appVersion')
            
            appVersionsList = makeList(appVersions,'appVersion')    
            myDict = { 'appVersions' : appVersionsList }
            
            return HttpResponse(json.dumps(myDict))
        
        if request.GET['function'] == 'Options':
            pass