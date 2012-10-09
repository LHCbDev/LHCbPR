# Create your views here.
from django.db.models import Q
from django.db import connection, transaction
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt    
from django.template import RequestContext
from django.core import serializers
from django.conf import settings

from lhcbPR.models import Host, JobDescription, Requested_platform, Platform, Application, Options, SetupProject, Handler, JobHandler, Job, JobResults, ResultString, ResultFloat, ResultInt, ResultBinary
import json, subprocess, sys, re, copy, os
from random import choice
from tools.viewTools import handle_uploaded_file, makeQuery, makeCheckedList, dictfetchall

#***********************************************
from django.contrib.auth.decorators import login_required
from django.contrib.auth import BACKEND_SESSION_KEY
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def test(request):
    """Just a test view which serves testing hmtl pages,
    for the moment it serves the jquery ui examples page"""
    myauth = request.user.is_authenticated()
    myDict = { 'myauth' : myauth, 'user' : request.user}
    return render_to_response('lhcbPR/index.html', myDict,
                  context_instance=RequestContext(request))
      
def index(request):
    """This view serves the home page of the application(lhcbPR), along 
    with the page it provides information for the user(if he is authenticated
    or not)"""
    myauth = request.user.is_authenticated()
    myDict = { 'myauth' : myauth, 'user' : request.user}
    return render_to_response('lhcbPR/indexOf.html', myDict,
                  context_instance=RequestContext(request))

@login_required  #login_url="login"
def jobDescriptions(request, app_name):
    """From the url is takes the requested application(app_name) , example:
    /django/lhcbPR/jobDescriptions/BRUNEL ==> app_name = 'BRUNEL' 
    and depending on the app_name it returns the available versions, options, setupprojects"""
    
    applicationsList = map(str,Application.objects.values_list('appName', flat=True).distinct())
        
    myauth = request.user.is_authenticated()
    
    apps = Application.objects.filter(appName__exact=app_name)
    if not apps:
        return HttpResponseNotFound("<h3>Page not found</h3>")        
    
    appVersions = JobDescription.objects.filter(application__appName__exact=app_name).values_list('application__appVersion', flat=True).distinct()
    
    if not appVersions:
        return HttpResponseNotFound("<h3>No existing job descriptions for this application yet.</h3>")
    
    options = Options.objects.values_list('description', flat=True).distinct()
    platforms = Platform.objects.values_list('cmtconfig', flat=True).distinct()
    setupProject = SetupProject.objects.values_list('description', flat=True).distinct()
    
    #the GET request may also have information about which versions,options etc the user wants to 
    #to be checked in the filtering checkboxes(used for bookmarking the jobDescriptions page)
    #so it gets all versions,options... for the requested application(from app_name) and checks which 
    #of them exists in GET request values and using the makeCheckedList method it creates the proper lists to
    #to redirected back to the user
    if 'appVersions' in request.GET:
        appVersionsList = makeCheckedList(appVersions,request.GET['appVersions'].split(','))
    else:
        appVersionsList = makeCheckedList(appVersions)
    if 'platforms' in request.GET:
        cmtconfigsList = makeCheckedList(platforms, request.GET['platforms'].split(','))
    else:
        cmtconfigsList = makeCheckedList(platforms)
    if 'SetupProjects' in request.GET:
        setupProjectList = makeCheckedList(setupProject, request.GET['SetupProjects'].split(','))
    else:
        setupProjectList = makeCheckedList(setupProject)
    if 'Options' in request.GET:
        optionsList = makeCheckedList(options,request.GET['Options'].split(','))
    else:
        optionsList = makeCheckedList(options)
    if 'page' in request.GET:
        requested_page = request.GET['page']
    else:
        requested_page = 1
    
    #then create the final data dictionary
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
    """Serves the jobDescriptions home page with the available applications"""
    applications = Application.objects.values('appName').distinct('appName')
    
    applicationsList = []
    for dict in applications:  
        applicationsList.append(dict['appName'])
    myauth = request.user.is_authenticated()
    myDict = { 'myauth' : myauth, 'user' : request.user, 'applications' : applicationsList }
      
    return render_to_response('lhcbPR/jobDescriptionsHome.html', 
                  myDict,
                  context_instance=RequestContext(request))
