import os, re, socket, subprocess, logging
import tools.socket_service as service
from  cPickle import dump, load, loads
from django.db.models import Q
from django.conf import settings
from django.db import transaction
from lhcbPR.models import  JobDescription, Requested_platform, Platform, Application, Options, SetupProject, Handler, JobHandler
#extra functions which are used in lhcbPR app, i moved them here in order
#to keep the views clean

#a custom dictionary setup the environment for using the afs ROOT
ROOTdict = os.environ.copy()
ROOTdict['LD_LIBRARY_PATH'] = '/afs/cern.ch/sw/lcg/app/releases/ROOT/5.32.02/x86_64-slc5-gcc43-opt/root/lib:/afs/cern.ch/sw/lcg/external/xrootd/3.1.0p2/x86_64-slc5-gcc43-opt/lib64:/afs/cern.ch/sw/lcg/external/gcc/4.3.5/x86_64-slc5/lib64:/afs/cern.ch/lhcb/software/releases/COMPAT/COMPAT_v1r10/CompatSys/x86_64-slc5-gcc43-opt/lib:/afs/cern.ch/sw/lcg/external/Python/2.6.5p2/x86_64-slc5-gcc43-opt/lib'
ROOTdict['PATH'] = '/afs/cern.ch/sw/lcg/app/releases/ROOT/5.32.02/x86_64-slc5-gcc43-opt/root/bin:/afs/cern.ch/sw/lcg/external/xrootd/3.1.0p2/x86_64-slc5-gcc43-opt/bin:/afs/cern.ch/sw/lcg/external/Python/2.6.5p2/x86_64-slc5-gcc43-opt/bin:/afs/cern.ch/sw/lcg/external/gccxml/0.9.0_20110825/x86_64-slc5-gcc43-opt/bin:/afs/cern.ch/sw/lcg/external/gcc/4.3.5/x86_64-slc5/bin:/afs/cern.ch/lhcb/software/releases/COMPAT/COMPAT_v1r10/CompatSys/x86_64-slc5-gcc43-opt/bin:/afs/cern.ch/sw/contrib/CMT/v1r20p20090520/Linux-x86_64:/afs/cern.ch/lhcb/software/releases/LBSCRIPTS/LBSCRIPTS_v6r7p4/InstallArea/scripts:/afs/cern.ch/lhcb/bin:/usr/sue/bin:/usr/local/bin:/usr/bin:/bin:/usr/bin/X11:/usr/kerberos/bin:/usr/X11R6/bin'
ROOTdict['PYTHONPATH'] = '/afs/cern.ch/sw/lcg/app/releases/ROOT/5.32.02/x86_64-slc5-gcc43-opt/root/lib:/afs/cern.ch/lhcb/software/releases/LBSCRIPTS/LBSCRIPTS_v6r7p4/InstallArea/python'
ROOTdict['ROOTSYS'] = '/afs/cern.ch/sw/lcg/app/releases/ROOT/5.32.02/x86_64-slc5-gcc43-opt/root'

def combineStatements(StatementsDict, operator):
    """Takes a dictionary with statements, combines them depending on the
    given operator(AND,OR) and return a final query(query)"""
    query =  Q()
    for k,v in StatementsDict.iteritems():
        query.add(Q( **{ v : k }),operator)
    
    return query
     
def makeQuery(statement,arguments,operator):
    """Gets a list of different arguments and for each argument creates 
    a dictionary with the given statement
    example :
    argument : v43r0
    statement: application__appVersion__exact"""
    dataDict = {}
    
    for arg in arguments:
        dataDict[arg] = statement
        
    return combineStatements(dataDict, operator)

def handle_uploaded_file(f):
    path_to_save = os.path.join(settings.PROJECT_PATH, 'static/uploaded/'+f.name)
    with open( path_to_save , 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            
#change version (make decimal to str) with map function 
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], map(str,row)))
        for row in cursor.fetchall()
    ]

