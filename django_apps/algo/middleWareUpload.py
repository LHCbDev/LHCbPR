from django.utils import functional
from django.http import HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django import middleware

class UploadMiddleware(object):
#(request.path == reverse("/save_file/"))
    def process_request(self, request):
        if (request.method == 'POST') and (request.POST['security'] == 'give_csrf_token'):
            c = {}
            
            yo = ""
            c.update(csrf(request))
            return HttpResponse( "memory address " %  c )
    
#request.POST['csrfmiddlewaretoken'] , request.COOKIES['csrftoken']