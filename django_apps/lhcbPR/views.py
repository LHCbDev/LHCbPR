import logging
from django.db.models import Q
from django.db import connection, transaction, DatabaseError, IntegrityError
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt    
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.decorators import login_required as default_login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files import File 

from lhcbPR.models import HandlerResult, Host, JobDescription, Requested_platform, Platform, Application, Options, SetupProject, Handler, JobHandler, Job, JobResults
import json, subprocess, sys, re, copy, os
from pprint import pformat
from exceptions import AttributeError
from random import choice
from tools.viewTools import handle_uploaded_file, makeQuery, formBuilder, getSplitted, jobdescription

#get the loggers
logger = logging.getLogger('views_logger')
logger_analysis = logging.getLogger('analysis_logger')

#this is used to skip the login_required decorator in case of local developing
if settings.LOCAL:
    def login_required(*args):
        return args[0]
else:
    login_required = default_login_required

@csrf_exempt
@login_required
def test(request):
    return HttpResponse('dummy_response')
    
def index(request):
    """This view serves the home page of the application(lhcbPR), along 
    with the page it provides information for the user(if he is authenticated
    or not)"""

    query = "SELECT * FROM lhcbpr_public_links" 
    cursor = connection.cursor()
    cursor.execute(query)
    links = cursor.fetchall()

    dataDict = {
       'links': json.dumps(links)
    }

    return render_to_response('lhcbPR/index.html',
       dataDict,
       context_instance=RequestContext(request))
    
@login_required
def saveUrl(request):
    ''' Method to store links for application into lhcbpr database.'''
    if request.method == 'GET':
        requestData = request.GET
    else:
        requestData = request.POST
    
    app  = requestData['app']
    url  = requestData['url']
    dscp = requestData['description']

    print app, " - ", url, " - ", dscp
    #
    # Here is a security measure missing to avoid adding anything.
    #

    query = ""
    if app != "" and url != "" and dscp != "":
        query = "INSERT INTO LHCBPR_PUBLIC_LINKS \
           (APPNAME, LINK, DESCRIPTION) VALUES \
           ('{0}', '{1}', '{2}')".format(app, url, dscp)

    #print query

    cursor = connection.cursor()
    cursor.execute(query)

    try:
        transaction.commit_unless_managed()
    except DatabaseError, IntegrityError:
        succ = False
    else:
        succ = True

    dataDic = {
        'app' : app,
        'url' : url,
        'dscp': dscp, 
        'succ': succ
    }

    return render_to_response('lhcbPR/success.html', dataDic, context_instance=RequestContext(request))

@login_required
def jobDescriptions(request, app_name):
    """From the url is takes the requested application(app_name) , example:
    /jobDescriptions/BRUNEL ==> app_name = 'BRUNEL' 
    and depending on the app_name it returns the available versions, options, setupprojects
    and a list of existing job descriptions(this happens with ajax and not from this view)"""
    
    #get a list of appications
    applicationsList = Application.objects.values_list('appName', flat=True).distinct().order_by('appName')
    
    #if the application does not exist raise 404
    apps = Application.objects.filter(appName__exact=app_name)
    if not apps:
        raise Http404
    
    #get the application versions and then sort them in a custom way
    appVersions_temp = Application.objects.filter(jobdescriptions__application__appName__exact= app_name).values_list('id','appVersion').distinct() 
    appVersions = reversed(sorted(appVersions_temp, key = lambda ver : getSplitted(ver[1])))
    
    if not appVersions:
        return HttpResponseNotFound("<h3>No existing job descriptions for this application yet.</h3>")
    
    #after get the options, platforms and setupproject of the corresponding application
    options = Options.objects.filter(jobdescriptions__application__appName=app_name).values_list('id', 'description').distinct().order_by('description')
    
    platforms = Platform.objects.values_list('id','cmtconfig').distinct().order_by('cmtconfig')
    
    setupProject = SetupProject.objects.filter(jobdescriptions__application__appName=app_name).values_list('id','description').distinct().order_by('description')
            
    if request.method == 'GET':
        requestData = request.GET
    else:
        requestData = request.POST
    
    
    if 'page' in requestData:
        requested_page = requestData['page']
    else:
        requested_page = 1

    #then create the final data dictionary
    dataDict = { 'appVersions' : appVersions,
               'options' : options,
               'platforms' : platforms,
               'setupProject' : setupProject,
               'active_tab' : app_name , 
               'applications' : applicationsList,
               'current_page' : requested_page,
               'bookmark' : json.dumps(requestData)
               }
    
    return render_to_response('lhcbPR/jobDescriptions.html', 
                  dataDict,
                  context_instance=RequestContext(request))
   
@login_required 
def joblistDescHome(request):
   """List of available jobs and runns"""
   return joblistDesc(request, "")