def getSplitted(version):
    """Takes a version and tranforms it like v41r0 ----> ['v', 41, 'r', '0']"""
    split_regex = re.compile('\d+|[^\d\s]+')
    splittedElement = []
    for v in re.findall(split_regex, version):
        if v.isdigit():
            splittedElement.append(int(v))
        else:
            splittedElement.append(v)
       
    return splittedElement

#return simple input text html elements
#(one for each list/tuple in the list parameter)
def formBuilder(listTexts):
    help = """
    <pre>
Attention:
    default form builder must take as an input a list at this format:
    my_text_elements_list = [
        #id of html element, text of the label, optional default value for the text input
        ('text_id', 'label content', 'default text value')
                            ]
    the items in the list can be either lists or tuple
    each of them should contain at least 2(id, label) values or 3(id,label,value-optional)
    </pre>
    """
    html_texts = []
    try:
        for text in listTexts:
            if len(text) == 2:
                id , label = text
                html_texts.append('<label>{1} </label><input id="{0}" type="text" value="" />'.format(id, label))
            elif len(text) == 3:
                id , label, value = text
                html_texts.append('<label>{1} </label><input id="{0}" type="text" value="{2}" />'.format(id, label, value))
            else:
                return help
    except Exception:
        return help
    else:
        return '<br>'.join(html_texts)
    
