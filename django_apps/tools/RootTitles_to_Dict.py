import os
from ROOT import TFile, TCanvas, TH1D, TH1F, TPad, gROOT, TMath, TArrayF
from ROOT import gDirectory, gPad, gStyle

titles = [ 'Multiplicity stable charged particles',
          'Multiplicity stable charged particles in LHCb eta',
          'Process type',
          'Num. of primary interaction per bunch',
          'PrimaryVertex x (mm)',
          'PrimaryVertex y (mm)',
          'PrimaryVertex z (mm)',
          'Pseudorapidity stable charged particles',
          'Pt stable charged particles',
          ]

def getObjectsTitleId(self, titles_list):
    myDict = {}
    for key in gDirectory.GetListOfKeys():
        mypath = gDirectory.GetPathStatic()
        self.filterKey(key,mypath,myDict, titles_list)
        gDirectory.cd(mypath)
   
    return myDict

def filterKey( self, mykey , currentpath, toDict, titles_list):
     if mykey.IsFolder():
         topath =  os.path.join(currentpath, mykey.GetName()) 
         print topath
         self.cd(topath)
         for key in gDirectory.GetListOfKeys():
              self.filterKey(key,topath,toDict, titles_list)
     else:
         object_title = mykey.GetTitle()
         if object_title in titles_list: 
             toDict[object_title] = os.path.join(gDirectory.GetPathStatic().split(':')[1][1:].strip(), mykey.GetName())
         return
                 
TFile.filterKey = filterKey
TFile.getObjectsTitleId = getObjectsTitleId

#refFile = TFile( 'my_file.root' )
refFile = TFile('2testBrunel.root')
yo = refFile.getObjectsTitleId(titles)

print '\n'  
for k, v in yo.iteritems():
    print '{0} : {1}'.format(k, v)
print '\n'

for k, v in yo.iteritems():
    print refFile.Get(v).GetTitle()