@login_required 
def joblistDesc(request, app_name):
   """List of available jobs and runns"""
   cnf_query = "SELECT DISTINCT \
      LHCBPR_JOBDESCRIPTION.ID, \
      LHCBPR_APPLICATION.APPNAME, \
      LHCBPR_APPLICATION.APPVERSION, \
      LHCBPR_PLATFORM.ID, \
      LHCBPR_PLATFORM.CMTCONFIG, \
      LHCBPR_OPTIONS.DESCRIPTION, \
      LHCBPR_OPTIONS.CONTENT, \
      LHCBPR_SETUPPROJECT.DESCRIPTION AS SETUP_DESC, \
      LHCBPR_SETUPPROJECT.CONTENT AS CONTENT1, \
      (SELECT max( \
        extract(day from (LHCBPR_JOB.TIME_END-timestamp '1970-01-01 00:00:00 +00:00'))*86400+ \
        extract(hour from (LHCBPR_JOB.TIME_END-timestamp '1970-01-01 00:00:00 +00:00'))*3600+ \
        extract(minute from (LHCBPR_JOB.TIME_END-timestamp '1970-01-01 00:00:00 +00:00'))*60+ \
        extract(second from (LHCBPR_JOB.TIME_END-timestamp '1970-01-01 00:00:00 +00:00'))) \
        FROM LHCBPR_JOB WHERE lhcbpr_job.jobdescription_id = LHCBPR_JOBDESCRIPTION.ID) AS ENDTIME, \
      CAST(SUM(LHCBPR_JOB.SUCCESS)/COUNT(*) AS FLOAT), \
      COUNT(*) \
      FROM LHCBPR_JOB \
      INNER JOIN LHCBPR_PLATFORM \
      ON LHCBPR_PLATFORM.ID = LHCBPR_JOB.PLATFORM_ID \
      INNER JOIN LHCBPR_JOBDESCRIPTION \
      ON LHCBPR_JOBDESCRIPTION.ID = LHCBPR_JOB.JOBDESCRIPTION_ID \
      INNER JOIN LHCBPR_APPLICATION \
      ON LHCBPR_APPLICATION.ID = LHCBPR_JOBDESCRIPTION.APPLICATION_ID \
      INNER JOIN LHCBPR_OPTIONS \
      ON LHCBPR_OPTIONS.ID = LHCBPR_JOBDESCRIPTION.OPTIONS_ID \
      INNER JOIN LHCBPR_SETUPPROJECT \
      ON LHCBPR_SETUPPROJECT.ID = NVL(LHCBPR_JOBDESCRIPTION.SETUP_PROJECT_ID, 1)"

   query = ""
   if not app_name == "All":
      query = " WHERE LHCBPR_APPLICATION.APPNAME = \'{0}\'".format(app_name)

   cnf_query += query

   cnf_query += " GROUP BY LHCBPR_JOBDESCRIPTION.ID, \
     LHCBPR_APPLICATION.APPNAME, \
     LHCBPR_APPLICATION.APPVERSION, \
     LHCBPR_PLATFORM.ID, \
     LHCBPR_PLATFORM.CMTCONFIG, \
     LHCBPR_OPTIONS.DESCRIPTION, \
     LHCBPR_OPTIONS.CONTENT, \
     LHCBPR_SETUPPROJECT.DESCRIPTION, \
     LHCBPR_SETUPPROJECT.CONTENT"

   cnf_query += " ORDER BY ENDTIME DESC"
   # print "Joblist Query: ", cnf_query

   cursor = connection.cursor()
   cursor.execute(cnf_query)
   description = [i[0] for i in cursor.description]
   configurations = cursor.fetchall()

   applicationList = Application.objects.values_list('appName',flat=True).distinct().order_by('appName')

   return render_to_response('lhcbPR/joblistHome.html',
                  { 'configs' : json.dumps(configurations),
                    'active_tab' : app_name,
                    'description' : description,
                    'applications' : applicationList
                  },
                  context_instance=RequestContext(request))

