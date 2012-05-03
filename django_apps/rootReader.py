#################################################################################
# Usage:
#  python GeneratorReferencePlots.py 
#  Exemple: 
#  python GeneratorReferencePlots.py -v -r GaussHistos_REF_30000000.root -f GaussOutput.txt -l GaussOutput.txt -s GaussHistos_24142001.root -i
#################################################################################

from ROOT import TFile, TCanvas, TH1D, gROOT
from ROOT import gDirectory, gPad, gStyle
from optparse import OptionParser
import re, sys, os, shutil, base64, json, cPickle

#################################################################################
def grepPattern(P,L):
  result = None
  resultobject = re.search( P , L )
  if ( resultobject != None ):
    result = resultobject.group(1)
  return result

#################################################################################
class GeneratorLogFile:
  def __init__(self,N):
    self.fileName = N
    self.GaussVersion = None
    self.PythiaVersion = None
    self.EventType = None
    self.TotalCrossSection = None
    self.TotalInteractions = None
    self.TotalIntWithB = None 
    self.TotalIntWithD = None
    self.TotalIntWithPromptCharm = None
    self.TotalAcceptedEvents = None
    self.TotalSignalProcessEvents = None
    self.TotalSignalProcessFromBEvents = None
    self.TotalZInvertedEvents = None
    self.TotalEventsAfterCut = None
    self.TotalTime = None
    
  def computeQuantities(self):
    f = open(self.fileName)
    for line in f:
      if ( self.EventType == None ):
        self.EventType = grepPattern('Requested to generate EventType (\d+)',line)
      if ( self.GaussVersion == None ):
        self.GaussVersion = grepPattern( 'Welcome to Gauss version (\S+)' , line )
      if ( self.PythiaVersion == None ):
        self.PythiaVersion = grepPattern( 'This is PYTHIA version (\S+)' , line )
      if ( self.TotalCrossSection == None ):
        self.TotalCrossSection = grepPattern( 'All included subprocesses *I *\d+ *\d+ I *(\S+)' , line )
        if (self.TotalCrossSection != None):
          if ('D' in self.TotalCrossSection):
            self.TotalCrossSection = self.TotalCrossSection.replace('D', 'E')
      if ( self.TotalInteractions == None ):
        self.TotalInteractions = grepPattern( 'Number of generated interactions : (\d+)' , line )
      if ( self.TotalIntWithB == None ):
        self.TotalIntWithB = grepPattern( 'Number of generated interactions with >= 1b : (\d+)' , line ) 
      if ( self.TotalIntWithD == None ):
        self.TotalIntWithD = grepPattern( 'Number of generated interactions with >= 1c : (\d+)' , line ) 
      if ( self.TotalIntWithPromptCharm == None):
        self.TotalIntWithPromptCharm = grepPattern( 'Number of generated interactions with >= prompt C : (\d+)' , line ) 
      if ( self.TotalAcceptedEvents == None ):
        self.TotalAcceptedEvents = grepPattern( 'Number of accepted events : (\d+)' , line )
      if ( self.TotalSignalProcessEvents == None ):
        self.TotalSignalProcessEvents = grepPattern( 'Number of events for generator level cut, before : (\d+)' , line)
      if ( self.TotalSignalProcessFromBEvents == None ):
        self.TotalSignalProcessFromBEvents = grepPattern( 'Number of accepted interactions with >= 1b : (\d+)' , line )
      if ( self.TotalZInvertedEvents == None ):
        self.TotalZInvertedEvents = grepPattern( 'Number of z-inverted events : (\d+)' , line )
      if ( self.TotalEventsAfterCut == None ):
        self.TotalEventsAfterCut = grepPattern( 'Number of events for generator level cut, before : \d+, after : (\d+)' , line )
      if ( self.TotalTime == None ):
        self.TotalTime = grepPattern( 'SequencerTime... *INFO *Generation *\| *(\S+)' , line )
        if ( self.TotalTime == None ):
          self.TotalTime = 0.
    f.close()
    
  def eventType(self):
    return self.EventType
  def gaussVersion(self):
    return self.GaussVersion
  def pythiaVersion(self):
    return self.PythiaVersion
  def totalCrossSection(self):
  #### This is the total cross-section printed by Pythia
    return float(self.TotalCrossSection)
  def bCrossSection(self):
  #### b quark or B hadron without b quark from production vertex
    return float( float(self.TotalCrossSection) * int(self.TotalIntWithB) / int(self.TotalInteractions))
  def cCrossSection(self):
  #### c quark or D hadron without c quark from production vertex
    return float( float(self.TotalCrossSection) * int(self.TotalIntWithD) / int(self.TotalInteractions))
  def promptCharmCrossSection(self):
  #### D hadron (like J/psi but also chi_c) without B hadron or c quark      
    return float( float(self.TotalCrossSection) * int(self.TotalIntWithPromptCharm) / int(self.TotalInteractions))
  def totalAcceptedEvents(self):
    return int(self.TotalAcceptedEvents)
  def signalProcessCrossSection(self):
  #### valid for J/psi (in general for all generation without CP mixture) 
    if (self.TotalSignalProcessEvents==None):
      return 0
    return float( float(self.TotalCrossSection) * int(self.TotalSignalProcessEvents) / int(self.TotalInteractions))
  def signalProcessFromBCrossSection(self):
  #### valid for J/psi (in general for all generation without CP mixture)
    return float( float(self.TotalCrossSection) * int(self.TotalSignalProcessFromBEvents) / int(self.TotalInteractions))
  def generatorLevelCutEfficiency(self):
    if ( self.TotalEventsAfterCut == None or self.TotalZInvertedEvents == None or self.TotalSignalProcessEvents == None ):
      return 0
    return float( ( int(self.TotalEventsAfterCut) - int(self.TotalZInvertedEvents) ) / float( self.TotalSignalProcessEvents) )
  def timePerEvent( self ):
    return float(self.TotalTime)

  def generateJsonOutput(self,name,histosDict):
      myDataDict = {}
      myDataDict['eventType'] = self.eventType()
      myDataDict['gaussVersion'] = self.gaussVersion()
      myDataDict['pythiaVersion'] = self.pythiaVersion()
      myDataDict['totalCrossSection'] = self.totalCrossSection()
      myDataDict['bCrossSection'] = self.bCrossSection()
      myDataDict['cCrossSection'] = self.cCrossSection()
      myDataDict['promptCharmCrossSection'] = self.promptCharmCrossSection()
      myDataDict['totalAcceptedEvents'] = self.totalAcceptedEvents()
      myDataDict['signalProcessCrossSection'] = self.signalProcessCrossSection()
      myDataDict['signalProcessFromBCrossSection'] = self.signalProcessFromBCrossSection()
      myDataDict['generatorLevelCutEfficiency'] = self.generatorLevelCutEfficiency()
      myDataDict['timePerEvent'] = self.timePerEvent()
      myDataDict['histograms'] = histosDict
      #keep the ROOT version
      myDataDict['ROOT_Version']= gROOT.GetVersion()
      
      f = open(name,'w')
      f.write(json.dumps(myDataDict))
       
