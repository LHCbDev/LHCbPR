from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.core.files.base import ContentFile
from lhcbPR.models import ResultFile, Platform, Host, Job, JobResults, JobAttribute, ResultString, ResultInt, ResultFloat, ResultBinary, JobDescription, HandlerResult, Handler
from django.db import connection, transaction
import json, re, logging
#
##Old,should not be used , to be deleted
#

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):
        cursor = connection.cursor()
        #cursor.execute("SELECT j.jobdescription_id, h.hostname, plat.cmtconfig, count(*) as \"Number\", round(avg(rf.data), 2) as Average, round(stddev(rf.data), 2) as stddev, round(stddev(rf.data)/avg(rf.data) * 100, 2) as stddev_per FROM lhcbpr_job j, lhcbpr_jobresults r, lhcbpr_jobattribute att,lhcbpr_resultfloat rf, lhcbpr_host h, lhcbpr_platform plat where j.id = r.job_id AND plat.id = j.platform_id AND h.id = j.host_id AND r.jobattribute_id = att.id AND att.name = 'EVENT_LOOP' AND rf.jobresults_ptr_id = r.id AND j.jobdescription_id = 41 GROUP BY j.jobdescription_id, h.hostname, plat.cmtconfig;")
        #row = cursor.fetchall()
        #cursor.execute("select att.name from lhcbpr_job j, lhcbpr_jobresults r, lhcbpr_jobattribute att, lhcbpr_application apl, lhcbpr_jobdescription jobdes where j.id = r.job_id and jobdes.id = j.jobdescription_id and apl.id = jobdes.application_id and apl.appname = 'BRUNEL' and r.jobattribute_id = att.id group by att.name")
        #row = dictfetchall(cursor)
        cursor.execute("SELECT rf.data FROM lhcbpr_job j, lhcbpr_jobresults r, lhcbpr_jobattribute att, lhcbpr_resultfloat rf, lhcbpr_host h, lhcbpr_platform plat  WHERE j.id = r.job_id and plat.id = j.platform_id AND h.id = j.host_id AND r.jobattribute_id = att.id AND rf.jobresults_ptr_id = r.id AND att.name ='EVENT_LOOP'  AND ( j.jobdescription_id = '41' )  GROUP BY rf.data")
        row = cursor.fetchall()
        
        mylist = [ r[0] for r in row ]
        
        print mylist