@login_required 
def joblistInfo(request, app_name, desc_id, plat_id):
   """Detailed information of jobs belonging to a certain job_description.id (configuration)."""
   if not desc_id:
      return HttpResponseNotFound("<h3>No existing jobs for job description or no job description given.</h3>")

   job_query = "SELECT LHCBPR_JOB.ID AS ID, \
      LHCBPR_APPLICATION.APPNAME AS Project, \
      LHCBPR_APPLICATION.APPVERSION AS Version, \
      LHCBPR_APPLICATION.ID AS APP_ID, \
      LHCBPR_PLATFORM.CMTCONFIG AS Platform, \
      LHCBPR_OPTIONS.DESCRIPTION AS Options, \
      LHCBPR_OPTIONS.ID AS OPT_ID, \
      TO_CHAR(LHCBPR_JOB.TIME_START, 'YYYY-MM-DD HH12:MI:SS AM') AS TIME_START, \
      TO_CHAR(LHCBPR_JOB.TIME_END, 'YYYY-MM-DD HH12:MI:SS AM') AS TIME_END, \
      LHCBPR_JOB.SUCCESS AS Stat \
      FROM LHCBPR_JOB \
      INNER JOIN LHCBPR_PLATFORM \
      ON LHCBPR_PLATFORM.ID = LHCBPR_JOB.PLATFORM_ID \
      INNER JOIN LHCBPR_JOBDESCRIPTION \
      ON LHCBPR_JOBDESCRIPTION.ID = LHCBPR_JOB.JOBDESCRIPTION_ID \
      INNER JOIN LHCBPR_APPLICATION \
      ON LHCBPR_APPLICATION.ID = LHCBPR_JOBDESCRIPTION.APPLICATION_ID \
      INNER JOIN LHCBPR_OPTIONS \
      ON LHCBPR_OPTIONS.ID = LHCBPR_JOBDESCRIPTION.OPTIONS_ID"
   
   query  = " WHERE LHCBPR_JOBDESCRIPTION.ID = {0}".format(desc_id)
   query += " AND LHCBPR_PLATFORM.ID = {0}".format(plat_id)

   job_query += query
   job_query += " ORDER BY LHCBPR_JOB.ID"

   #print job_query

   info_query = "SELECT LHCBPR_JOBRESULTS.JOB_ID, \
      LHCBPR_JOBATTRIBUTE.NAME, \
      LHCBPR_JOBATTRIBUTE.\"GROUP\", \
      LHCBPR_JOBATTRIBUTE.DESCRIPTION, \
      LHCBPR_RESULTSTRING.DATA \
      FROM LHCBPR_RESULTSTRING \
      INNER JOIN LHCBPR_JOBRESULTS \
      ON LHCBPR_JOBRESULTS.ID = LHCBPR_RESULTSTRING.JOBRESULTS_PTR_ID \
      INNER JOIN LHCBPR_JOBATTRIBUTE \
      ON LHCBPR_JOBRESULTS.JOBATTRIBUTE_ID = LHCBPR_JOBATTRIBUTE.ID \
      WHERE LHCBPR_JOBATTRIBUTE.\"GROUP\" = 'JobInfo' \
      ORDER BY LHCBPR_JOBRESULTS.JOB_ID, \
      LHCBPR_JOBATTRIBUTE.NAME"

   #print info_query

   file_query = "SELECT LHCBPR_JOBRESULTS.JOB_ID, \
     LHCBPR_JOBATTRIBUTE.NAME, \
     LHCBPR_RESULTFILE.\"FILE\" \
     FROM LHCBPR_JOBRESULTS \
     INNER JOIN LHCBPR_JOBATTRIBUTE \
     ON LHCBPR_JOBRESULTS.JOBATTRIBUTE_ID = LHCBPR_JOBATTRIBUTE.ID \
     INNER JOIN LHCBPR_RESULTFILE \
     ON LHCBPR_JOBRESULTS.ID = LHCBPR_RESULTFILE.JOBRESULTS_PTR_ID \
     ORDER BY LHCBPR_JOBRESULTS.JOB_ID"

   #print file_query

   group_query = "SELECT DISTINCT LHCBPR_JOBRESULTS.JOB_ID, \
     LHCBPR_JOBATTRIBUTE.\"GROUP\" \
     FROM LHCBPR_JOBRESULTS \
     INNER JOIN LHCBPR_JOBATTRIBUTE \
     ON LHCBPR_JOBRESULTS.JOBATTRIBUTE_ID = LHCBPR_JOBATTRIBUTE.ID \
     INNER JOIN LHCBPR_RESULTFLOAT \
     ON LHCBPR_RESULTFLOAT.JOBRESULTS_PTR_ID = LHCBPR_JOBRESULTS.ID \
     ORDER BY LHCBPR_JOBRESULTS.JOB_ID"

   #print group_query

   cursor = connection.cursor()
   cursor.execute(job_query)
   description = [i[0] for i in cursor.description]
   jobs = cursor.fetchall()

   cursor = connection.cursor()
   cursor.execute(info_query)
   description = [i[0] for i in cursor.description]
   infos = cursor.fetchall()

   cursor = connection.cursor()
   cursor.execute(file_query)
   description = [i[0] for i in cursor.description]
   files = cursor.fetchall()

   cursor = connection.cursor()
   cursor.execute(group_query)
   description = [i[0] for i in cursor.description]
   groups = cursor.fetchall()
 
   atr_groups = []
   for k, v in enumerate(groups):
      if v[0] != "":
         atr_groups.append([v[0], v[1]])

   applicationList = Application.objects.values_list('appName',flat=True).distinct().order_by('appName')

   return render_to_response('lhcbPR/joblistInfo.html',
                  {
                    'jobs'        : json.dumps(jobs),
                    'infos'       : json.dumps(infos),
                    'files'       : json.dumps(files),
                    'groups'      : json.dumps(groups),
                    'application' : app_name,
                    'active_tab'  : app_name,
                    'applications' : applicationList,
                    'description' : description
                  },
                  context_instance=RequestContext(request))

