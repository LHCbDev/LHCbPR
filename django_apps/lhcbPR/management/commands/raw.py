from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.core.files.base import ContentFile
from lhcbPR.models import ResultFile, Platform, Host, Job, JobResults, JobAttribute, ResultString, ResultInt, ResultFloat, ResultBinary, JobDescription, HandlerResult, Handler
from django.db import connection, transaction
import json, re, logging
import socket
import select
import sys
#import _pb2
import cPickle
from cPickle import dump
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



CRLF = '\r\n'
class MalformedMessage(Exception): pass
class ConnectionClosed(Exception): pass

def read_exactly(sock, buflen):
    data = ''
    while len(data) != buflen:
        data += sock.recv(buflen - len(data))
    return data

def peek(sock, buflen):
    data = sock.recv(buflen, socket.MSG_PEEK)
    return data

def socket_send(sock, obj):
    
    #myrfdata = _pb2.rfdata()
    #myrfdata.version = obj[0]
    #myrfdata.options = obj[1]
    #myrfdata.cmtconfig = obj[2]
    #myrfdata.data = obj[3]
    
    #data = myrfdata.SerializeToString()
    data = cPickle.dumps(obj)
    #data = ','.join(list(map(str, obj)))
    #data = json.encode(obj)
    size = len(data)
    #print str(size)+str(CRLF)+data
    #sock.sendall(str(size)+str(CRLF)+data)
    #sock.sendall('%i%s%s' % (size, CRLF, data))
    sock.sendall('{0}{1}{2}'.format(size, CRLF, data))

def socket_recv(sock):
    peekdata = peek(sock, 1024)
    if peekdata == '':
        raise ConnectionClosed
    sizepos = peekdata.find(CRLF)
    if sizepos == -1:
        raise MalformedMessage('Did not find CRLF in message %r' % peekdata)
    sizedata = read_exactly(sock, sizepos)
    read_exactly(sock, len(CRLF))
    try:
        size = int(sizedata)
    except ValueError:
        raise MalformedMessage(
            'size data %r could not be converted to an int' % sizedata)
    data = read_exactly(sock, size)
    return json.loads(data)

class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):
        cursor = connection.cursor()
        #cursor.execute("SELECT j.jobdescription_id, h.hostname, plat.cmtconfig, count(*) as \"Number\", round(avg(rf.data), 2) as Average, round(stddev(rf.data), 2) as stddev, round(stddev(rf.data)/avg(rf.data) * 100, 2) as stddev_per FROM lhcbpr_job j, lhcbpr_jobresults r, lhcbpr_jobattribute att,lhcbpr_resultfloat rf, lhcbpr_host h, lhcbpr_platform plat where j.id = r.job_id AND plat.id = j.platform_id AND h.id = j.host_id AND r.jobattribute_id = att.id AND att.name = 'EVENT_LOOP' AND rf.jobresults_ptr_id = r.id AND j.jobdescription_id = 41 GROUP BY j.jobdescription_id, h.hostname, plat.cmtconfig;")
        #row = cursor.fetchall()
        #cursor.execute("select att.name from lhcbpr_job j, lhcbpr_jobresults r, lhcbpr_jobattribute att, lhcbpr_application apl, lhcbpr_jobdescription jobdes where j.id = r.job_id and jobdes.id = j.jobdescription_id and apl.id = jobdes.application_id and apl.appname = 'BRUNEL' and r.jobattribute_id = att.id group by att.name")
        #row = dictfetchall(cursor)
        #cursor.execute("SELECT rf.data FROM lhcbpr_job j, lhcbpr_jobresults r, lhcbpr_jobattribute att, lhcbpr_resultfloat rf, lhcbpr_host h, lhcbpr_platform plat  WHERE j.id = r.job_id and plat.id = j.platform_id AND h.id = j.host_id AND r.jobattribute_id = att.id AND rf.jobresults_ptr_id = r.id AND att.name ='EVENT_LOOP'  AND ( j.jobdescription_id = '41' )  GROUP BY rf.data")
        
        cursor.execute("SELECT apl.appversion, opt.description , plat.cmtconfig, rf.data \
 FROM lhcbpr_job j, lhcbpr_jobresults r, lhcbpr_jobattribute att,\
 lhcbpr_resultfloat rf, lhcbpr_platform plat, lhcbpr_jobdescription jobdes, \
 lhcbpr_application apl, lhcbpr_options opt \
 WHERE j.id = r.job_id \
 AND j.jobdescription_id = jobdes.id \
 AND plat.id = j.platform_id \
 AND r.jobattribute_id = att.id \
 AND jobdes.application_id = apl.id \
 AND jobdes.options_id = opt.id \
 AND att.name = 'EVENT_LOOP' \
 AND rf.jobresults_ptr_id = r.id \
 AND apl.appname= 'BRUNEL' \
 AND opt.description = '1000Evts-COLLISION12-Beam4000GeV-VeloClosed-MagDown' \
 AND  plat.cmtconfig = 'x86_64-slc5-gcc43-opt' \
 AND ( apl.appversion = 'v43r2');")
        
        row = cursor.fetchall()
        
        #mylist = [ r[0] for r in row ]
        
        #create an INET, STREAMing socket
        s = socket.socket(
                          socket.AF_INET, socket.SOCK_STREAM)
        #now connect to the web server on port 80
        # - the normal http port
        s.connect(("localhost", 4321))
        filelike = s.makefile()
        #for i in range(5000):
        #    for r in row:
        #        socket_send(s,r)
        #for i in range(5000):
        #    socket_send(s,row)
        
        for i in range(5000):
           for r in row:
                dump(r, filelike)
                filelike.flush()
        #for i in range(5000):
        #   for r in row:
        #        dump(r, sys.stdout, 2)
        
        #socket_send(s,'finish')
        #yo = socket_recv(s)
       # s.close()
        #print yo
        
        #s.close()