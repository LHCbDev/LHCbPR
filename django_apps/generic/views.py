# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt    
from django.template import RequestContext
from generic.models import App, AppDes, Attr, Blob, AppAtr
import json, subprocess, sys, configs

def index(request):
    applications = App.objects.values('appName').distinct('appName')
    
    applicationsList = []
    for dict in applications:  
        applicationsList.append(dict['appName'])

    return render_to_response('generic/genericPlot.html',
                    {'applications' : applicationsList}, 
                  context_instance=RequestContext(request))
    
def choose(request):
    if request.method == 'POST':      
        cDict = {}
        currentApp = App.objects.get(appName__exact=request.POST['application'],appVersion__exact=request.POST['AppVersion'])
        currentAppDes = AppDes.objects.get(app__exact=currentApp, options__exact=request.POST['Options'])
        current_histos = Blob.objects.all().filter(appDes__exact=currentAppDes)
        
        attributesCurrent = AppAtr.objects.all().filter(appDes__exact=currentAppDes)
        current = {}
        for atr in attributesCurrent:
            current[atr.attr.name]=atr.value
            
        current['gaussVersion'] = currentApp.appVersion
        
        for cur in current_histos:
            cDict[cur.name]=cur.data
            
            
            
        rDict = {}
        referenceApp = App.objects.get(appName__exact=request.POST['applicationREF'],appVersion__exact=request.POST['AppVersionREF'])
        referenceAppDes = AppDes.objects.get(app__exact=referenceApp, options__exact=request.POST['OptionsREF'])
        reference_histos = Blob.objects.all().filter(appDes__exact=referenceAppDes)
         
        attributesReference = AppAtr.objects.all().filter(appDes__exact=referenceAppDes)
        reference = {}
        for atr in attributesReference:
            reference[atr.attr.name]=atr.value
            
        reference['gaussVersion'] = referenceApp.appVersion
           
        for ref in reference_histos:
            rDict[ref.name]=ref.data
            
        gloDict = {}
            
        gloDict['current']= cDict
        gloDict['reference'] = rDict
         
        outputfile = configs.project_work_path+'something.json'   
        f = open(outputfile,'wb')
        f.write(json.dumps(gloDict))
        f.close()
        pythonROOT = configs.project_work_path+'pythonROOT'
        genplotpy = configs.project_work_path+'genplot.py'
        
        
        subprocess.call(['bash', pythonROOT, genplotpy, '-f', outputfile])
                
        return render_to_response('generic/genericPlotResults.html',
                      {'current' : current , 'reference' : reference}, 
                      context_instance=RequestContext(request))

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