@login_required 
def analyseHome(request):
    """To be used later when we start developing the analyzing functions for the 
    lhcbpr application"""
    
    #find for which applications there are runned jobs
    applicationsList = list(Job.objects.values_list('jobDescription__application__appName',flat=True).distinct())
        
    myauth = request.user.is_authenticated()
    
    myauth = request.user.is_authenticated()
    myDict = { 'myauth' : myauth, 'user' : request.user, 'applications' : applicationsList }
      
    return render_to_response('lhcbPR/analyseHome.html', 
                  myDict,
                  context_instance=RequestContext(request))

@login_required  #login_url="login"
def analyse(request, app_name):
    """From the url is takes the requested application(app_name) , example:
    /django/lhcbPR/jobDescriptions/BRUNEL ==> app_name = 'BRUNEL' 
    and depending on the app_name it returns the available versions, options, setupprojects"""
    applicationsList = list(Job.objects.values_list('jobDescription__application__appName',flat=True).distinct())
    myauth = request.user.is_authenticated()
    
    apps = Application.objects.filter(appName__exact=app_name)
    if not apps:
        return HttpResponseNotFound("<h3>Page not found, no such application</h3>")     
    
    atrs = map(str, JobResults.objects.filter(job__jobDescription__application__appName__exact=app_name).values_list('jobAttribute__name', flat=True).distinct())
    
    #cursor = connection.cursor()
    #get all available(saved from runned jobs) attribute names for the requested application 
    #cursor.execute("select att.name from lhcbpr_job j, lhcbpr_jobresults r, lhcbpr_jobattribute att, lhcbpr_application apl, lhcbpr_jobdescription jobdes where j.id = r.job_id and jobdes.id = j.jobdescription_id and apl.id = jobdes.application_id and apl.appname = '{0}' and r.jobattribute_id = att.id".format(app_name))
    #atrs = cursor.fetchall()
    
    platforms = Job.objects.filter(jobDescription__application__appName=app_name).values_list('platform__cmtconfig', flat=True).distinct()
    hosts = Job.objects.filter(jobDescription__application__appName=app_name).values_list('host__hostname', flat=True).distinct()
    jobdes = Job.objects.filter(jobDescription__application__appName=app_name).values_list('jobDescription__pk',flat=True).distinct()
    versions = Job.objects.filter(jobDescription__application__appName=app_name).values_list('jobDescription__application__appVersion', flat=True).distinct()
    
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
    if 'JobDes' in request.GET:
        checked_jobdes = request.GET['JobDes'].split(',')
    else:
        checked_jobdes = []

    jobdesList = []
    for j_pk in jobdes:
        j_temp = JobDescription.objects.get(pk=j_pk)
        
        jobdes_value = j_temp.application.appVersion+' '+j_temp.options.description
        try:
          j_temp.setup_project.description
        except Exception:
            pass
        else:
           jobdes_value+=' '+j_temp.setup_project.description    
          
        if j_temp.pk in checked_jobdes:
            jobdesList.append({'id': j_temp.pk, 'checked': True, 'value': jobdes_value })
        else:
            jobdesList.append({'id': j_temp.pk, 'checked': False, 'value': jobdes_value })
  
    
    dataDict = { 'attributes' : atrs,
                'platforms' : platformsList,
                'hosts' : hostsList,
                'jobdescr' : jobdesList,
                'versions' : versionsList,
                'active_tab' : app_name ,
                'myauth' : myauth, 
                'user' : request.user, 
                'applications' : applicationsList,
               }
      
    return render_to_response('lhcbPR/analyse.html', 
                  dataDict,
                  context_instance=RequestContext(request))