@login_required 
def jobFileView(request):
    """Returns file for download."""
    if request.method == 'GET':
        requestData = request.GET
    else:
        requestData = request.POST

    if requestData['file'] == "":
        return HttpResponse(json.dumps({ 'error' : True, 'errorMessage' : 'No file given.' }))

    data_store = "/afs/cern.ch/lhcb/software/webapps/LHCbPR/data/files/"
    data_file  = requestData['file']

    reco  = re.compile('\d+')
    names = reco.findall(data_file)

    reco  = re.compile('[0-9a-zA-Z.-]+$')
    name  = reco.findall(data_file)

    filename = "lhcbpr-%s-%s-%s" % (names[0], names[1], name[0])

    data_file  = data_store + data_file

    if not os.path.isfile(data_file):
        return HttpResponse(json.dumps({ 'error' : True, 'errorMessage' : 'File not readable.' }))

    fsock = open(data_file, 'r')
    response = HttpResponse(fsock, mimetype='text/html')
    response['Content-Disposition'] = "attachment; filename=%s" % (filename)
    return response

@login_required 
def jobDescriptionsHome(request):
    """Serves the jobDescriptions home page with the available applications"""
    applicationsList = Application.objects.values_list('appName',flat=True).distinct().order_by('appName')
    myDict = { 'applications' : applicationsList }
      
    return render_to_response('lhcbPR/jobDescriptionsHome.html', 
                  myDict,
                  context_instance=RequestContext(request))
@login_required 
def analyseHome(request):
    """Return the home page of the analysis, prints the applications for which exist saved jobs
    in the database"""
    
    #find for which applications there are runned jobs
    applicationsList = Job.objects.filter(success=True).values_list('jobDescription__application__appName',flat=True).distinct().order_by('jobDescription__application__appName')
    myDict = { 'applications' : applicationsList }
      
    return render_to_response('lhcbPR/analyseHome.html', 
                  myDict,
                  context_instance=RequestContext(request))

@login_required  #login_url="login"
def analysis_application(request, app_name):
    """Get the name of an application from the url and return all the available analysis modules for the
    selected application, the analysis modules(web pages) appear as html buttons. Each analysis module contains a method:
    isAvailableFor(app_name) it takes an application name and returns true or false whether this analysis is available for
    the current selected application or not"""
    applicationsList = Job.objects.filter(success=True).values_list('jobDescription__application__appName',flat=True).distinct().order_by('jobDescription__application__appName')
    
    apps = Application.objects.filter(appName__exact=app_name)
    if not apps:
        raise Http404
    
    #get a list of the successful handler for the selected application
    handlers = HandlerResult.objects.filter(job__jobDescription__application__appName=app_name).filter(success=True).values_list('handler__name',flat=True).distinct().order_by('handler__name')
    
    #get the contents of the analysis folder, each folder in the analysis represents a different analysis module
    analysis_dir = os.path.join(settings.PROJECT_PATH, 'analysis')
    modules = os.listdir(analysis_dir)
    
    #after loop over all the available modules
    analysisList = []
    for module in modules:
        #if the element is a directory, try to dynamically import it(check if no exception is occurred) to 
        #check if it is a valid python module
        if os.path.isdir(os.path.join(analysis_dir, module)):
            mod_import = 'analysis.{0}'.format(module)
            try:
                mod = __import__(mod_import, fromlist=[mod_import])
            except ImportError, e:
                logger_analysis.exception(e)
                return HttpResponseNotFound('<h3>An exception occurred please try again later</h3>')
            else:
                #if the module is imported properly check if it is available for the current selected application 
                if mod.isAvailableFor(app_name):
                    analysisList.append((module, module.upper()))
            
            analysisList.sort()
    dataDict = { 
                'handlers' : handlers,
                'active_tab' : app_name , 
                'applications' : applicationsList,
                'analysisList' : analysisList
               }
      
    return render_to_response('lhcbPR/analyse.html', 
                  dataDict,
                  context_instance=RequestContext(request))

