from django.conf import settings

def base_variables(request):
    return { 
            'ROOT_URL' : settings.ROOT_URL,
            }