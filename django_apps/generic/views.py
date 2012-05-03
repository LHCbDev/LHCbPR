# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt    
from django.template import RequestContext
from genplot.models import Job, Histos
import json, subprocess, sys, configs

def index(request):
    gaussVersions = Job.objects.values('gaussVersion').distinct('gaussVersion')
    
    gaussVersionsList = []
    for dict in gaussVersions:  
        gaussVersionsList.append(dict['gaussVersion'])

    return render_to_response('genplot/generatePlot.html',
                    {'gaussVersions' : gaussVersionsList}, 
                  context_instance=RequestContext(request))
    
def choose(request):
    if request.method == 'POST':
        cDict = {}
        current = Job.objects.get(gaussVersion__exact=request.POST['gaussVersion'],pythiaVersion__exact=request.POST['pythiaVersion'],eventType__exact=request.POST['eventType'])
        current_histos = Histos.objects.all().filter(job__exact=current)
            
        for cur in current_histos:
            cDict[cur.name]=cur.data
            
        rDict = {}
        reference = Job.objects.get(gaussVersion__exact=request.POST['gaussVersionREF'],pythiaVersion__exact=request.POST['pythiaVersionREF'],eventType__exact=request.POST['eventTypeREF'])
        reference_histos = Histos.objects.all().filter(job__exact=reference)
            
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
                
        return render_to_response('genplot/generatePlotResults.html',
                      {'current' : current , 'reference' : reference}, 
                      context_instance=RequestContext(request))

def handleService(request):
    if request.method == 'GET':
        if request.GET['service'] == 'pythia':
            querykey = request.GET['key']
            pythiaVersions = Job.objects.filter(gaussVersion__exact=querykey).values('pythiaVersion').distinct('pythiaVersion')
            
            pythiaVersionsList = []
            for dict in pythiaVersions:  
                pythiaVersionsList.append(dict['pythiaVersion'])
            
            myDict = {}
            myDict['pythiaVersions'] = pythiaVersionsList

            return HttpResponse(json.dumps(myDict))
        
        if request.GET['service'] == 'eventType':
            gaussVer = request.GET['gaussVersion'] 
            pythiaVer = request.GET['pythiaVersion']
            eventTypes = Job.objects.filter(gaussVersion__exact=gaussVer).filter(pythiaVersion__exact=pythiaVer).values('eventType').distinct('eventType')
            
            eventTypesList = []
            for dict in eventTypes:  
                eventTypesList.append(dict['eventType'])
            
            myDict = {}
            myDict['eventTypes'] = eventTypesList
            print myDict
            return HttpResponse(json.dumps(myDict))
