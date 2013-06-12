import json, math, re
from django.db import connection
from django.http import HttpResponse 
from lhcbPR.models import Application, JobResults
from django.db.models import Q
from django.http import Http404

from tools.viewTools import getSplitted
import tools.socket_service as service
from query_builder import get_data_query, get_jobs_query, get_tree_query

class GroupDict(dict):
   def __getitem__(self, key):
      if key not in self:
         self[key] = []
      return dict.__getitem__(self, key)

def render(**kwargs):
   app_name = kwargs['app_name']
    
   apps = Application.objects.filter(appName__exact=app_name)
   if not apps:
      raise Http404     
    
   atrs_float = JobResults.objects.filter(
         job__jobDescription__application__appName=app_name,
         job__success=True
   ).filter(Q(jobAttribute__type='Float'))
   atrs_temp = atrs_float.values_list(
         'jobAttribute__id',
         'jobAttribute__name',
         'jobAttribute__type',
         'jobAttribute__group'
   ).distinct()
   atrs     = []
   groups   = {}
   types    = {}
   for i, at in enumerate(atrs_temp):
      #if type in types
      if not at[2] in types:
         types[at[2]] = len(types)
        
      #if group in groups
      if not at[3] in groups:
         groups[at[3]] = len(groups)
        
      atrs.append([ at[0], at[1], types[at[2]], groups[at[3]] ])
        
      atr_groups = []
      for k, v in groups.iteritems():
         if k != "":
            atr_groups.append([k, v])
   
   print atr_groups 
    
   dataDict = {
         'atrs'      : json.dumps(atrs),
         'atrGroups' : atr_groups,
         'groups'    : json.dumps(dict((v,k) for k, v in groups.iteritems())),
         'types'     : json.dumps(dict((v,k) for k, v in types.iteritems()))  
   }
      
   return dataDict

def analyse(**kwargs):
   requestData   = kwargs['requestData']
   app_name      = kwargs['app_name']

   #print requestData

   grps = requestData['grps'].split(',')
   print grps[0]
   if grps[0] == "":
      raise Http404     
    
   versions = requestData['versions'].split(',')
   if versions[0] == "":
      raise Http404     
    
   options = requestData['options'].split(',')
   if options[0] == "":
      raise Http404

   # Get SQL query
   query_jobs = get_jobs_query(requestData, app_name)
   #print "Query jobs in overview: ", query_jobs
    
   cursor = connection.cursor()
   cursor.execute(query_jobs)
   cursor_description = cursor.description
   jobs = cursor.fetchall()

   query_tree_info = get_tree_query(jobs)
   #print "Query tree in overview: ", query_tree_info
    
   #cursor1 = connection.cursor()
   #cursor1.execute(query_results)
   #cursor_description1 = cursor1.description
    
   cursor2 = connection.cursor()
   cursor2.execute(query_tree_info)
   cursor_description2 = cursor2.description

   groups = GroupDict()

   result = cursor2.fetchone()
   while not result == None:
      group = tuple(result[:-7])
      groups[group].append(tuple(result[-7:]))
      result = cursor2.fetchone()

   trends = []
   for g,values in groups.iteritems():
      datatable = []
      entry_avg = {}
      entry_sdv = {}
      parents   = {}
      levels    = {}
      events    = {}
      for res in values:
         if '_parent' in res[-7]:
            attr = re.sub('_parent$','',res[-7])
            parents[attr] = res[-2]
            if res[-2] == None:
                levels[attr] = 0
            elif res[-2] == 'EVENT_LOOP':
                levels[attr] = 1
            elif res[-2] in levels:
                levels[attr] = levels[res[-2]]+1
            else:
                levels[attr] = -1
         if '_count' in res[-7]:
            attr = re.sub('_count$','',res[-7])
            events[attr] = res[-3]
         if '_id' in res[-7]:
            continue
         elif not res[-6] == None:
            entry_avg[res[-7]] = res[-6]
            entry_sdv[res[-7]] = res[-5]

      for k in entry_avg.keys():
         datatable.append([ \
            '{0}'.format(k), \
            float(entry_avg[k]), \
            float(entry_avg[k]+entry_sdv[k]), \
            float(entry_avg[k]-entry_sdv[k]), \
            'Average: {0}, Stddev.: +-{1}\nEvents: {2}\nParent: {3}'.format(entry_avg[k], entry_sdv[k], events[k], parents[k])
         ])
        
      dataDict = {}
      dataDict['description']  = dict(zip([col[0] for col in cursor2.description[:-7]], g))
      dataDict['platform']     = dataDict['description']['PLATFORM']
      dataDict['datatable']    = datatable
        
      trends.append(dataDict)
        
   return { 'trends': json.dumps(trends) }

def isAvailableFor(app_name):
   return True