@transaction.commit_on_success
def jobdescription(dataDict, update=False):
    request = None
    """This view checks if a commit request from the user(add new job description/or edit an existing one) is valid.
    if it's valid it updates/creates the old/new job description, which means add/edit handler,requested platforms, options etc"""
    
    
    optObj = Options.objects.filter(description__exact=dataDict['options_description'])
    if optObj.count() > 0:
        if 'options_content' in dataDict:
            if not optObj[0].content == dataDict['options_content']:
                raise Exception('Using existing Options description with wrong corresponding content')
        else:
            dataDict['options_content'] = optObj[0].content
        
    
    if not 'options_content' in dataDict:
        raise Exception('No options content was provided, and the options description you provided did not match with any existing options')
    
    optObjD = Options.objects.filter(content__exact=dataDict['options_content'])
    if optObjD.count() > 0:
        if not optObjD[0].description == dataDict['options_description']:
            raise Exception('Using existing Options content with wrong corresponding description')
    
    if 'setupproject_description' in dataDict:
        setupObj = SetupProject.objects.filter(description__exact=dataDict['setupproject_description'])
        if setupObj.count() > 0:
            if 'setupproject_content' in dataDict:
                if not setupObj[0].content == dataDict['setupproject_content']:
                    raise Exception('Using existing SetupProject description with wrong corresponding content')
            else:
                dataDict['setupproject_content'] = setupObj[0].content
        else:
            if not 'setupproject_content' in dataDict:
                raise Exception('You did not provide a setupproject content, and the setupproject description you provided did not match with any existing setupprojects')
    
    if 'setupproject_content' in dataDict and 'setupproject_description' in dataDict:   
        setupObjD = SetupProject.objects.filter(content__exact=dataDict['setupproject_content'])
        if setupObjD.count() > 0:
            if not setupObjD[0].description == dataDict['setupproject_description']:
                raise Exception('Using existing SetupProject content with wrong corresponding description')
    
    #if the request is an edit request
    if update:
        myObj = JobDescription.objects.get(pk=dataDict['id'])
        myObj.setup_project = None
        if 'setupproject_content' in dataDict and 'setupproject_description' in dataDict:
            setupprojectTemp, created = SetupProject.objects.get_or_create(content=dataDict['setupproject_content'], description=dataDict['setupproject_description'])
            myObj.setup_project=setupprojectTemp
        
        
        optionsTemp, created = Options.objects.get_or_create(content=dataDict['options_content'], description=dataDict['options_description'])
        appTemp, created = Application.objects.get_or_create(appName=dataDict['application'], appVersion=dataDict['version'])
        
        
        myObj.options = optionsTemp
        myObj.application = appTemp
        
        myObj.save()
        
        if 'handlers' in dataDict:
            JobHandler.objects.filter(jobDescription__pk=dataDict['id']).delete()
            
            for handler_name in dataDict['handlers'].split(','):
                handlerTemp = Handler.objects.get(name=handler_name)
                jobHandlerTemp, created = JobHandler.objects.get_or_create(jobDescription=myObj, handler=handlerTemp)
        
        if 'platforms' in dataDict:
            Requested_platform.objects.filter(jobdescription__pk=dataDict['id']).delete()
            
            for platform_name in dataDict['platforms'].split(','):
                platformTemp = Platform.objects.get(cmtconfig=platform_name)
                requestedPlatfromTemp, created = Requested_platform.objects.get_or_create(jobdescription=myObj, cmtconfig=platformTemp)
            
        return { 'error' : False, 'updated' : True, 'job_id' : myObj.id }
    
    
    if 'setupproject_content' in dataDict and 'setupproject_description' in dataDict:
        myjob_id = JobDescription.objects.filter(application__appName__exact=dataDict['application'], 
                                                 application__appVersion__exact=dataDict['version'],
                                                 options__content__exact=dataDict['options_content'],
                                                 options__description__exact=dataDict['options_description'],
                                                 setup_project__content__exact=dataDict['setupproject_content'],
                                                 setup_project__description__exact=dataDict['setupproject_description']
                                                 )
    else:
        myjob_id = JobDescription.objects.filter(application__appName__exact=dataDict['application'], 
                                                 application__appVersion__exact=dataDict['version'],
                                                 options__content__exact=dataDict['options_content'],
                                                 options__description__exact=dataDict['options_description'],
                                                 )
    if myjob_id.count() > 0:
        return { 'error': False , 'exists': True , 'jobdescription_id' : myjob_id[0].pk}
    else:   
        optionsTemp, created = Options.objects.get_or_create(content=dataDict['options_content'], description=dataDict['options_description'])
        appTemp, created = Application.objects.get_or_create(appName=dataDict['application'], appVersion=dataDict['version'])
        
        if 'setupproject_content' in dataDict and 'setupproject_description' in dataDict:
            setupprojectTemp, created = SetupProject.objects.get_or_create(content=dataDict['setupproject_content'], description=dataDict['setupproject_description'])
            myObj, created = JobDescription.objects.get_or_create(application=appTemp, options=optionsTemp, setup_project=setupprojectTemp)
        else:
            myObj, created = JobDescription.objects.get_or_create(application=appTemp, options=optionsTemp)           
        
        if 'handlers' in dataDict:
            for handler_name in dataDict['handlers'].split(','):
                handlerTemp = Handler.objects.get(name=handler_name)
                jobHandlerTemp, created = JobHandler.objects.get_or_create(jobDescription=myObj, handler=handlerTemp)
        
        if 'platforms' in dataDict:            
            for platform_name in dataDict['platforms'].split(','):
                platformTemp = Platform.objects.get(cmtconfig=platform_name)
                requestedPlatfromTemp, created = Requested_platform.objects.get_or_create(jobdescription=myObj, cmtconfig=platformTemp)
        
        return {'error' : False,  'exists' : False, 'jobdescription_id' : myObj.id }

#socket ROOT service
class remoteService(object):
    def __init__(self):
        self.connection = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
    def connect(self,port=4321):
        try:
            self.connection.connect(("localhost", port))
        except Exception:
            return False
        else:
            return True
    def send(self, data):
        service.send(self.connection, data)
    def recv(self):
        return service.recv(self.connection)
    def finish(self):
        self.connection.close()

#subProcess ROOT service
class subService(object):
    def __init__(self):
        self.connection = subprocess.Popen(['python', os.path.join(settings.PROJECT_PATH,'tools/ROOT_service.py'), 
                                            'subprocess'], 
                 env = ROOTdict , stdin = subprocess.PIPE, stdout = subprocess.PIPE)
    def connect(self):
        return True
    def send(self, data):
        dump(data,self.connection.stdin,2)
    def recv(self):
        return loads(self.connection.communicate()[0])
    def finish(self):
        pass
