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
    #groups = request.META.get('ADFS_GROUP').split(';') 
    return HttpResponse(request.user.is_authenticated())
 
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