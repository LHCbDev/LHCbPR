# Create your views here.
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt    
from django.template import RequestContext


from lhcbPR.models import JobDescription, Requested_platform, Platform, Application, Options, SetupProject, Handler, JobHandler, Job
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

@login_required  #login_url="login"
def jobDescriptions(request, app_name):
    
    applications = Application.objects.values('appName').distinct('appName')
    applicationsList = makeList(applications, 'appName')
        
    myauth = request.user.is_authenticated()
    
    appVersions = JobDescription.objects.filter(application__appName__exact=app_name).values('application__appVersion').distinct('application__appVersion')
    
    if not appVersions:
        return HttpResponseNotFound("<h3>Page was not found</h3>")
    
    options = Options.objects.all().values('description').distinct('description')
    platforms = Platform.objects.all().values('cmtconfig').distinct('cmtconfig')
    setupProject = SetupProject.objects.all().values('description').distinct('description')
    
    if 'appVersions' in request.GET:
        appVersionsList = makeListChecked(appVersions,'application__appVersion',request.GET['appVersions'].split(','))
    else:
        appVersionsList = makeListChecked(appVersions,'application__appVersion')
    if 'platforms' in request.GET:
        cmtconfigsList = makeListChecked(platforms,'cmtconfig',request.GET['platforms'].split(','))
    else:
        cmtconfigsList = makeListChecked(platforms,'cmtconfig')
    if 'SetupProjects' in request.GET:
        setupProjectList = makeListChecked(setupProject,'description',request.GET['SetupProjects'].split(','))
    else:
        setupProjectList = makeListChecked(setupProject,'description')
    if 'Options' in request.GET:
        optionsList = makeListChecked(options,'description',request.GET['Options'].split(','))
    else:
        optionsList = makeListChecked(options,'description')
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
def analyseHome(request):
    myauth = request.user.is_authenticated()
    myDict = { 'myauth' : myauth, 'user' : request.user }
      
    return render_to_response('lhcbPR/analyseHome.html', 
                  myDict,
                  context_instance=RequestContext(request))
    
@login_required     
def handleRequest(request):
    if request.method == 'GET':
        if request.GET['function'] == 'i_love_cookies':
            appVersionsList = makeList(JobDescription.objects.filter(application__appName__exact=request.GET['key']).values('application__appVersion').distinct('application__appVersion'),'application__appVersion') 
            optionsList = makeList(Options.objects.all().values('content').distinct('content'),'content')   
            cmtconfigsList = makeList(Requested_platform.objects.filter(jobdescription__application__appName__exact=request.GET['key']).values('cmtconfig__cmtconfig').distinct('cmtconfig__cmtconfig'),'cmtconfig__cmtconfig')
            setupProjectList = makeList(SetupProject.objects.all().values('content').distinct('content'),'content')
            
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
            querylist.append(makeQuery('options__description__exact',request.GET['Options'].split(','), Q.OR))
        if request.GET['SetupProjects']:
            querylist.append(makeQuery('setup_project__description__exact',request.GET['SetupProjects'].split(','), Q.OR))
        
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
                myDict['setupproject'] = j.setup_project.description
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