@login_required
def analysis_render(request, analysis_type, app_name):
    """This function call the right render_to_response depending on the analysis
    type argument
    """
    if request.method == 'GET':
        requestData = request.GET
    else:
        requestData = request.POST

    module = 'analysis.{0}'.format(analysis_type)
    try:
        #try to import the module by each name eg basic, timing etc
        mod = __import__(module, fromlist=[module])
    except ImportError, e:
        logger_analysis.exception(e)
        return HttpResponseNotFound('<h3>Analyse {0} render was not found</h3>'.format(analysis_type))
    else:   
        #if the module is imported properly call the render function and take the data which
        #the analysis wants to use
        user_data = mod.render(request=request, requestData=requestData, app_name=app_name)
        
        #check if the user provided a custom template(different than the render.html)
        if 'template' in user_data:
            template = user_data['template']
        else:
            #else use the default custom template by the name render in the corresponding template path
            template = 'analysis/{0}/render.html'.format(analysis_type)
            template_dir = os.path.join(settings.TEMPLATE_DIRS[0], template)
            
            #if the user doesn't provide any template at all use the default one
            if not os.path.isfile(template_dir):
                template = 'analysis/default_render.html'
                if not 'form' in user_data:
                    #if the user has not provide any template nor an html form(check documentation)
                    #return as html_form a message to be rendered
                    user_data['html_form'] = """
<pre>
Attention:
    No render.html template was provided for this analysis.
    By using the default  but you must provide at least a 'form' key
    (at your data dictionary which you return) value which 
    contains an initial text input form, example:
                        
    my_text_elements_list = [
    #id of html element, text of the label, optional default value for the text input
    ('text_id', 'label content', 'default text value')
                                                ]
    return { 'form' : my_text_elements_list }                 
</pre> 
                    """
        
        #then check if the user has provided (through the analysis module) any options, versions objects etc
        #if not, use the default ones           
        if not 'options' in user_data:
            user_data['options'] = Options.objects.filter(jobdescriptions__jobs__success=True,jobdescriptions__application__appName=app_name).distinct().order_by('description')
        if not 'versions' in user_data:
            versions_temp = Application.objects.filter(jobdescriptions__jobs__success=True, appName=app_name).distinct()
            versions = sorted(versions_temp, key = lambda ver : getSplitted(ver.appVersion), reverse = True)
            user_data['versions'] = versions
        if not 'platforms' in user_data:
            user_data['platforms'] = Platform.objects.filter(jobs__success=True,jobs__jobDescription__application__appName=app_name).distinct().order_by('cmtconfig')
        if not 'hosts' in user_data:
            user_data['hosts'] = Host.objects.filter(jobs__success=True,jobs__jobDescription__application__appName=app_name).distinct().order_by('hostname')
        
        #as a helptext take the pydoc of the module
        help = mod.__doc__
        if help is None:
            help = 'This module is not documented yet.'
        
        #also as title of the web page take the title attribute of the module
        try:
            title = mod.title
        except AttributeError:
            title = analysis_type+' analysis'
        
        if 'form' in user_data:
            html_form = formBuilder(user_data['form'])
            del(user_data['form'])
            user_data['html_form'] = html_form

        applicationsList = Job.objects.filter(success=True).values_list('jobDescription__application__appName',flat=True).distinct().order_by('jobDescription__application__appName')

        dataDict = {
                    'applications' : applicationsList,
                    'active_tab' : app_name,
                    'analysis_type' : analysis_type,
                    'bookmark' : json.dumps(requestData), 
                    'title' : title,
                    'help' : help,
                    }
        #include user's data
        if user_data:
            dataDict.update(user_data)

        return render_to_response(template, 
                  dataDict,
                  context_instance=RequestContext(request))

@login_required
def analysis_extras(request, analysis_type, function_name, app_name):
    if request.method == 'GET':
        requestData = request.GET
    else:
        requestData = request.POST
    
    module = 'analysis.{0}'.format(analysis_type)
    try:
        called_function = getattr(__import__(module, fromlist=[module]), function_name)
    except ImportError, e:
        logger_analysis.exception(e)
        return HttpResponseNotFound(json.dumps({ 'errorMessage' : 'Analysis function {0} for {1} analysis was not found'.format(function_name, analysis_type) }))
    else:   
        return called_function(request = request, requestData = requestData, app_name = app_name )
 
@login_required
def analysis_function(request, analysis_type, app_name):
    """This function call the right render_to_response depending on the analysis
    type argument
    """
    if request.method == 'GET':
        requestData = request.GET
    else:
        requestData = request.POST
    
    module = 'analysis.{0}'.format(analysis_type)
    try:
        mod = __import__(module, fromlist=[module])
    except ImportError, e:
        logger_analysis.exception(e)
        return render_to_response('analysis/error.html', 
                  { 'errorMessage' : 'Analysis function: {0} was not found!'.format(requestData['analysis_type']) },
                  context_instance=RequestContext(request)) 
    
    else:   
        user_data = mod.analyse(request = request, requestData = requestData, app_name = app_name)
        if 'template' in user_data:
            template = user_data['template']
        else:
            template = 'analysis/{0}/analyse.html'.format(analysis_type)
            template_dir = os.path.join(settings.TEMPLATE_DIRS[0], template)
            if not os.path.isfile(template_dir):
                #choose the default template
                template = 'analysis/default_analyse.html'
                #in case of default template  return str representation of data
                if not 'str' in user_data:
                 user_data['str'] = pformat(user_data)
            
            
        dataDict = {}
        dataDict.update(user_data)
        return render_to_response(template, 
                  dataDict,
                  context_instance=RequestContext(request))
    
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
            querylist.append(makeQuery('application__id__exact', request.GET['appVersions'].split(','), Q.OR))
        if request.GET['Options']:
            querylist.append(makeQuery('options__id__exact',request.GET['Options'].split(','), Q.OR))
        if request.GET['SetupProjects']:
            querylist.append(makeQuery('setup_project__id__exact',request.GET['SetupProjects'].split(','), Q.OR))
        
        final_query = Q()
        for q in querylist:
           final_query &= q 
        
        jobDesTemp = JobDescription.objects.filter(final_query)
        Qplatform = None
        if request.GET['platforms']:
           Qplatform = makeQuery('cmtconfig__id__exact', request.GET['platforms'].split(','), Q.OR)
        
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
    if request.method == 'GET':
        requestData = request.GET
    elif request.method == 'POST':
        requestData = request.POST
    else:
        return HttpResponse(json.dumps({'error' : True, 'errorMessage' : 'unsupported http method, only GET or POST are supported'}))
    
    if not 'job_id' in requestData:
        return HttpResponseNotFound()
    
    myJob = JobDescription.objects.get(pk=requestData['job_id'])

    platforms = list(Requested_platform.objects.filter(jobdescription__exact=myJob).values_list('cmtconfig__cmtconfig', flat=True).distinct().order_by('cmtconfig__cmtconfig'))
            
    handlers = map(str,JobHandler.objects.filter(jobDescription__exact=myJob).values_list('handler__name', flat=True).distinct().order_by('handler__name'))
    
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
    if 'cloneRequest' or 'editRequest' in requestData:
        dataDict['versionsAll'] = list(Application.objects.filter(appName__exact=myJob.application.appName).values_list('appVersion', flat=True).distinct())
        dataDict['optionsAll'] = list(Options.objects.all().values_list('content', flat=True).distinct())
        dataDict['optionsDAll'] = list(Options.objects.all().values_list('description', flat=True).distinct())
        dataDict['setupAll'] = list(SetupProject.objects.all().values_list('content', flat=True).distinct())
        dataDict['setupDAll'] = list(SetupProject.objects.all().values_list('description', flat=True).distinct())
    
    #check if the jobdescription exists in runned jobs so the user can edit or not some attributes
    runned_jobs = Job.objects.filter(jobDescription__pk=requestData['job_id']).count()
    if runned_jobs > 0:
        dataDict['runned_job'] = True
    else:
        dataDict['runned_job'] = False
        
                
    return HttpResponse(json.dumps(dataDict))
    
