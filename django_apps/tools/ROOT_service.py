import socket, cPickle, os, sys, inspect, random
from threading import Thread
import socket_service as service
from ROOT import TFile, TCanvas, TH1D, TH1F, TPad, gROOT, TMath, TArrayF
from ROOT import gDirectory, gPad, gStyle

gROOT.SetBatch(True)
#gStyle.SetOptStat(000000000)
#remove the label of imposed histograms   
gStyle.SetOptStat(000000000)
#blue , red, green
colors = [4, 2, 3]
colorsName = [ 'blue', 'red', 'green' ]

parent_work_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
write_path = 'static/images/histograms/'
#create an INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#bind the socket to a public host,
# and a well-known port
serversocket.bind(('localhost', 4321))
#become a server socket
serversocket.listen(5)

#those methods/classes are used for the basic analysis
def define_bins(request,groupvalues):
    step = 10
    bins = {}
    min_max_values = [ [ v.minvalue, v.maxvalue ] for g, v in groupvalues.iteritems() ]
    
    if request['xup'] == '':
        bins['xup'] = max([ i[1] for i in min_max_values ])
    else:
        bins['xup'] = int(request['xup'])
    if request['xlow'] == '':
        bins['xlow'] = min([ i[0] for i in min_max_values ])
    else:
        bins['xlow'] = float(request['xlow'])
    if request['nbins'] == '':
        bins['nbins'] = 100
    else:
        bins['nbins'] = float(request['nbins'])
    
    return bins

class GroupDict(dict):
    def __getitem__(self, key):
        if key not in self:
            self[key] = []
        return dict.__getitem__(self, key)

class Stats(object):
    def __init__(self, data):
        self.data = data
        self.minvalue = min(data)
        self.maxvalue = max(data)
        array = TArrayF(len(data))
        for i, v in enumerate(data):
            array.SetAt(v, i)
        self._array = array
        self.mean = round(TMath.Mean(array.GetSize(), array.GetArray()),2)
        self.stdev = round(TMath.RMS(array.GetSize(), array.GetArray()),2)
        if self.mean == 0:
            self.stdev_per = 0
        else:
            self.stdev_per = round((self.stdev/self.mean)*100,2)
        self.count = array.GetSize()
        
    def histogramObject(self, bins,name):
        h0f = TH1F("histogram","{0} values".format(name),bins['nbins'],bins['xlow'],bins['xup'])
        for value in self.data:
            h0f.Fill(value)
        
        return h0f

def Stats_to_dict(key, value, cursor_description):
    datadict = dict(zip(cursor_description, key)) 
    datadict['STDEV'] = value.stdev
    datadict['AVERAGE'] = value.mean
    datadict['STDEV_PER'] = value.stdev_per
    datadict['ENTRIES'] = value.count
    
    return datadict

def plot_histogram(histogramObjects):
    c1 = TCanvas("c1","The Histograms",200,10,450,400)
    c1.SetFillColor(18)
     
    firstLoop = True
    
    for i, hist in enumerate(histogramObjects):
        hist.SetLineColor(colors[i])
        if firstLoop:
            hist.Draw()
            firstLoop = False
        else:
            hist.Draw('same')
        c1.Update()
    
    serve_path = 'static/images/histograms/histogram{0}{1}.png'.format(random.randint(1, 100),random.randint(1, 100))
    c1.Print(os.path.join(parent_work_path , serve_path))
    
    return '/{0}'.format(serve_path)

def basic_ROOT_service(remoteservice):
    try:
        #reading the request info(histogram, nbins, xlow, xup etc)
        request_info = remoteservice.recv()

        group_dict = GroupDict()
        group_names = {}
        
        while True:
            obj = remoteservice.recv()
            if obj == 'STAHP':
                print 'user requested stop'
                break
            elif obj[0] == 'NEWGROUP':
                group_names[obj[1]] = obj[2]
            else:
                group_id, value = obj
                group_dict[group_id].append(value)   
                
        groups_dict = dict((group_names[g], Stats(v)) for g, v in group_dict.iteritems())
        all_results = []
        
        bins = None
        if request_info['histogram'] == True:
            bins = define_bins(request_info,groups_dict)
            
            if request_info['separately_hist'] == True:
                for k, v in groups_dict.iteritems():
                    result = Stats_to_dict(k,v,request_info['description'])
                    result['histogram'] = plot_histogram([ v.histogramObject(bins,request_info['atr']) ])
                    all_results.append(result)

            else:
                histogramObjects = []
                for k, v in groups_dict.iteritems():
                    histogramObjects.append(v.histogramObject(bins,request_info['atr']))
                
                histogramImposedUrl = plot_histogram(histogramObjects)
                for i, keyvalue in enumerate(groups_dict.iteritems()):
                    k, v = keyvalue
                    result = Stats_to_dict(k,v,request_info['description'])
                    result['histogram'] = colorsName[i]
                    result['histogramImposed'] = histogramImposedUrl
                    all_results.append(result)

        else:
           for k, v in groups_dict.iteritems():
               result = Stats_to_dict(k,v,request_info['description'])
               all_results.append(result)
        
        remoteservice.send({ 'results' : all_results, 'bins' : bins })
        remoteservice.finish()
        
    except Exception,e:
        remoteservice.finish()
        print '{0}  {1}'.format(Exception,e)
    finally:
        print '\nfinished work exiting...'
        return 
    

class remoteService(object):
    def __init__(self,connection):
        self.connection = connection
    def send(self, data):
        service.send(self.connection, data)
    def recv(self):
        return service.recv(self.connection)
    def finish(self):
        self.connection.close()

print "start listening..."
while True:
    (clientsocket, address) = serversocket.accept()
    remoteservice = remoteService(clientsocket)
    t = Thread(target=basic_ROOT_service, args=(remoteservice,))
    t.start()