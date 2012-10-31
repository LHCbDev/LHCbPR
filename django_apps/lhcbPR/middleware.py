from django.http import HttpResponse

class AjaxRedirect(object):
    def process_response(self, request, response):
        if request.is_ajax():
            if type(response) == HttpResponse and 'also_redirect' in response:
                response.status_code = 278
        return response