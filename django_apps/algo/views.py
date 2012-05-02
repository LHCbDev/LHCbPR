import urllib
import urllib2
from algo.models import Algorithm, History
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt    
from django.template import RequestContext
from xml.etree.ElementTree import ElementTree
import tools

def compare_page(request):
    total_algs = Algorithm.objects.all().count()
    algorithms = Algorithm.objects.all()[:40]
    return render_to_response('algo/algos.html', 
                              {'algorithms': algorithms}, 
                              context_instance=RequestContext(request))

def compare_page_results(request):
    if request.method == "POST":
        total_algs = Algorithm.objects.all().count()
        algorithms = Algorithm.objects.all()[:40]
    
        current = Algorithm.objects.get(alg__exact=request.POST['current'])
        reference = Algorithm.objects.get(alg__exact=request.POST['reference'])
        
        diffs = tools.fix_diffs(current,reference)
          
        history_exists = History.objects.all().filter(current__exact=current.alg).filter(reference__exact=reference.alg).count()
        
        if history_exists == 0:
            hist = History(current=current.alg,reference=reference.alg,body=tools.fix_history(current, reference, diffs))
            hist.save()
        
        return render_to_response('algo/algos_results.html', 
                {'algorithms': algorithms,'diffs' : diffs, 'current' : current ,'reference' : reference }, 
                context_instance=RequestContext(request))
    else:
        return HttpResponse("Nope")


def history(request):
    return HttpResponse(tools.generate_history())


#old examples-non in use right now
###########################################################################################################################3
#path_to_saving = '/afs/cern.ch/user/e/ekiagias/workspace/database_test/database_test/inputs/results.xml'

@csrf_exempt
def save_file(request):
     handle_uploaded_file(request.FILES['file'])
     add()
     return HttpResponse( 'File uploaded successful')

def handle_uploaded_file(f):
    destination = open(path_to_saving , 'wb+')

    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

def add():
    tree = ElementTree()
    tree.parse(path_to_saving)
    
    #empty dictonary which is going
    #to contain the input data
    input = {}
    
    for parent in tree.getiterator("alg"):
        input[parent.tag] = parent.attrib.get("name")
        for child in parent:
            input[child.tag] = child.text

        al=Algorithm(alg=input['alg'],avg_user=input['avg_user'],avg_clock=input['avg_clock'],
                 minn=input['min'],maxn=input['max'],count=input['count'],total=input['total'])
        al.save()
        input.clear()