@login_required
def commitClone(request):
    """This view checks if a commit request from the user(add new job description/or edit an existing one) is valid.
    if it's valid it updates/creates the old/new job description, which means add/edit handler,requested platforms, options etc"""
    if request.method == 'GET':
        requestData = request.GET
    elif request.method == 'POST':
        requestData = request.POST
    else:
        return HttpResponse(json.dumps({'error' : True, 'errorMessage' : 'unsupported http request method, only GET or POST'}))
    
    optObj = Options.objects.filter(description__exact=requestData['optionsD'])
    if optObj.count() > 0:
        if not optObj[0].content == requestData['options']:
            return HttpResponse(json.dumps({ 'error' : True, 'errorMessage' : 'Using existing Options description with wrong corresponding content' , 
                             'content' : optObj[0].content, 'description' : optObj[0].description  }))
    
    optObjD = Options.objects.filter(content__exact=requestData['options'])
    if optObjD.count() > 0:
        if not optObjD[0].description == requestData['optionsD']:
            return HttpResponse(json.dumps({ 'error' : True, 'errorMessage' : 'Using existing Options content with wrong corresponding description' , 
                             'content' : optObjD[0].content, 'description' : optObjD[0].description  }))
    
    if not requestData['setupproject'] == "" and not requestData['setupprojectD'] == "":
        setupObj = SetupProject.objects.filter(description__exact=requestData['setupprojectD'])
        if setupObj.count() > 0:
            if not setupObj[0].content == requestData['setupproject']:
                return HttpResponse(json.dumps({ 'error' : True, 'errorMessage' : 'Using existing SetupProject description with wrong corresponding content' , 
                          'content' : setupObj[0].content, 'description' : setupObj[0].description  }))
        
        setupObjD = SetupProject.objects.filter(content__exact=requestData['setupproject'])
        if setupObjD.count() > 0:
            if not setupObjD[0].description == requestData['setupprojectD']:
                return HttpResponse(json.dumps({ 'error' : True, 'errorMessage' : 'Using existing SetupProject content with wrong corresponding description' , 
                             'content' : setupObjD[0].content, 'description' : setupObjD[0].description  }))
    
    if 'update' in requestData:
        myObj = JobDescription.objects.get(pk=requestData['id'])
        myObj.setup_project = None
        if requestData['setupproject'] != '' and requestData['setupprojectD'] != '':
            setupprojectTemp, created = SetupProject.objects.get_or_create(content=requestData['setupproject'], description=requestData['setupprojectD'])
            myObj.setup_project=setupprojectTemp
        
        
        optionsTemp, created = Options.objects.get_or_create(content=requestData['options'], description=requestData['optionsD'])
        appTemp, created = Application.objects.get_or_create(appName=requestData['application'], appVersion=requestData['version'])
        
        
        myObj.options = optionsTemp
        myObj.application = appTemp
        
        myObj.save()
                  
        JobHandler.objects.filter(jobDescription__pk=requestData['id']).delete()
        for handler_name in requestData['handlers'].split(','):
            handlerTemp = Handler.objects.get(name=handler_name)
            jobHandlerTemp, created = JobHandler.objects.get_or_create(jobDescription=myObj, handler=handlerTemp)
        
        Requested_platform.objects.filter(jobdescription__pk=requestData['id']).delete()
        for platform_name in requestData['platforms'].split(','):
            platformTemp = Platform.objects.get(cmtconfig=platform_name)
            requestedPlatfromTemp, created = Requested_platform.objects.get_or_create(jobdescription=myObj, cmtconfig=platformTemp)
        
        return HttpResponse(json.dumps({ 'error' : False, 'updated' : True, 'job_id' : myObj.id }))
    
    
    if requestData['setupproject'] != '' and requestData['setupprojectD'] != '':
        myjob_id = JobDescription.objects.filter(application__appName__exact=requestData['application'], 
                                                 application__appVersion__exact=requestData['version'],
                                                 options__content__exact=requestData['options'],
                                                 options__description__exact=requestData['optionsD'],
                                                 setup_project__content__exact=requestData['setupproject'],
                                                 setup_project__description__exact=requestData['setupprojectD']
                                                 )
    else:
        myjob_id = JobDescription.objects.filter(application__appName__exact=requestData['application'], 
                                                 application__appVersion__exact=requestData['version'],
                                                 options__content__exact=requestData['options'],
                                                 options__description__exact=requestData['optionsD'],
                                                 )
    if myjob_id.count() > 0:
        return HttpResponse(json.dumps({ 'error': False , 'exists': True }))
    else:
        if requestData['setupproject'] != '' and requestData['setupprojectD'] != '':
            setupprojectTemp, created = SetupProject.objects.get_or_create(content=requestData['setupproject'], description=requestData['setupprojectD'])
        
        optionsTemp, created = Options.objects.get_or_create(content=requestData['options'], description=requestData['optionsD'])
        appTemp, created = Application.objects.get_or_create(appName=requestData['application'], appVersion=requestData['version'])
        
        if requestData['setupproject'] != '' and requestData['setupprojectD'] != '':
            myObj, created = JobDescription.objects.get_or_create(application=appTemp, options=optionsTemp, setup_project=setupprojectTemp)
        else:
            myObj, created = JobDescription.objects.get_or_create(application=appTemp, options=optionsTemp)           
        
        for handler_name in requestData['handlers'].split(','):
            handlerTemp = Handler.objects.get(name=handler_name)
            jobHandlerTemp, created = JobHandler.objects.get_or_create(jobDescription=myObj, handler=handlerTemp)
        
        for platform_name in requestData['platforms'].split(','):
            platformTemp = Platform.objects.get(cmtconfig=platform_name)
            requestedPlatfromTemp, created = Requested_platform.objects.get_or_create(jobdescription=myObj, cmtconfig=platformTemp)
        
        return HttpResponse(json.dumps({'error' : False,  'exists' : False, 'job_id' : myObj.id }))