@login_required
def getJobDetails(request):
    if not 'job_id' in request.GET:
        return HttpResponseNotFound()
    
    myJob = JobDescription.objects.get(pk=request.GET['job_id'])

    platforms = makeList(Requested_platform.objects.filter(jobdescription__exact=myJob).values('cmtconfig__cmtconfig').distinct('cmtconfig_cmtconfig'),'cmtconfig__cmtconfig')
    
    all_platforms = makeList(Platform.objects.values('cmtconfig').distinct('cmtconfig'),'cmtconfig')
    all_platformsList = []
    for all_p in all_platforms:
        if all_p in platforms:
            all_platformsList.append({ 'platform' : all_p, 'checked' : True })
        else:
            all_platformsList.append({ 'platform' : all_p, 'checked' : False })
            
    handlers = makeList(JobHandler.objects.filter(jobDescription__exact=myJob).values('handler__name').distinct('handler__name'),'handler__name')
    
    all_handlers = makeList(Handler.objects.values('name').distinct('name'),'name')
    all_handlersList = []
    for all_h in all_handlers:
        if all_h in handlers:
            all_handlersList.append({ 'handler' : all_h, 'checked' : True })
        else:
            all_handlersList.append({ 'handler' : all_h, 'checked' : False })
    
    dataDict = {
                'pk' : myJob.id,   
                'appName' : myJob.application.appName,
                'appVersion' : myJob.application.appVersion,
                'options' : myJob.options.content,
                'optionsD' : myJob.options.description,
                'platforms' : all_platformsList,
                'handlers' : all_handlersList
                }
    try:
        dataDict['setupProject'] = myJob.setup_project.content
        dataDict['setupProjectD'] = myJob.setup_project.description
    except:
        dataDict['setupProject'] = ''
        dataDict['setupProjectD'] = ''
    
    if 'cloneRequest' or 'editRequest' in request.GET:
        dataDict['versionsAll'] = makeList(Application.objects.filter(appName__exact=myJob.application.appName).values('appVersion').distinct('appVersion'),'appVersion')
        dataDict['optionsAll'] = makeList(Options.objects.all().values('content').distinct('content'),'content')
        dataDict['optionsDAll'] = makeList(Options.objects.all().values('description').distinct('description'),'description')
        dataDict['setupAll'] = makeList(SetupProject.objects.all().values('content').distinct('content'),'content')
        dataDict['setupDAll'] = makeList(SetupProject.objects.all().values('description').distinct('description'),'description')
    
    #check if the jobdescription exists in runned jobs so the user can edit or not some attributes
    if 'editRequest':
        try:
            Job.objects.get(jobDescription__pk__exact=request.GET['job_id'])
        except Exception:
            dataDict['exists'] = False
        else:
            dataDict['exists'] = True
                
    return HttpResponse(json.dumps(dataDict))

@login_required
def editRequests(request):
    if not 'value' or not 'key' or not 'real_name' in request.GET:
        return HttpResponse()
    if request.GET['real_name'] == 'Options':
        myObj = Options.objects.filter( **{'{0}__exact'.format(request.GET['key']) : request.GET['value']} )
    else: #request.GET['real_name'] == 'SetupProject':
        myObj = SetupProject.objects.filter( **{'{0}__exact'.format(request.GET['key']) : request.GET['value']} )
    
    if myObj.count() == 1:
        if request.GET['key'] == 'description':
            return HttpResponse(json.dumps({ 'data' : myObj[0].content }))
        elif request.GET['key'] == 'content':
            return HttpResponse(json.dumps({ 'data' : myObj[0].description }))
        else:
            return HttpResponse(json.dumps({ 'data' : '' }))
    else:
        return HttpResponse(json.dumps({ 'data' : '' }))
    
@login_required
def commitClone(request):
    if 'update' in request.GET:
        return HttpResponse(json.dumps({ 'updated' : True }))
    
    app = Application(appName=request.GET['application'],appVersion=request.GET['version'])
    setup = SetupProject(content=request.GET['setupproject'],description=request.GET['setupprojectD'])
    opts = Options(content=request.GET['options'],description=request.GET['optionsD'])
    
    myjob_id = JobDescription.objects.filter(application__appName__exact=request.GET['application'], 
                                             application__appVersion__exact=request.GET['version'],
                                             options__content__exact=request.GET['options'],
                                             options__description__exact=request.GET['optionsD'],
                                             setup_project__content__exact=request.GET['setupproject'],
                                             setup_project__description__exact=request.GET['setupprojectD']
                                             )
    if myjob_id.count() > 0:
        return HttpResponse(json.dumps({ 'exists': True }))
    else:
        return HttpResponse(json.dumps({ 'exists' : False }))