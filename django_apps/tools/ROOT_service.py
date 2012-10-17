import socket, cPickle, os, sys, inspect, random
from threading import Thread
import socket_service as service
from ROOT import TFile, TCanvas, TH1D, TH1F, TPad, gROOT, TMath, TArrayF
from ROOT import gDirectory, gPad, gStyle

gROOT.SetBatch(True)
gStyle.SetOptStat(000000000)

#remove the label of imposed histograms   
gStyle.SetOptStat(000000000)

#blue , red, green
colors = [4, 2, 3]
colorsName = [ 'blue', 'red', 'green' ]

parent_work_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
write_path = 'static/images/histograms/'
#create an INET, STREAMing socket
serversocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
#bind the socket to a public host,
# and a well-known port
serversocket.bind(('localhost', 4321))
#become a server socket
serversocket.listen(5)

def defineHistogramBins(request,groupvalues):
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
        bins['xlow'] = int(request['xlow'])
    if request['nbins'] == '':
        bins['nbins'] = int((bins['xup']-bins['xlow'])/step)+1
    else:
        bins['nbins'] = int(request['nbins'])
    
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
        self.stdev_per = round((self.stdev/self.mean)*100,2)
        self.count = array.GetSize()
        
    def histogramObject(self, bins,name):
        h0f = TH1F("histogram","{0} values".format(name),bins['nbins'],bins['xlow'],bins['xup'])
        for value in self.data:
            h0f.Fill(value)
        
        return h0f
    
    def histogramUrl(self,bins,request, write_path ):
        c1 = TCanvas("c1","The Histograms",200,10,450,400)
        c1.SetFillColor(18)
        h0f = TH1F("histogram","{0} values".format(request['atr']),bins['nbins'],bins['xlow'],bins['xup'])
        for value in self.data:
            h0f.Fill(value)
        h0f.Draw()
        c1.Update()
        
        subpath = 'static/images/histograms/{0}/histogram{1}{2}.png'.format(request['user'], self.count,random.randint(1, 50))
        c1.Print( os.path.join(write_path , subpath) )
        
        return '/{0}'.format(subpath)

def generate_results(clientsocket):
    #set gStyle back to default
    #gStyle.SetOptStat(000001111)
    try:
        #reading the request info(histogram, nbins, xlow, xup etc)
        request_info = service.recv(clientsocket)

        group_dict = GroupDict()
        group_names = {}
        
        while True:
            obj = service.recv(clientsocket)
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
        
        if request_info['histogram'] == True:
            bins = defineHistogramBins(request_info,groups_dict)
            write_to = os.path.join(parent_work_path , 'static/images/histograms/{0}/'.format(request_info['user']))
            if not os.path.isdir(write_to):
                os.makedirs(write_to)
            
            if request_info['separately_hist'] == True:
                for k, v in groups_dict.iteritems():
                    result = dict(zip(request_info['description'], k)) 
                    result['STDEV'] = v.stdev
                    result['AVERAGE'] = v.mean
                    result['STDEV_PER'] = v.stdev_per
                    result['ENTRIES'] = v.count
                    result['histogram'] = v.histogramUrl(bins, request_info,parent_work_path)
                    all_results.append(result)
                
                service.send(clientsocket,all_results)
                clientsocket.close()
                return
                
            else:
                c1 = TCanvas("c1","The Histograms",200,10,450,400)
                c1.SetFillColor(18)
                histogramObjects = []
                
                for k, v in groups_dict.iteritems():
                    histogramObjects.append(v.histogramObject(bins,request_info['atr']))
                 
                firstLoop = True
                
                for i, hist in enumerate(histogramObjects):
                    hist.SetLineColor(colors[i])
                    if firstLoop:
                        hist.Draw()
                        firstLoop = False
                    else:
                        hist.Draw('same')
                    c1.Update()
                
                serve_path = 'static/images/histograms/{0}/histogramImposed.png'.format(request_info['user'])
                c1.Print(os.path.join(parent_work_path , serve_path))
                i=0
                for k, v in groups_dict.iteritems():
                    result = dict(zip(request_info['description'], k)) 
                    result['STDEV'] = v.stdev
                    result['AVERAGE'] = v.mean
                    result['STDEV_PER'] = v.stdev_per
                    result['ENTRIES'] = v.count
                    result['histogram'] = colorsName[i]
                    result['histogramImposed'] = '/{0}'.format(serve_path)
                    all_results.append(result)
                    i+=1
                   
                service.send(clientsocket,all_results)
                clientsocket.close()
                return
                
        else:
           for k, v in groups_dict.iteritems():
               result = dict(zip(request_info['description'], k)) 
               result['STDEV'] = v.stdev
               result['AVERAGE'] = v.mean
               result['STDEV_PER'] = v.stdev_per
               result['ENTRIES'] = v.count
               all_results.append(result)
               
           service.send(clientsocket,all_results)
           clientsocket.close()
           return
        
    except Exception,e:
        print str(Exception)+' '+str(e)
    finally:
        print '\nfinished work exiting...'
        #print 'total objects now received :'+str(counter)
    return 
    

print "start listening..."
while True:
    (clientsocket, address) = serversocket.accept()
    t = Thread(target=generate_results, args=(clientsocket,))
    t.start()