@login_required
def editPanel(request):
    """Serves the information is needed for the editing handlers/platforms dialog, just sends back
    all available handlers and platforms"""
    if request.method == 'GET':
        requestData = request.GET
    elif request.method == 'POST':
        requestData = request.POST
    else:
        return HttpResponse(json.dumps({'error' : True, 'errorMessage' : 'unsupported http request method, only GET or POST'}))
    
    all_attributes = []
    if requestData['service'] == 'platforms':
        #convert valueslistqueryset(result of django query) to list because it is not json serializable  
        all_attributes = list(Platform.objects.values_list('cmtconfig', flat=True).distinct().order_by('cmtconfig'))
        
    if requestData['service'] == 'handlers':     
        all_attributes = list(Handler.objects.values_list('name', flat=True).distinct().order_by('name'))

    return HttpResponse(json.dumps({ 'available' : all_attributes }))

#@login_required no need to protect this one
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
    except Exception, e:
        logger.exception(e)
        return HttpResponse("<h3>Not valid integer primary key was given lol.</h3>")
    
    try:
        myJobDes = JobDescription.objects.get(pk=request.GET['pk'])
    except Exception, e:
        return HttpResponse("<h3>Not such job description id</h3>")
    
    application = myJobDes.application.appName
    version = myJobDes.application.appVersion
    try:
        setup_project =  myJobDes.setup_project.content
    except Exception:
        setup_project = ''
    options = myJobDes.options.content
    platforms = Requested_platform.objects.filter(jobdescription__exact=myJobDes).values_list('cmtconfig__cmtconfig', flat=True).distinct()       
    handlers = JobHandler.objects.filter(jobDescription__exact=myJobDes).values_list('handler__name', flat=True).distinct()
    
    script = '#!/bin/bash\n'
    script += '#this script produced by: {0} machine\n\n'.format(settings.HOSTNAME)
    script += '#attention, in order to use this script you must make sure you have\n'
    script += '#runned LbLogin and lhcb-proxy-init to get a proxy\n'
    script += 'proxy=`lhcb-proxy-info`\nOUT=$?\nif [ ! $OUT -eq 0 ];then\n'
    script += '   echo "lhcb-proxy invalid, please make sure you used the command: lhcb-proxy-init, aborting..."\n'
    script += '   exit 1\nfi\n\n'
    script += '\n#job description id\n'
    script += 'JOB_DESCRIPTION_ID={0}\n\n'.format(myJobDes.pk)
    script += 'HANDLERS="'+','.join(handlers)+'"\n'
    script += '#PLATFORMS="'+','.join(platforms)+'"\n\n'
    script += '. SetupProject.sh {0} {1} {2}\n\n'.format(application, version, setup_project)
    script += 'START=`date +"%Y-%m-%d,%T"`\n'
    script += 'gaudirun.py {0} 2>&1 > run.log\n'.format(options)
    script += 'END=`date +"%Y-%m-%d,%T"`\n\n'
    script += '#also setup the enviroment to use LHCbDirac StorageElement to send the result to the database\n'
    script += '. SetupProject.sh LHCbDirac\n\n'
    script += '#the next command, downloads the LHCbPRHandlers, unzips the file, removes the zip file(overrides previous folder/files, if any)\n'
    script += "python -c \"import os,urllib,zipfile;urllib.urlretrieve('http://lhcbproject.web.cern.ch/lhcbproject/GIT/dist/LHCbPRHandlers/LHCbPRHandlers.zip','LHCbPRHandlers.zip');unzipper=zipfile.ZipFile('LHCbPRHandlers.zip');unzipper.extractall();os.remove('LHCbPRHandlers.zip')\"\n\n"
    script += '#the collectRunResults has by default the -a argument which automatically sends the data\n'
    script += '#to the database, if you want to do it manually remove -a argument and uncomment the sendToDB script\n'
    script += 'python LHCbPRHandlers/collectRunResults.py -s ${START} -e ${END} -p `hostname` -c ${CMTCONFIG} -j ${JOB_DESCRIPTION_ID} -l ${HANDLERS} -a\n'
    script += '#python LHCbPRHandlers/sendToDB.py -s name_of_zip'
    
    return HttpResponse(script, mimetype="text/plain")

