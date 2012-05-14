from ROOT import TFile, TCanvas, TH1D, gROOT
from ROOT import gDirectory, gPad, gStyle
from optparse import OptionParser
import re, sys, os, shutil, json, cPickle, pickle

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

  def generateJsonOutput(self,attributeslist,DataDict,outputfile):
      """
      adds to the attribute's list the rest of the attributes and then 
      return the final json format
      """
      
      attributeslist.append(self.getAtrDict('eventType',self.eventType(),'Float',''))
      attributeslist.append(self.getAtrDict('gaussVersion',self.gaussVersion(),'String',''))
      attributeslist.append(self.getAtrDict('pythiaVersion',self.pythiaVersion(),'String',''))
      attributeslist.append(self.getAtrDict('totalCrossSection',self.totalCrossSection(),'Float',''))
      attributeslist.append(self.getAtrDict('bCrossSection',self.bCrossSection(),'Float',''))
      attributeslist.append(self.getAtrDict('cCrossSection',self.cCrossSection(),'Float',''))
      attributeslist.append(self.getAtrDict('promptCharmCrossSection',self.promptCharmCrossSection(),'Float',''))
      attributeslist.append(self.getAtrDict('totalAcceptedEvents',self.totalAcceptedEvents(),'Float',''))
      attributeslist.append(self.getAtrDict('signalProcessCrossSection',self.signalProcessCrossSection(),'Float',''))
      attributeslist.append(self.getAtrDict('signalProcessFromBCrossSection',self.signalProcessFromBCrossSection(),'Float',''))
      attributeslist.append(self.getAtrDict('generatorLevelCutEfficiency',self.generatorLevelCutEfficiency(),'Float',''))
      attributeslist.append(self.getAtrDict('timePerEvent',self.timePerEvent(),'Float',''))
      
      DataDict['JobAttributes'] = attributeslist
      
      f = open(outputfile,'w')
      f.write(json.dumps(DataDict))
       
  
  def getAtrDict(self,atrName,atrValue,type,description):
      """
      Fix a dictionary in the needed format with the attributes of the
      GeneratorLogFile class
      """
      atrDict = {}
      atrDict['name'] = atrName
      atrDict['data'] = atrValue
      atrDict['type'] = type
      atrDict['description'] = description
      
      return atrDict

def getRootList(HistoFile):
    aFile = TFile( HistoFile ) 
    ROOT_version = gROOT.GetVersion()
    dictList = []
    rootObjectDetails = [
                  ['GenMonitorAlg/10','Int','ROOT_Blob',''],
                  ['GenMonitorAlg/11','PrimaryVtxX','ROOT_Blob',''],
                  ['GenMonitorAlg/12','PrimaryVtxY','ROOT_Blob',''],
                  ['GenMonitorAlg/13','PrimaryVtxZ','ROOT_Blob',''],
                  ['GenMonitorAlg/3','Multiplicity','ROOT_Blob',''],
                  ['GenMonitorAlg/44','Pseudorap','ROOT_Blob',''],
                  ['GenMonitorAlg/45','Pt','ROOT_Blob',''],
                  ['GenMonitorAlg/5','Process','ROOT_Blob',''],
                  ['GenMonitorAlg/4','MultInLHCb','ROOT_Blob',''],
                ]
   
    for obj in rootObjectDetails:
        tempDict = {}
        tempDict['data'] = cPickle.dumps(gDirectory.Get(obj[0]))
        tempDict['type'] = obj[2]
        tempDict["ROOT_version"] = ROOT_version
        tempDict['name'] = obj[1]
        tempDict['description'] = obj[3]
        
        dictList.append(tempDict)
      
    aFile.Close()
    
    return dictList

def main():    
  usage = "usage: %prog [options]"
  parser = OptionParser(usage)
  parser.add_option( "-s" , "--histo" , action="store", type="string" , 
    dest="HistoName" , help="Histogram file to save" ) 
  parser.add_option( "-f" , "--log_file" , action="store" , type="string" ,
    dest="LogfileName" , help="Log file to save" ) 
  parser.add_option( "-o" , "--outputfile" , action="store" , type="string" ,
    dest="outputfile" , help="Name of the output file" )
  parser.add_option( "-d" , "--datadict" , action="store" , type="string" ,
    dest="DataDict" , help="Path to dictionary file" )
      
  (options, args) = parser.parse_args()
  
  f = open(options.DataDict,'r').read()
  myDataDict = json.loads(f)
  
  TheLog = GeneratorLogFile( options.LogfileName ) 
  TheLog.computeQuantities()
        
  TheLog.generateJsonOutput(getRootList(options.HistoName), myDataDict,options.outputfile)
  
  #just remove the temporary file, to be avoided
  os.remove(options.DataDict)
    
if __name__ == "__main__":
  main()