@login_required
def queryOverview(request):
    if request.method == 'GET' and 'hosts' in request.GET and 'jobdes' in request.GET and 'platforms' in request.GET and 'atr' in request.GET:
        
        query = 'SELECT j.jobdescription_id, h.hostname, plat.cmtconfig, count(*) as "Number", \n'
        query += 'round(avg(rf.data), 2) as Average, round(stddev(rf.data), 2) as stddev,\n'
        query +=' round(stddev(rf.data)/avg(rf.data) * 100, 2) as stddev_per, \n'
        query += ' round(avg((extract( second from  (time_end - time_start)) + extract( minute from  (time_end - time_start)) * 60 + extract ( hour  from  (time_end - time_start)) * 3600)),2) totaltime_avg \n'
        query += ' FROM lhcbpr_job j, lhcbpr_jobresults r, lhcbpr_jobattribute att,\n'
        query += ' lhcbpr_resultfloat rf, lhcbpr_host h, lhcbpr_platform plat \n'
        query += ' WHERE j.id = r.job_id and plat.id = j.platform_id AND h.id = j.host_id \n'
        query += ' AND r.jobattribute_id = att.id AND rf.jobresults_ptr_id = r.id \n'
        query += " AND att.name ='{0}'".format(request.GET['atr'])
        
        hosts = request.GET['hosts'].split(',')
        host_temp = []
        if not hosts[0] == "":
            for h in hosts:
                host_temp.append("h.hostname = '"+h+"'")
            
            query += ' AND ( '+' OR '.join(host_temp)+' ) \n'
        
        jobdes = request.GET['jobdes'].split(',')
        jobdes_temp = []
        if not jobdes[0] == "":
            for j in jobdes:
                jobdes_temp.append("j.jobdescription_id = '"+j+"'")
            
            query += ' AND ( '+' OR '.join(jobdes_temp)+' ) \n'
        
        platforms = request.GET['platforms'].split(',')
        platforms_temp = []
        if not platforms[0] == "":
            for p in platforms:
                platforms_temp.append("plat.cmtconfig = '"+p+"'")
            
            query += ' AND ( '+' OR '.join(platforms_temp)+' ) \n'
            
        query+= 'GROUP BY j.jobdescription_id, h.hostname, plat.cmtconfig;\n'
        
        
        return HttpResponse(query, mimetype="text/plain")
    
@login_required
def query(request):
    if request.method == 'GET' and 'hosts' in request.GET and 'jobdes' in request.GET and 'platforms' in request.GET and 'atr' in request.GET:
        
        query = 'SELECT j.jobdescription_id, h.hostname, plat.cmtconfig, count(*) as "Number", round(avg(rf.data), 2) as Average, round(stddev(rf.data), 2) as stddev, round(stddev(rf.data)/avg(rf.data) * 100, 2) as stddev_per, '
        query += ' round(avg((extract( second from  (time_end - time_start)) + extract( minute from  (time_end - time_start)) * 60 + extract ( hour  from  (time_end - time_start)) * 3600)),2) totaltime_avg '
        query += 'FROM lhcbpr_job j, lhcbpr_jobresults r, lhcbpr_jobattribute att,lhcbpr_resultfloat rf, lhcbpr_host h, lhcbpr_platform plat '
        query += 'WHERE j.id = r.job_id and plat.id = j.platform_id AND h.id = j.host_id AND r.jobattribute_id = att.id AND rf.jobresults_ptr_id = r.id '
        query += "AND att.name ='{0}'".format(request.GET['atr'])
        
        hosts = request.GET['hosts'].split(',')
        host_temp = []
        if not hosts[0] == "":
            for h in hosts:
                host_temp.append("h.hostname = '"+h+"'")
            
            query += ' AND ( '+' OR '.join(host_temp)+' ) '
        
        jobdes = request.GET['jobdes'].split(',')
        jobdes_temp = []
        if not jobdes[0] == "":
            for j in jobdes:
                jobdes_temp.append("j.jobdescription_id = '"+j+"'")
            
            query += ' AND ( '+' OR '.join(jobdes_temp)+' ) '
        
        platforms = request.GET['platforms'].split(',')
        platforms_temp = []
        if not platforms[0] == "":
            for p in platforms:
                platforms_temp.append("plat.cmtconfig = '"+p+"'")
            
            query += ' AND ( '+' OR '.join(platforms_temp)+' ) '
            
        query+= 'GROUP BY j.jobdescription_id, h.hostname, plat.cmtconfig;'
        
        #establish connection
        cursor = connection.cursor()
        #execute query
        cursor.execute(query)
        answerDict = dictfetchall(cursor)
        
        return HttpResponse(json.dumps(answerDict))

