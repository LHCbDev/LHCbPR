#################################################################################
# Usage:
#  python GeneratorReferencePlots.py 
#  Exemple: 
#  python GeneratorReferencePlots.py -v -r GaussHistos_REF_30000000.root -f GaussOutput.txt -l GaussOutput.txt -s GaussHistos_24142001.root -i
#################################################################################
from ROOT import TFile, TCanvas, TH1D, gROOT
from ROOT import gDirectory, gPad, gStyle
from optparse import OptionParser
import re, sys, os, shutil, json , cPickle, configs,base64,zlib
from tools import converter

################################################################################
class GeneratorHisto:
  def __init__(self,c,RH,OH,XT,YT,HT,FN,LS):
    self.canvas = c
    self.referenceHisto = RH
    self.compHisto = OH
    self.XTitle = XT 
    self.YTitle = YT
    self.HistTitle = HT
    self.FileName = FN
    self.LogScale = LS
    self.path_to_save = configs.project_work_path+'static/images/'
    
  def title(self):
    return self.HistTitle
  def refFileName(self):
    return "Reference"+self.FileName+".png"
  def fileName(self):
    return self.FileName+".png"
  def compFileName(self):
    return "Comp"+self.FileName+".png"    
    
  def plot(self):
    self.referenceHisto.GetXaxis().SetTitle( self.XTitle) 
    self.referenceHisto.GetXaxis().SetLabelSize( 0.025 ) 
    self.referenceHisto.GetYaxis().SetTitle( self.YTitle ) 
    self.referenceHisto.GetYaxis().SetLabelSize( 0.025 ) 
    self.referenceHisto.SetMarkerStyle(20)
    self.referenceHisto.SetMarkerColor(2)
    self.referenceHisto.SetMarkerSize(1.0)
    self.referenceHisto.SetTitle(self.HistTitle)
    if self.LogScale:
      gPad.SetLogy()
    else:
      gPad.SetLogy(0)
    self.referenceHisto.DrawNormalized('') 
    self.canvas.Update()
    self.canvas.Print(self.path_to_save+self.refFileName())  
#
    self.compHisto.GetXaxis().SetTitle( self.XTitle) 
    self.compHisto.GetXaxis().SetLabelSize( 0.025 ) 
    self.compHisto.GetYaxis().SetTitle( self.YTitle ) 
    self.compHisto.GetYaxis().SetLabelSize( 0.025 ) 
    self.compHisto.SetMarkerStyle(21)
    self.compHisto.SetMarkerColor(4)
    self.compHisto.SetMarkerSize(1.0)
    self.compHisto.SetTitle(self.HistTitle)
    if self.LogScale:
      gPad.SetLogy()
    else:
      gPad.SetLogy(0)
    self.compHisto.DrawNormalized('') 
    self.canvas.Update()
    self.canvas.Print(self.path_to_save+self.fileName())            
#
    self.referenceHisto.DrawNormalized('SAME')
    self.canvas.Update()
    self.canvas.Print(self.path_to_save+self.compFileName())     
    