#################################################################################  

# Read command line options
def main():
  usage = "usage: %prog [options]"
  parser = OptionParser(usage)
  parser.add_option( "-s" , "--histo" , action="store", type="string" , 
    dest="HistoName" , help="Histogram file to save" ) 
  parser.add_option( "-f" , "--log_file" , action="store" , type="string" ,
    dest="LogfileName" , help="Log file to save" ) 
  parser.add_option( "-o" , "--outputfile" , action="store" , type="string" ,
    dest="outputfile" , help="Name of the output file" )
      
  (options, args) = parser.parse_args()
  
  #####################################################################


  print "Read log file: " + options.LogfileName
  TheLog = GeneratorLogFile( options.LogfileName ) 
  TheLog.computeQuantities()
    
    
  print "Event type = " , TheLog.eventType() 
  print "Gauss version = " , TheLog.gaussVersion()
  print "Total event = " , TheLog.totalAcceptedEvents()
  print "Pythia version = " , TheLog.pythiaVersion()
  print "Total cross-section = " , TheLog.totalCrossSection()
  print "b cross-section = " , TheLog.bCrossSection()
  print "c cross-section = " , TheLog.cCrossSection()
  print "prompt charm = " , TheLog.promptCharmCrossSection()
  print "signal process cross-section = " , TheLog.signalProcessCrossSection()
  print "signal process from B cross-section = " , TheLog.signalProcessFromBCrossSection()
  print "generator level cut efficiency = " , TheLog.generatorLevelCutEfficiency()
  print "processing time per event = " , TheLog.timePerEvent()       
    
  #####  Histos    
  
  print "Saving data from histogram file: " + options.HistoName
  aFile = TFile( options.HistoName ) 
  
  Int = gDirectory.Get( 'GenMonitorAlg/10' )
  PrimaryVtxX = gDirectory.Get( 'GenMonitorAlg/11' ) 
  PrimaryVtxY = gDirectory.Get( 'GenMonitorAlg/12' ) 
  PrimaryVtxZ = gDirectory.Get( 'GenMonitorAlg/13' ) 
  Multiplicity = gDirectory.Get( 'GenMonitorAlg/3' )
  Pseudorap = gDirectory.Get( 'GenMonitorAlg/44' )
  Pt = gDirectory.Get( 'GenMonitorAlg/45' )
  Process = gDirectory.Get( 'GenMonitorAlg/5' )
  MultInLHCb = gDirectory.Get( 'GenMonitorAlg/4' ) 
  
  #encode TH1D objects
  histosDict = {}
  histosDict['Int']= cPickle.dumps(Int)
  histosDict['PrimaryVtxX']= cPickle.dumps(PrimaryVtxX)
  histosDict['PrimaryVtxY']= cPickle.dumps(PrimaryVtxY)
  histosDict['PrimaryVtxZ']= cPickle.dumps(PrimaryVtxZ)
  histosDict['Multiplicity']= cPickle.dumps(Multiplicity)
  histosDict['Pseudorap']= cPickle.dumps(Pseudorap)
  histosDict['Pt']= cPickle.dumps(Pt)
  histosDict['Process']= cPickle.dumps(Process)
  histosDict['MultInLHCb']= cPickle.dumps(MultInLHCb)
  
  TheLog.generateJsonOutput(options.outputfile,histosDict)
  aFile.Close()
  
  ###########################################################################
    
if __name__ == "__main__":
  main()
  
