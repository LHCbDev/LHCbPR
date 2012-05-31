import subprocess, os, json, pickle, inspect
from handlers import parseTiming
import configs

def parse(DataDict,resultslist):
    path_to_save = os.getcwd()
    LogfileName = ''
    HistoFile = ''
    xmlfile = ''
    
    if inputValid(resultslist):
        for result in resultslist:
          fileName, fileExtension = os.path.splitext(result)
          if fileExtension == '.root':
              HistoFile = result
          elif fileExtension == '.xml':
              xmlfile = result
          else:
              LogfileName = result
        
        #change later
        DataDict['timingList'] = parseTiming.parse(xmlfile)
        
        f  = open(path_to_save+'/DataDict.json','w')
        f.write(json.dumps(DataDict))
        f.close()
        
        real_path = configs.work_path
        outputfile = 'frafo.json'
        python_used = real_path+'/'+'pythonROOT'
        parser = real_path+'/'+'gaussRootReader.py'
        argslist =('bash', python_used, parser, 
                   '-s', HistoFile, 
                   '-f', LogfileName, 
                   '-o', outputfile,
                   '-d', path_to_save+'/DataDict.json' )
    
        subprocess.call(argslist)
        
        return 'Parsing is done.'
    
    else:
        return 'Wrong input was given!!'
    
def inputValid(resultslist): 
    if not len(resultslist) == 3:
        return False
    
    for result in resultslist:
        fileName, fileExtension = os.path.splitext(result)
        if fileExtension == '.root':
            return True
    
    return False