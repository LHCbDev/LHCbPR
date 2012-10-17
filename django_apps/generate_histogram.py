import json, os

from ROOT import TFile, TCanvas, TH1D, TH1F, TPad, gROOT
from ROOT import gDirectory, gPad, gStyle


gROOT.SetBatch(True)

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
path_to = os.path.join(PROJECT_PATH, 'static/images/histograms/')

f = open(os.path.join(PROJECT_PATH, 'static/images/histograms/values_list'),'r').read()
dataDict = json.loads(f)
mylist = dataDict['values_list']

c1 = TCanvas("c1","The FillRandom example",200,10,450,400)
c1.SetFillColor(18)
h1f = TH1F("h1f","{0} values".format(dataDict['atr']),dataDict['nbins'],dataDict['xlow'],dataDict['xup'])
h1f.SetFillColor(45)
for value in mylist:
    h1f.Fill(value)
h1f.Draw()
c1.Update()

#just an example , to be changed
c1.Print(os.path.join(PROJECT_PATH, 'static/images/histograms/histogram.png'))
