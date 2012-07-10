# Create your views here.
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt    
from django.template import RequestContext

from lhcbPR.models import JobDescription, Requested_platform, Platform, Application, Options, SetupProject
import json, subprocess, sys, configs, re, copy

#***********************************************
from django.contrib.auth.decorators import login_required
from django.contrib.auth import BACKEND_SESSION_KEY
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    pass
 
def makeList(mylist,key):
    List = []
    for dict in mylist:  
        List.append(dict[key])
    
    return List
def makeListChecked(mylist,key,are_checked = []):
    List = []
    for dict in mylist:
        if dict[key] in are_checked:
            List.append({'value' : dict[key], 'checked' : True})
        else:
            List.append({'value' : dict[key], 'checked' : False})
    return List
      
def index(request):
    myauth = request.user.is_authenticated()
    myDict = { 'myauth' : myauth, 'user' : request.user}
    return render_to_response('lhcbPR/index.html', myDict,
                  context_instance=RequestContext(request))

@login_required     
def addnew(request):
    myauth = request.user.is_authenticated()
    myDict = { 'myauth' : myauth, 'user' : request.user}
    
    return render_to_response('lhcbPR/addnew.html', myDict,
                  context_instance=RequestContext(request))

@login_required  #login_url="login"
def jobDescriptions(request, app_name):
    
    applications = Application.objects.values('appName').distinct('appName')
    applicationsList = makeList(applications, 'appName')
        
    myauth = request.user.is_authenticated()
    
    appVersions = JobDescription.objects.filter(application__appName__exact=app_name).values('application__appVersion').distinct('application__appVersion')
    
    if not appVersions:
        return HttpResponseNotFound("<h3>Page was not found</h3>")
    
    options = Options.objects.all().values('content').distinct('content')
    platforms = Requested_platform.objects.filter(jobdescription__application__appName__exact=app_name).values('cmtconfig__cmtconfig').distinct('cmtconfig__cmtconfig')
    setupProject = SetupProject.objects.all().values('content').distinct('content')
    
    if 'appVersions' in request.GET:
        appVersionsList = makeListChecked(appVersions,'application__appVersion',request.GET['appVersions'].split(','))
    else:
        appVersionsList = makeListChecked(appVersions,'application__appVersion')
    if 'platforms' in request.GET:
        cmtconfigsList = makeListChecked(platforms,'cmtconfig__cmtconfig',request.GET['platforms'].split(','))
    else:
        cmtconfigsList = makeListChecked(platforms,'cmtconfig__cmtconfig')
    if 'SetupProjects' in request.GET:
        setupProjectList = makeListChecked(setupProject,'content',request.GET['SetupProjects'].split(','))
    else:
        setupProjectList = makeListChecked(setupProject,'content')
    if 'Options' in request.GET:
        optionsList = makeListChecked(options,'content',request.GET['Options'].split(','))
    else:
        optionsList = makeListChecked(options,'content')
    if 'page' in request.GET:
        requested_page = request.GET['page']
    else:
        requested_page = 1
    
    dataDict = { 'appVersions' : appVersionsList,
               'options' : optionsList,
               'platforms' : cmtconfigsList,
               'setupProject' : setupProjectList,
               'active_tab' : app_name ,
               'myauth' : myauth, 
               'user' : request.user, 
               'applications' : applicationsList,
               'current_page' : requested_page
               }
      
    return render_to_response('lhcbPR/jobDescriptions.html', 
                  dataDict,
                  context_instance=RequestContext(request))
   
@login_required 
def jobDescriptionsHome(request):
    applications = Application.objects.values('appName').distinct('appName')
    
    applicationsList = []
    for dict in applications:  
        applicationsList.append(dict['appName'])
    myauth = request.user.is_authenticated()
    myDict = { 'active_tab' : 'home' ,'myauth' : myauth, 'user' : request.user, 'applications' : applicationsList }
      
    return render_to_response('lhcbPR/jobDescriptionsHome.html', 
                  myDict,
                  context_instance=RequestContext(request))

@login_required 
def newdata(request):
    applications = Application.objects.values('appName').distinct('appName')
    
    applicationsList = []
    for dict in applications:  
        applicationsList.append(dict['appName'])
    myauth = request.user.is_authenticated()
    myDict = { 'active_tab' : 'home' ,'myauth' : myauth, 'user' : request.user, 'applications' : applicationsList }
      
    return render_to_response('lhcbPR/newdata.html', 
                  myDict,
                  context_instance=RequestContext(request))

    
@login_required     
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

@login_required
def getFilters(request):
    results_per_page = 15
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
        
        jobDesTemp = JobDescription.objects.filter(final_query)
        Qplatform = None
        if request.GET['platforms']:
           Qplatform = makeQuery('cmtconfig__cmtconfig__exact', request.GET['platforms'].split(','), Q.OR)
        
        paginator = Paginator(jobDesTemp,results_per_page)
        requested_page = request.GET['page']
        
        try:
            jobDes = paginator.page(requested_page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            jobDes = paginator.page(1)
        except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
            jobDes = paginator.page(paginator.num_pages)
        
        myobjectlist = []
        for j in jobDes.object_list :#jobDesTemp 
            myDict={ 'pk' : j.id,   
                     'appName' : j.application.appName,
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
            
            #old missing part
            
            myobjectlist.append(myDict)
            
        pageIngo = {
                    'num_of_pages' : paginator.num_pages,
                    'current_page' : jobDes.number
                    }
        
        return HttpResponse(json.dumps({ 'jobs' :  myobjectlist, 'page_info' : pageIngo }))