@login_required
def getFiltersAnalyse(request):
    """Gets the filtering values for the request and returns the jobDescriptions which 
    agree with the filtering values(query to the database)"""
    results_per_page = 15
    if request.method == 'GET':
    
        querylist = []
        
        if request.GET['app']:
            querylist.append(makeQuery('jobDescription__application__appName__exact', request.GET['app'].split(','), Q.OR))
        if request.GET['appVersions']:
            querylist.append(makeQuery('jobDescription__application__appVersion__exact', request.GET['appVersions'].split(','), Q.OR))
        if request.GET['Options']:
            querylist.append(makeQuery('jobDescription__options__description__exact',request.GET['Options'].split(','), Q.OR))
        if request.GET['SetupProjects']:
            querylist.append(makeQuery('jobDescription__setup_project__description__exact',request.GET['SetupProjects'].split(','), Q.OR))
        if request.GET['platforms']:
           querylist.append(makeQuery('platform__cmtconfig__exact', request.GET['platforms'].split(','), Q.OR))
        
        final_query = Q()
        for q in querylist:
           final_query &= q 
        
        jobsTemp = Job.objects.filter(final_query).distinct('jobDescription')     
        
        
        myJobDescriptions = []
        for jd in jobsTemp:
            myJobDescriptions.append(jd.jobDescription)
        unique_jobDescriptions = list(set(myJobDescriptions))
        paginator = Paginator(unique_jobDescriptions ,results_per_page)
        requested_page = request.GET['page']
        
        try:
            jobsDes = paginator.page(requested_page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            jobsDes = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            jobsDes = paginator.page(paginator.num_pages)
        
        
        myobjectlist = []
        
        for j in jobsDes.object_list :#jobsTemp
            myDict={ 'pk' : j.id,   
                     'appName' : j.application.appName,
                     'appVersion' : j.application.appVersion,
                     'optionsD' : j.options.description,
                     } 
            try:
                myDict['setupproject'] = j.jobDescription.setup_project.description
            except Exception:
                myDict['setupproject'] = ""
            
            myobjectlist.append(myDict)
            
        pageIngo = {
                    'num_of_pages' : paginator.num_pages,
                    'current_page' : jobsDes.number,
                    'total_results' : len(unique_jobDescriptions)
                    }
        
        return HttpResponse(json.dumps({ 'jobs' :  myobjectlist, 'page_info' : pageIngo }))
  
@login_required
def getFilters(request):
    """Gets the filtering values for the request and returns the jobDescriptions which 
    agree with the filtering values(query to the database)"""
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
                     'optionsD' : j.options.description,
                     } 
            try:
                myDict['setupproject'] = j.setup_project.description
            except Exception:
                myDict['setupproject'] = ""
            
            myobjectlist.append(myDict)
            
        pageIngo = {
                    'num_of_pages' : paginator.num_pages,
                    'current_page' : jobDes.number,
                    'total_results' : jobDesTemp.count()
                    }
        
        return HttpResponse(json.dumps({ 'jobs' :  myobjectlist, 'page_info' : pageIngo }))

@login_required
def getJobDetails(request):
    """Gets a job description id from the GET request and returns back all the available information
    for the requested job description options,setupproject,handlers,platforms etc, also if the request comes 
    from the clone or edit dialogs(from the web interface) it returns all the available handlers/platforms/options etc"""
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
    
    #if the request comes from the edit or clone dialog(web iterface) send all available
    #needed information(this information is used to create a new job description or edit 
    #an existing one, so the user needs to have (except from the information for the choosed job description)
    #all the available values for options/setupprojects etc
    if 'cloneRequest' or 'editRequest' in request.GET:
        dataDict['versionsAll'] = map(str,Application.objects.filter(appName__exact=myJob.application.appName).values_list('appVersion', flat=True).distinct())
        dataDict['optionsAll'] = map(str,Options.objects.all().values_list('content', flat=True).distinct())
        dataDict['optionsDAll'] = map(str,Options.objects.all().values_list('description', flat=True).distinct())
        dataDict['setupAll'] = map(str,SetupProject.objects.all().values_list('content', flat=True).distinct())
        dataDict['setupDAll'] = map(str,SetupProject.objects.all().values_list('description', flat=True).distinct())
    
    #check if the jobdescription exists in runned jobs so the user can edit or not some attributes
    runned_jobs = Job.objects.filter(jobDescription__pk=request.GET['job_id']).count()
    if runned_jobs > 0:
        dataDict['runned_job'] = True
    else:
        dataDict['runned_job'] = False
        
                
    return HttpResponse(json.dumps(dataDict))
    
