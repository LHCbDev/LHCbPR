# Create your views here.
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt    
from django.template import RequestContext

from lhcbPR.models import JobDescription, Requested_platform, Platform, Application, Options, SetupProject
import json, subprocess, sys, configs, re, copy

#***********************************************
from django.contrib.auth.decorators import login_required
from django.contrib.auth import BACKEND_SESSION_KEY

def combineStatements(StatementsDict, operator):
    """Takes a dictionary with statements, combines them depending on the
    given operator(AND,OR) and return a final query(query)"""
    query =  Q()
    for k,v in StatementsDict.iteritems():
        query.add(Q( **{ v : k }),operator)
    
    return query
     
def makeQuery(statement,arguments,operator):
    dataDict = {}
    
    for arg in arguments:
        dataDict[arg] = statement
        
    return combineStatements(dataDict, operator)
    
def test(request):
    if request.method == 'GET':
        
        #return HttpResponse(request.GET['appVersions'])
        querylist = []
        
        if request.GET['app']:
            querylist.append(makeQuery('application__appName__exact', request.GET['app'].split(','), Q.OR))
        if request.GET['appVersions']:
            querylist.append(makeQuery('application__appVersion__exact', request.GET['appVersions'].split(','), Q.OR))
        if request.GET['Options']:
            querylist.append(makeQuery('options__content__exact',request.GET['Options'].split(','), Q.OR))
        if request.GET['SetupProjects']:
            querylist.append(makeQuery('setup_project__content__exact',request.GET['SetupProjects'].split(','), Q.OR))
        
        final_query = Q()
        for q in querylist:
           final_query &= q 
        
        jobDes = JobDescription.objects.filter(final_query)
        Qplatform = None
        if request.GET['cmtconfigs']:
           Qplatform = makeQuery('cmtconfig__cmtconfig__exact', request.GET['cmtconfigs'].split(','), Q.OR)
        
        myobjectlist = []
        for j in jobDes:
            myDict={ 'appName' : j.application.appName,
                     'appVersion' : j.application.appVersion,
                     'options' : j.options.content,
                     'optionsD' : j.options.description,
                     } 
            try:
                myDict['setupproject'] = j.setup_project.content
            except Exception:
                myDict['setupproject'] = ""
            
            platforms = None
            if Qplatform:
                platforms = Requested_platform.objects.filter(jobdescription__exact=j).filter(Qplatform)
            else: 
                platforms = Requested_platform.objects.filter(jobdescription__exact=j) 

            if platforms:
                for p in platforms:
                    DictTemp = {}
                    DictTemp.update(myDict)
                    DictTemp['cmtconfig'] = p.cmtconfig.cmtconfig
                    myobjectlist.append(DictTemp)
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

#@login_required(login_url="login")      
def addnew(request):
    myauth = request.user.is_authenticated()
    myDict = { 'myauth' : myauth, 'user' : request.user}
    
    return render_to_response('lhcbPR/addnew.html', myDict,
                  context_instance=RequestContext(request))
    
#@login_required(login_url="login")  
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
        if request.GET['function'] == 'i_love_cookies':
            appVersions = JobDescription.objects.filter(application__appName__exact=request.GET['key']).values('application__appVersion').distinct('application__appVersion')
            options = Options.objects.all().values('content').distinct('content')
            cmtconfigs = Requested_platform.objects.filter(jobdescription__application__appName__exact=request.GET['key']).values('cmtconfig__cmtconfig').distinct('cmtconfig__cmtconfig')
            setupProject = SetupProject.objects.all().values('content').distinct('content')
            
            appVersionsList = makeList(appVersions,'application__appVersion') 
            optionsList = makeList(options,'content')   
            cmtconfigsList = makeList(cmtconfigs,'cmtconfig__cmtconfig')
            setupProjectList = makeList(setupProject,'content')
            
            myDict = { 'appVersions' : appVersionsList,
                       'options' : optionsList,
                       'cmtconfigs' : cmtconfigsList,
                       'setupProject' : setupProjectList,
                       }
            
            return HttpResponse(json.dumps(myDict))
        
        if request.GET['function'] == 'Options':
            pass
def getFilters(request):
        if request.method == 'GET':
        
            querylist = []
            
            if request.GET['app']:
                querylist.append(makeQuery('application__appName__exact', request.GET['app'].split(','), Q.OR))
            if request.GET['appVersions']:
                querylist.append(makeQuery('application__appVersion__exact', request.GET['appVersions'].split(','), Q.OR))
            if request.GET['Options']:
                querylist.append(makeQuery('options__content__exact',request.GET['Options'].split(','), Q.OR))
            if request.GET['SetupProjects']:
                querylist.append(makeQuery('setup_project__content__exact',request.GET['SetupProjects'].split(','), Q.OR))
            
            final_query = Q()
            for q in querylist:
               final_query &= q 
            
            jobDes = JobDescription.objects.filter(final_query)
            Qplatform = None
            if request.GET['cmtconfigs']:
               Qplatform = makeQuery('cmtconfig__cmtconfig__exact', request.GET['cmtconfigs'].split(','), Q.OR)
            
            myobjectlist = []
            for j in jobDes:
                myDict={ 'appName' : j.application.appName,
                         'appVersion' : j.application.appVersion,
                         'options' : j.options.content,
                         'optionsD' : j.options.description,
                         } 
                try:
                    myDict['setupproject'] = j.setup_project.content
                except Exception:
                    myDict['setupproject'] = ""
                
                fixed_description = myDict['appName']+"   "+myDict['appVersion']+"  "+myDict["setupproject"]
                fixed_description += "  "+myDict['options']
                
                platforms = None
                if Qplatform:
                    platforms = Requested_platform.objects.filter(jobdescription__exact=j).filter(Qplatform)
                else: 
                    platforms = Requested_platform.objects.filter(jobdescription__exact=j) 
    
                if platforms:
                    for p in platforms:
                        DictTemp = {}
                        DictTemp.update(myDict)
                        DictTemp['cmtconfig'] = p.cmtconfig.cmtconfig
                        fixed_temp = c = copy.copy(fixed_description)
                        fixed_temp += "  "+DictTemp['cmtconfig']
                        myobjectlist.append(fixed_temp)
                        #myobjectlist.append(DictTemp)
                else:
                    myDict['cmtconfig'] = ""
                    myobjectlist.append(fixed_description)
                    #myobjectlist.append(myDict)
                
                
            return HttpResponse(json.dumps({ 'jobs' :  myobjectlist }))