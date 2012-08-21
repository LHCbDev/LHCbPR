# Create your views here.
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt    
from django.template import RequestContext
from django.core import serializers

from lhcbPR.models import JobDescription, Requested_platform, Platform, Application, Options, SetupProject, Handler, JobHandler, Job
import json, subprocess, sys, configs, re, copy, os

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
    myauth = request.user.is_authenticated()
    myDict = { 'myauth' : myauth, 'user' : request.user}
    return render_to_response('lhcbPR/index.html', myDict,
                  context_instance=RequestContext(request))

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
    return render_to_response('lhcbPR/indexOf.html', myDict,
                  context_instance=RequestContext(request))

@login_required  #login_url="login"
def jobDescriptions(request, app_name):
    
    applicationsList = map(str,Application.objects.values_list('appName', flat=True).distinct())
        
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
            appVersionsList = map(str,JobDescription.objects.filter(application__appName__exact=request.GET['key']).values_list('application__appVersion', flat=True).distinct()) 
            optionsList = map(str,Options.objects.all().values_list('content', flat=True).distinct())
            cmtconfigsList = map(str,Requested_platform.objects.filter(jobdescription__application__appName__exact=request.GET['key']).values_list('cmtconfig__cmtconfig', flat=True).distinct())
            setupProjectList = map(str,SetupProject.objects.all().values_list('content', flat=True).distinct())
            
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
                    'current_page' : jobDes.number,
                    'total_results' : jobDesTemp.count()
                    }
        
        return HttpResponse(json.dumps({ 'jobs' :  myobjectlist, 'page_info' : pageIngo }))

@login_required
def getJobDetails(request):
    if not 'job_id' in request.GET:
        return HttpResponseNotFound()
    
    myJob = JobDescription.objects.get(pk=request.GET['job_id'])

    platforms = map(str,Requested_platform.objects.filter(jobdescription__exact=myJob).values_list('cmtconfig__cmtconfig', flat=True).distinct())
    platforms.sort() 
            
    handlers = map(str,JobHandler.objects.filter(jobDescription__exact=myJob).values_list('handler__name', flat=True).distinct())
    handlers.sort()
    
    dataDict = {
                'pk' : myJob.id,   
                'appName' : myJob.application.appName,
                'appVersion' : myJob.application.appVersion,
                'options' : myJob.options.content,
                'optionsD' : myJob.options.description,
                'platforms' : platforms,
                'handlers' : handlers
                }
    try:
        dataDict['setupProject'] = myJob.setup_project.content
        dataDict['setupProjectD'] = myJob.setup_project.description
    except:
        dataDict['setupProject'] = ''
        dataDict['setupProjectD'] = ''
    
    if 'cloneRequest' or 'editRequest' in request.GET:
        dataDict['versionsAll'] = map(str,Application.objects.filter(appName__exact=myJob.application.appName).values_list('appVersion', flat=True).distinct())
        dataDict['optionsAll'] = map(str,Options.objects.all().values_list('content', flat=True).distinct())
        dataDict['optionsDAll'] = map(str,Options.objects.all().values_list('description', flat=True).distinct())
        dataDict['setupAll'] = map(str,SetupProject.objects.all().values_list('content', flat=True).distinct())
        dataDict['setupDAll'] = map(str,SetupProject.objects.all().values_list('description', flat=True).distinct())
    
    #check if the jobdescription exists in runned jobs so the user can edit or not some attributes
    if 'editRequest' in request.GET:
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
        myObj = JobDescription.objects.get(pk=request.GET['id'])
        myObj.setup_project = None
        if request.GET['setupproject'] != '' and request.GET['setupprojectD'] != '':
            setupprojectTemp, created = SetupProject.objects.get_or_create(content=request.GET['setupproject'], description=request.GET['setupprojectD'])
            myObj.setup_project=setupprojectTemp
        
        
        optionsTemp, created = Options.objects.get_or_create(content=request.GET['options'], description=request.GET['optionsD'])
        appTemp, created = Application.objects.get_or_create(appName=request.GET['application'], appVersion=request.GET['version'])
        
        
        myObj.options = optionsTemp
        myObj.application = appTemp
        
        myObj.save()
                  
        JobHandler.objects.filter(jobDescription__pk=request.GET['id']).delete()
        for handler_name in request.GET['handlers'].split(','):
            handlerTemp = Handler.objects.get(name=handler_name)
            jobHandlerTemp, created = JobHandler.objects.get_or_create(jobDescription=myObj, handler=handlerTemp)
        
        Requested_platform.objects.filter(jobdescription__pk=request.GET['id']).delete()
        for platform_name in request.GET['platforms'].split(','):
            platformTemp = Platform.objects.get(cmtconfig=platform_name)
            requestedPlatfromTemp, created = Requested_platform.objects.get_or_create(jobdescription=myObj, cmtconfig=platformTemp)
        
        return HttpResponse(json.dumps({ 'updated' : True, 'job_id' : myObj.id }))
    
    
    if request.GET['setupproject'] != '' and request.GET['setupprojectD'] != '':
        myjob_id = JobDescription.objects.filter(application__appName__exact=request.GET['application'], 
                                                 application__appVersion__exact=request.GET['version'],
                                                 options__content__exact=request.GET['options'],
                                                 options__description__exact=request.GET['optionsD'],
                                                 setup_project__content__exact=request.GET['setupproject'],
                                                 setup_project__description__exact=request.GET['setupprojectD']
                                                 )
    else:
        myjob_id = JobDescription.objects.filter(application__appName__exact=request.GET['application'], 
                                                 application__appVersion__exact=request.GET['version'],
                                                 options__content__exact=request.GET['options'],
                                                 options__description__exact=request.GET['optionsD'],
                                                 )
    if myjob_id.count() > 0:
        return HttpResponse(json.dumps({ 'exists': True }))
    else:
        if request.GET['setupproject'] != '' and request.GET['setupprojectD'] != '':
            setupprojectTemp, created = SetupProject.objects.get_or_create(content=request.GET['setupproject'], description=request.GET['setupprojectD'])
        
        optionsTemp, created = Options.objects.get_or_create(content=request.GET['options'], description=request.GET['optionsD'])
        appTemp, created = Application.objects.get_or_create(appName=request.GET['application'], appVersion=request.GET['version'])
        
        if request.GET['setupproject'] != '' and request.GET['setupprojectD'] != '':
            myObj, created = JobDescription.objects.get_or_create(application=appTemp, options=optionsTemp, setup_project=setupprojectTemp)
        else:
            myObj, created = JobDescription.objects.get_or_create(application=appTemp, options=optionsTemp)           
        
        for handler_name in request.GET['handlers'].split(','):
            handlerTemp = Handler.objects.get(name=handler_name)
            jobHandlerTemp, created = JobHandler.objects.get_or_create(jobDescription=myObj, handler=handlerTemp)
        
        for platform_name in request.GET['platforms'].split(','):
            platformTemp = Platform.objects.get(cmtconfig=platform_name)
            requestedPlatfromTemp, created = Requested_platform.objects.get_or_create(jobdescription=myObj, cmtconfig=platformTemp)
        
        return HttpResponse(json.dumps({ 'exists' : False, 'job_id' : myObj.id }))