@login_required
def commitClone(request):
    """This view checks if a commit request from the user(add new job description/or edit an existing one) is valid.
    if it's valid it updates/creates the old/new job description, which means add/edit handler,requested platforms, options etc"""
    
    
    optObj = Options.objects.filter(description__exact=request.GET['optionsD'])
    if optObj.count() > 0:
        if not optObj[0].content == request.GET['options']:
            return HttpResponse(json.dumps({ 'error' : True, 'errorMessage' : 'Using existing Options description with wrong corresponding content' , 
                             'content' : optObj[0].content, 'description' : optObj[0].description  }))
    
    optObjD = Options.objects.filter(content__exact=request.GET['options'])
    if optObjD.count() > 0:
        if not optObjD[0].description == request.GET['optionsD']:
            return HttpResponse(json.dumps({ 'error' : True, 'errorMessage' : 'Using existing Options content with wrong corresponding description' , 
                             'content' : optObjD[0].content, 'description' : optObjD[0].description  }))
    
    if not request.GET['setupproject'] == "" and not request.GET['setupprojectD'] == "":
        setupObj = SetupProject.objects.filter(description__exact=request.GET['setupprojectD'])
        if setupObj.count() > 0:
            if not setupObj[0].content == request.GET['setupproject']:
                return HttpResponse(json.dumps({ 'error' : True, 'errorMessage' : 'Using existing SetupProject description with wrong corresponding content' , 
                          'content' : setupObj[0].content, 'description' : setupObj[0].description  }))
        
        setupObjD = SetupProject.objects.filter(content__exact=request.GET['setupproject'])
        if setupObjD.count() > 0:
            if not setupObjD[0].description == request.GET['setupprojectD']:
                return HttpResponse(json.dumps({ 'error' : True, 'errorMessage' : 'Using existing SetupProject content with wrong corresponding description' , 
                             'content' : setupObjD[0].content, 'description' : setupObjD[0].description  }))
    
    #if the request is an edit request
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
        
        return HttpResponse(json.dumps({ 'error' : False, 'updated' : True, 'job_id' : myObj.id }))
    
    
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
        return HttpResponse(json.dumps({ 'error': False , 'exists': True }))
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
        
        return HttpResponse(json.dumps({'error' : False,  'exists' : False, 'job_id' : myObj.id }))
@login_required
def editPanel(request):
    """Serves the information is needed for the editing handlers/platforms dialog, just sends back
    all available handlers and platforms"""
    all_attributes = []
    if request.GET['service'] == 'platforms':
        all_attributes = map(str,Platform.objects.values_list('cmtconfig', flat=True).distinct())
        
    if request.GET['service'] == 'handlers':     
        all_attributes = map(str,Handler.objects.values_list('name', flat=True).distinct())

    all_attributes.sort()
    return HttpResponse(json.dumps({ 'available' : all_attributes }))

