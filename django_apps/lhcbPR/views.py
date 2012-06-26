# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt    
from django.template import RequestContext
from generic.models import App, AppDes, Attr, Blob, AppAtr
from lhcbPR.models import Application
import json, subprocess, sys, configs

#***********************************************
from django.contrib.auth.decorators import login_required
from django.contrib.auth import BACKEND_SESSION_KEY
def test(request):
    
    return HttpResponse(request.session.get(BACKEND_SESSION_KEY))
 
def makeList(mylist,key):
    List = []
    for dict in mylist:  
        List.append(dict[key])
    
    return List
       
def index(request):
    return render_to_response('lhcbPR/index.html', 
                  context_instance=RequestContext(request))
@login_required(login_url="login")  
def newdata(request):
    applications = Application.objects.values('appName').distinct('appName')
    
    applicationsList = []
    for dict in applications:  
        applicationsList.append(dict['appName'])
        
    return render_to_response('lhcbPR/newdata.html', 
                  { 'applications' : applicationsList },
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
        
def handleService(request):
    if request.method == 'GET':
        if request.GET['service'] == 'version':
            querykey = request.GET['key']
            appVersions = App.objects.filter(appName__exact=querykey).values('appVersion').distinct('appVersion')
            
            appVersionsList = []
            for dict in appVersions:  
                appVersionsList.append(dict['appVersion'])
            
            myDict = {}
            myDict['appVersions'] = appVersionsList

            return HttpResponse(json.dumps(myDict))
        
        if request.GET['service'] == 'options':
            appl = request.GET['appl'] 
            version = request.GET['version']
            application = App.objects.get(appName__exact=appl,appVersion__exact=version)
            
            options = AppDes.objects.filter(app__exact=application).values('options').distinct('options')
            
            optionsList = []
            for dict in options:  
                optionsList.append(dict['options'])
            
            myDict = {}
            myDict['optionsList'] = optionsList
            print myDict
            return HttpResponse(json.dumps(myDict))