# Read command line options
def main():
  #run ROOT in batch mode
  gROOT.SetBatch(True)
  
  usage = "usage: %prog [options]"
  parser = OptionParser(usage)
  parser.add_option( "-f" , "--fileinput" , action="store", type="string" , 
    dest="filein" , help="TH1D objects' file" ) 
      
  (options, args) = parser.parse_args()

 
  f = open(options.filein,'r').read()
  gloDict = json.loads(f)
  
  rDict={}
  rDict = gloDict['reference']
  
  IntREF = converter.deserialize(str(rDict['Int']))
  PrimaryVtxXREF = converter.deserialize(str(rDict['PrimaryVtxX']))
  PrimaryVtxYREF = converter.deserialize(str(rDict['PrimaryVtxY']))
  PrimaryVtxZREF = converter.deserialize(str(rDict['PrimaryVtxZ']))
  MultiplicityREF = converter.deserialize(str(rDict['Multiplicity']))
  PseudorapREF = converter.deserialize(str(rDict['Pseudorap']))
  PtREF = converter.deserialize(str(rDict['Pt']))
  ProcessREF = converter.deserialize(str(rDict['Process']))
  MultInLHCbREF = converter.deserialize(str(rDict['MultInLHCb']))
  
  #IntREF = cPickle.loads(str(rDict['Int']))
  #PrimaryVtxXREF = cPickle.loads(str(rDict['PrimaryVtxX']))
  #PrimaryVtxYREF = cPickle.loads(str(rDict['PrimaryVtxY']))
  #PrimaryVtxZREF = cPickle.loads(str(rDict['PrimaryVtxZ']))
  #MultiplicityREF = cPickle.loads(str(rDict['Multiplicity']))
  #PseudorapREF = cPickle.loads(str(rDict['Pseudorap']))
  #PtREF = cPickle.loads(str(rDict['Pt']))
  #ProcessREF = cPickle.loads(str(rDict['Process']))
  #MultInLHCbREF = cPickle.loads(str(rDict['MultInLHCb']))
  
  
  cDict={}
  cDict = gloDict['current']
  
  Int = converter.deserialize(str(cDict['Int']))
  PrimaryVtxX = converter.deserialize(str(cDict['PrimaryVtxX']))
  PrimaryVtxY = converter.deserialize(str(cDict['PrimaryVtxY']))
  PrimaryVtxZ = converter.deserialize(str(cDict['PrimaryVtxZ']))
  Multiplicity = converter.deserialize(str(cDict['Multiplicity']))
  Pseudorap = converter.deserialize(str(cDict['Pseudorap']))
  Pt = converter.deserialize(str(cDict['Pt']))
  Process = converter.deserialize(str(cDict['Process']))
  MultInLHCb = converter.deserialize(str(cDict['MultInLHCb']))
  
  #Int = cPickle.loads(str(cDict['Int']))
  #PrimaryVtxX = cPickle.loads(str(cDict['PrimaryVtxX']))
  #PrimaryVtxY = cPickle.loads(str(cDict['PrimaryVtxY']))
  #PrimaryVtxZ = cPickle.loads(str(cDict['PrimaryVtxZ']))
  #Multiplicity = cPickle.loads(str(cDict['Multiplicity']))
  #Pseudorap = cPickle.loads(str(cDict['Pseudorap']))
  #Pt = cPickle.loads(str(cDict['Pt']))
  #Process = cPickle.loads(str(cDict['Process']))
  #MultInLHCb = cPickle.loads(str(cDict['MultInLHCb']))
  
  c1 = TCanvas( 'c1' , 'Gauss' , 200 , 10 , 800 , 800 ) 
  
  gStyle.SetOptStat(2210)
  
  ####################################################################
  nIntRefHist = GeneratorHisto( c1 , IntREF , Int ,
    "Number of interactions" , "N" , "Number of primary interactions per bunch" ,
    "NInteractionsPerBunch" , True ) 
  nIntRefHist.plot()
  
  ####################################################################
  primaryVtxXRefHist = GeneratorHisto( c1 , PrimaryVtxXREF , PrimaryVtxX ,
    "x (mm)" , "N/0.01 mm" , "x position of primary vertex" ,
    "XPrimaryVtx" , False )
  primaryVtxXRefHist.plot()
  
  
  ####################################################################
  primaryVtxYRefHist = GeneratorHisto( c1 , PrimaryVtxYREF , PrimaryVtxY ,
    "y (mm)" , "N/0.01 mm" , "y position of primary vertex" ,
    "YPrimaryVtx" , False )
  primaryVtxYRefHist.plot()
  
  
  ####################################################################
  primaryVtxZRefHist = GeneratorHisto( c1 , PrimaryVtxZREF , PrimaryVtxZ ,
    "z (mm)" , "N/4 mm" , "z position of primary vertex" ,
    "ZPrimaryVtx" , False )
  primaryVtxZRefHist.plot()
  
  
  ####################################################################
  multiplicityRefHist = GeneratorHisto( c1 , MultiplicityREF , Multiplicity ,
    "N(charged particles)" , "N/5" , "Multiplicity of stable charged particles in 4#pi" ,
    "Multiplicity" , True )
  multiplicityRefHist.plot()
 
  
  ####################################################################
  pseudorapRefHist = GeneratorHisto( c1 , PseudorapREF , Pseudorap ,
    "#eta" , "N/0.2" , "#eta of stable charged particles in 4#pi" ,
    "Pseudorapidity" , False )
  pseudorapRefHist.plot()
  
  
  ####################################################################
  ptRefHist = GeneratorHisto( c1 , PtREF , Pt , 
    "p_{T} (GeV/c)" , "N/40 MeV/c" , "p_{T} of stable charged particles in 4#pi" ,
    "Pt" , True )
  ptRefHist.plot()
  
  
  ####################################################################
  processRefHist = GeneratorHisto( c1 , ProcessREF , Process ,  
    "Process Number" , "N" , "Process" ,
    "Process" , False )
  processRefHist.plot()
 
  
  ####################################################################
  multiplicityInLHCbRefHist = GeneratorHisto( c1 , MultInLHCbREF , MultInLHCb ,
    "N(charged particles)" , "N/5" , "Multiplicity of charged particles in LHCb" ,
    "MultiplicityInLHCb" , True )
  multiplicityInLHCbRefHist.plot()
  
  
  ####################################################################
   
if __name__ == "__main__":
  main()
  