#@login_required comment in order the wget can work on this one
def script(request):
    """Takes a job description id from the GET request and creates the corresponding script for the
    requested id, it's the script which the user will use to run it's job, call handlers to collect
    the run results, push the data to the database(uses the right options, handlers list etc)"""
    if not 'pk' in request.GET:
        return HttpResponse("<h3>Not primary key was given lol.</h3>")
    if  not len(request.GET) ==  1:
        return HttpResponse("<h3>Only one GET attribute is allowed lol.</h3>")
    try:
        int(request.GET['pk'])
    except Exception:
        return HttpResponse("<h3>Not valid integer primary key was given lol.</h3>")
    
    myJobDes = JobDescription.objects.get(pk=request.GET['pk'])
    application = myJobDes.application.appName
    version = myJobDes.application.appVersion
    try:
        setup_project =  myJobDes.setup_project.content
    except Exception:
        setup_project = ''
    options = myJobDes.options.content
    platforms = map(str,Requested_platform.objects.filter(jobdescription__exact=myJobDes).values_list('cmtconfig__cmtconfig', flat=True).distinct())       
    handlers = map(str,JobHandler.objects.filter(jobDescription__exact=myJobDes).values_list('handler__name', flat=True).distinct())
    
    file_lines = [
                  '#!/bin/bash\n\n',
                  '#this script produced by: {0} machine\n\n'.format(settings.HOSTNAME),
                  '#job description id\n',
                  'JOB_DESCRIPTION_ID='+str(myJobDes.pk)+'\n\n',
                  'HANDLERS="'+','.join(handlers)+'"\n',
                  '#PLATFORMS="'+','.join(platforms)+'"\n\n',
                  '. SetupProject.sh {0} {1} {2}\n\n'.format(str(application), str(version), str(setup_project)),
                  'START=`date +"%Y-%m-%d,%T"`\n',
                  'gaudirun.py {0} 2>&1 > run.log\n'.format(str(options)),
                  'END=`date +"%Y-%m-%d,%T"`\n\n',
                  '#the next command, downloads the LHCbPRHandlers, unzips the file, removes the zip file(overrides previous folder/files, if any)\n',
                  "python -c \"import os,urllib,zipfile;urllib.urlretrieve('http://lhcbproject.web.cern.ch/lhcbproject/GIT/dist/LHCbPRHandlers/LHCbPRHandlers.zip','LHCbPRHandlers.zip');unzipper=zipfile.ZipFile('LHCbPRHandlers.zip');unzipper.extractall();os.remove('LHCbPRHandlers.zip')\"\n\n",
                  '#use python version 2.6\n',
                  '#the collectRunResults has by default the -a argument which automatically sends the data\n',
                  '#to the database, if you want to do it manually remove -a argument and uncomment the sendToDB script\n',
                  'python LHCbPRHandlers/collectRunResults.py -s ${START} -e ${END} -p `hostname` -c ${CMTCONFIG} -j ${JOB_DESCRIPTION_ID} -l ${HANDLERS} -a\n',
                  '#python LHCbPRHandlers/sendToDB.py -s name_of_zip',
                  ]
    
    script = ''
    for line in file_lines:
        script += line
    
    return HttpResponse(script, mimetype="text/plain")

def getRunnedJobs(request):
    """Just an example of printing information about runned jobs(summary, collected results for each job etc)
    to be replaced soon, choose randomly one runned job for the requested job description"""
    if not 'pk' in request.GET:
        return HttpResponse("<h3>Not primary key was given lol.</h3>")
    if  not len(request.GET) ==  1:
        return HttpResponse("<h3>Only one GET attribute is allowed lol.</h3>")
    try:
        int(request.GET['pk'])
    except Exception:
        return HttpResponse("<h3>Not valid integer primary key was given lol.</h3>")
    
    details = ''
    #runnedJobs = Job.objects.filter(jobDescription__pk=request.GET['pk'])
    total = Job.objects.filter(jobDescription__pk=request.GET['pk']).count()
    jobTemp = choice(Job.objects.filter(jobDescription__pk=request.GET['pk']))
    #for jobTemp in runnedJobs:
    details+='\nTotal number of runned jobs: '+str(total)+'\n\n'
    details+='Sample of the collected attributes of a random runned job\n'
    details+='-------------------------------- Job details-----------------------------------------------\n'
    details+='Job id: '+str(jobTemp.id)+'\n'
    details+='Host:'+jobTemp.host.hostname+'\n'
    details+='Job description id:'+str(jobTemp.jobDescription.id)+'\n'
    details+='Platform:'+jobTemp.platform.cmtconfig+'\n'
    details+='Start time:'+str(jobTemp.time_start)+'\n'
    details+='End time time:'+str(jobTemp.time_end)+'\n'
    details+='Status:'+jobTemp.status+'\n'
    
    details+='{0:30} ===> {1:30}\n'.format('Attribute Name', 'Value')
    attributesList = []
    attributesList.extend(JobResults.objects.filter(job__pk=jobTemp.pk))
    #attributesList.extend(ResultBinary.objects.filter(job__pk=jobTemp.pk))
    
    for attr in attributesList:
        if attr.jobAttribute.type == 'Float':
            details+='{0:30} ===> {1:30}\n'.format(attr.jobAttribute.name, str(attr.resultfloat.data))
        elif attr.jobAttribute.type == 'Integer':
            details+='{0:30} ===> {1:30}\n'.format(attr.jobAttribute.name, str(attr.resultint.data))
        elif attr.jobAttribute.type == 'String':
            details+='{0:30} ===> {1:30}\n'.format(attr.jobAttribute.name, str(attr.resultstring.data))
        
    details+='\n\n'
    
    return HttpResponse(details, mimetype="text/plain")

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        handle_uploaded_file(request.FILES['file'])
        return HttpResponse('Server message: Uploading results zip file was successful')
    