@login_required
def getFiles(request, filename):
    django_file = ""
    try:
        file = open(filename)
        django_file = File(file) 
    except IOError:
        print "File: ", filename, "can not be opened."

    t = loader.get_template('myapp/template.html')
    c = Context({'file':django_file})
    return HttpResponse(t.render(c)) 

@csrf_exempt
def get_content(request):
    """Gets an option description or setupproject description and returns the content"""
    if request.method == 'GET':
        requestData = request.GET
    elif request.method == 'POST':
        requestData = request.POST
    else:
        return HttpResponse(json.dumps({ 'error' : True, 'errorMessage' : 'unsupported method, supported GET,POST' }))
    
    
    if 'optionsD' in requestData:
        try:
            myopt = Options.objects.get(description=requestData['optionsD'])
            return HttpResponse( json.dumps( { 'error' : False, 'content' : myopt.content } ) )
        except Exception, e:
            return HttpResponse( json.dumps( { 'error' : True, 'errorMessage' : 'Such options description do not exist' } ) )
    elif 'setupprojectD' in requestData:
        try:
            myset = SetupProject.objects.get(description=requestData['setupprojectD'])
            return HttpResponse( json.dumps( { 'error' : False, 'content' : myset.content } ) )
        except Exception, e:
            return HttpResponse( json.dumps( { 'error' : True, 'errorMessage' : 'Such setupproject description do not exist' } ) )
    else:
        return HttpResponse( json.dumps( { 'error' : True, 'errorMessage' : 'You must at least provide an options value or setupproject value in your request to the content.' } ) )
    
#@login_required
@csrf_exempt
def new_job_description(request):
    """This view checks if a commit request from the user(add new job description/or edit an existing one) is valid.
    if it's valid it updates/creates the old/new job description, which means add/edit handler,requested platforms, options etc"""
    
    if request.method == 'GET':
        requestData = request.GET
    elif request.method == 'POST':
        requestData = request.POST
    else:
        return HttpResponse(json.dumps({ 'error' : True, 'errorMessage' : 'unsupported method, supported GET,POST' }))
    
    #return HttpResponse(request.POST['application'])
    
    if not set(['application', 'version', 'optionsD']).issubset(requestData):
        return HttpResponse(json.dumps({ 'error' : True, 'errorMessage' : 'Your HTTP request must contain at least an application,version and optionsD(options_description)' }))
    
    dataDict = {}
    dataDict['application'] = requestData['application']
    dataDict['version'] = requestData['version']
    dataDict['options_description'] = requestData['optionsD']
    if 'options' in requestData:
        dataDict['options_content'] = requestData['options']
    if 'setupprojectD' in requestData:
        dataDict['setupproject_description'] = requestData['setupprojectD']
    if 'setupproject' in requestData:
        dataDict['setupproject_content'] = requestData['setupproject']
    if 'handlers' in requestData:
        dataDict['handlers'] = requestData['handlers']
    if 'platforms' in requestData:
        dataDict['platforms'] = requestData['platforms']
    
    try:
        result = jobdescription(dataDict)
    except Exception, e:
         #TODO look up for the logger cause they do not work from times to times damn 
         logger.exception(e)
         return HttpResponse('{0} {1}'.format(Exception, e))
         #return HttpResponse( json.dumps({ 'error' : True, 'errorMessage': '{0}'.format(e) }) )
    else:
        return HttpResponse(json.dumps(result))
