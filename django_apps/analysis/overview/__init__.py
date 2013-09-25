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
   request  = kwargs['requestData']
   jobs = []
   try:
      jobs = request['jobs'].split(',')
   except KeyError:
      jobs = []

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

   dataDict = {
         'atrs'      : json.dumps(atrs),
         'jobs'      : jobs,
         'atrGroups' : atr_groups,
         'groups'    : json.dumps(dict((v,k) for k, v in groups.iteritems())),
         'types'     : json.dumps(dict((v,k) for k, v in types.iteritems()))
   }
      
   return dataDict

def analyse(**kwargs):
   requestData   = kwargs['requestData']
   app_name      = kwargs['app_name']

   versions  = requestData['versions'].split(',')
   options   = requestData['options'].split(',')
   atr_group = requestData['grps']
   min_value = requestData['min']
   sorting   = requestData['sort']
   logscale  = requestData['log']

   axis = "unknown unit"

   jobs = []
   try:
      jobs = requestData['jobs'].split(",")
   except KeyError:
      jobs = []

   if jobs[0] == "":
      if versions[0] == "" and options[0] == "":
         raise Http404
      else:
         # Get SQL query
         query_jobs = get_jobs_query(requestData)
         #print "Query jobs in overview: ", query_jobs
    
         cursor = connection.cursor()
         cursor.execute(query_jobs)
         cursor_description = cursor.description
         jobs = [j[0] for j in cursor.fetchall()]

   query_tree_info = get_tree_query(jobs, atr_group)
   #print "Query tree in overview: ", query_tree_info
    
   cursor2 = connection.cursor()
   cursor2.execute(query_tree_info)
   cursor_description2 = cursor2.description

   groups = GroupDict()

   result = cursor2.fetchone()
   while not result == None:
      group = tuple(result[:-8])
      if result[-6] != None:
         axis  = result[-8]
      groups[group].append(tuple(result[-7:]))
      result = cursor2.fetchone()

   trends = []
   for g,values in groups.iteritems():
      datatable = []
      entry_avg = {}
      entry_sdv = {}
      parents   = {}
      events    = {}
      ids       = {}

      for res in values:
         if '_parent' in res[-7]:
            attr = re.sub('_parent$','',res[-7])
            parents[attr] = res[-2]
         elif '_count' in res[-7]:
            attr = re.sub('_count$','',res[-7])
            events[attr] = res[-3]
         elif '_id' in res[-7]:
            attr = re.sub('_id$','',res[-7])
            ids[attr] = res[-1]
         elif not res[-6] == None:
            entry_avg[res[-7]] = res[-6]
            entry_sdv[res[-7]] = res[-5]

      try:
         db_temp = []
         for k in entry_avg.keys():
             # Bug occurs with this key, probably import to DB failed
             # values (id) and others already in DB missing! 
             if k == "Hlt2CharmHadD2HHHKsDD":
                continue
             db_temp.append([ \
               '{0}'.format(k), \
               float(entry_avg[k]), \
               float(entry_avg[k]+entry_sdv[k]), \
               float(entry_avg[k]-entry_sdv[k]), \
               'Id: {0:03d}\nAverage: {1}, Stddev.: +-{2}\nEvents: {3}\nParent: {4}'.format(ids[k], entry_avg[k], entry_sdv[k], events[k], parents[k])
            ])
         datatable = db_temp
         sort_column = 4
      except KeyError:
         for k in entry_avg.keys():
            datatable.append([ \
               '{0}'.format(k), \
               float(entry_avg[k]), \
               float(entry_avg[k]+entry_sdv[k]), \
               float(entry_avg[k]-entry_sdv[k]), \
               'Average: {0}\nStddev.: +-{1}'.format(entry_avg[k], entry_sdv[k])
            ])
         sort_column = 0
         if sorting == "true":
            sort_column = 1

      dataDict = {}
      dataDict['application']  = app_name,
      dataDict['description']  = dict(zip([col[0] for col in cursor2.description[:-7]], g))
      dataDict['platform']     = dataDict['description']['PLATFORM']
      dataDict['datatable']    = datatable
      dataDict['min']          = min_value
      dataDict['sort']         = sort_column
      dataDict['log']          = logscale
      dataDict['axis']         = axis

      trends.append(dataDict)

   return { 'trends': json.dumps(trends) }

def isAvailableFor(app_name):
   return True