@login_required
def editPanel(request):
    all_attributes = []
    if request.GET['service'] == 'platforms':
        all_attributes = map(str,Platform.objects.values_list('cmtconfig', flat=True).distinct())
        
    if request.GET['service'] == 'handlers':     
        all_attributes = map(str,Handler.objects.values_list('name', flat=True).distinct())

    all_attributes.sort()
    return HttpResponse(json.dumps({ 'available' : all_attributes }))

#@login_required comment in order the wget can work on this one
def script(request):
    if not 'pk' in request.GET:
        return HttpResponse("<h3>Not primary key was given lol.</h3>")
    if  not len(request.GET) ==  1:
        return HttpResponse("<h3>Only one get attribute is allowed lol.</h3>")
    try:
        int(request.GET['pk'])
    except Exception:
        return HttpResponse("<h3>Not valid integer primary key was given lol.</h3>")
    
    myJobDes = JobDescription.objects.get(pk=request.GET['pk'])
    filename = 'trolololo'+str(myJobDes.pk)
    application = myJobDes.application.appName
    version = myJobDes.application.appVersion
    try:
        setup_project =  myJobDes.setup_project.content
    except Exception:
        setup_project = ''
    options = myJobDes.options.content
    platforms = map(str,Requested_platform.objects.filter(jobdescription__exact=myJobDes).values_list('cmtconfig__cmtconfig', flat=True).distinct())       
    handlers = map(str,JobHandler.objects.filter(jobDescription__exact=myJobDes).values_list('handler__name', flat=True).distinct())
    
    file_lines = [filename,
                  '#!/bin/bash',
                  '\n\n',
                  '#job description id',
                  '\n',
                  'JOB_DESCRIPTION_ID='+str(myJobDes.pk),
                  '\n\n'
                  'HANDLERS="'+','.join(handlers)+'"',
                  '\n',
                  '#PLATFORMS="'+','.join(platforms)+'"',
                  '\n\n',
                  '. SetupProject.sh '+str(application)+' '+str(version)+' '+str(setup_project),
                  '\n\n',
                  'START=`date +"%Y-%m-%d,%T"`\n',
                  'gaudirun.py '+str(options),
                  '\n',
                  'END=`date +"%Y-%m-%d,%T"`',
                  '\n\n',
                  'git clone /afs/cern.ch/lhcb/software/GIT/LHCbPR\n'
                  'git clone /afs/cern.ch/lhcb/software/GIT/LHCbPRHandlers\n',
                  'export PYTHONPATH=$PYTHONPATH:LHCbPRHandlers:.\n\n'
                  '#use python version 2.6\n'
                  'python LHCbPRHandlers/collectRunResults.py -s ${START} -e ${END} -p `hostname` -c ${CMTCONFIG} -j ${JOB_DESCRIPTION_ID} -l ${HANDLERS}\n',
                  'python LHCbPR/django_apps/manage.py pushToDB json_results',
                  ]
    
    script = ''
    for line in file_lines[1:]:
        script += line
    
    return HttpResponse(script, mimetype="text/plain")
    