from django.contrib import admin
from lhcbPR.models import Application, Options, SetupProject, JobDescription, Platform, Requested_platform, Job, Handler, JobHandler, JobAttribute, JobResults, ResultString, ResultFloat, ResultInt, ResultFile, HandlerResult, AddedResults

admin.site.register(Options)
admin.site.register(SetupProject)
admin.site.register(Platform)
admin.site.register(Handler)
admin.site.register(AddedResults)

#no need for the moment to appear in admin panel
#admin.site.register(ResultString)
#admin.site.register(ResultFloat)
#admin.site.register(ResultInt)
#admin.site.register(ResultFile)

#possible actions performed on job objects
def flag_unsuccessful(modeladmin, request, queryset):
    queryset.update(success = False)
flag_unsuccessful.short_description = "Flag selected jobs as unsuccessful"

def flag_successful(modeladmin, request, queryset):
    queryset.update(success = True)
flag_successful.short_description = "Flag selected jobs as successful"

class JobAdmin(admin.ModelAdmin):
    #fields = ( 'time_start', 'jobDescription')
    date_hierarchy = 'time_start'
    search_fields = ['jobDescription__id', 'host__hostname',
                      'platform__cmtconfig', 'time_start', 'success']
    actions = [ flag_unsuccessful,  flag_successful ]

admin.site.register(Job, JobAdmin)

class ApplicationAdmin(admin.ModelAdmin):
    search_fields = ['appName', 'appVersion']
    
admin.site.register(Application, ApplicationAdmin)

class JobDescriptionAdmin(admin.ModelAdmin):
    search_fields = ['application__appName', 'application__appVersion',
                      'options__description']
    
admin.site.register(JobDescription, JobDescriptionAdmin)

class Requested_PlatformAdmin(admin.ModelAdmin):
    search_fields = [ 'jobdescription__id', 'cmtconfig__cmtconfig' ]

admin.site.register(Requested_platform, Requested_PlatformAdmin)

class JobHandlerAdmin(admin.ModelAdmin):
    search_fields = [ 'jobDescription__id', 'handler__name' ]
    
admin.site.register(JobHandler, JobHandlerAdmin)

class HandlerResultAdmin(admin.ModelAdmin):
    search_fields = ['job__id', 'handler__name', 'success']
     
admin.site.register(HandlerResult, HandlerResultAdmin)

class JobAttributeAdmin(admin.ModelAdmin):
    search_fields = ['name', 'type']

admin.site.register(JobAttribute, JobAttributeAdmin)

class JobResultsAdmin(admin.ModelAdmin):
    search_fields = ['job__id', 'jobAttribute__id']

admin.site.register(JobResults, JobResultsAdmin)