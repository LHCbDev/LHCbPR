import subprocess, os, json, pickle

def parse(DataDict,resultslist):
    path_to_save = os.getcwd()
    LogfileName = ''
    HistoFile = ''
    
    if inputValid(resultslist):
        for result in resultslist:
          fileName, fileExtension = os.path.splitext(result)
          if fileExtension == '.root':
              HistoFile = result
          else:
              LogfileName = result
        
        f  = open(path_to_save+'/DataDict.json','w')
        f.write(json.dumps(DataDict))
        f.close()
        
        outputfile = 'frafo.json'
        python_used = 'pythonROOT'
        parser = 'gaussRootReader.py'
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
    if not len(resultslist) == 2:
        return False
    
    for result in resultslist:
        fileName, fileExtension = os.path.splitext(result)
        if fileExtension == '.root':
            return True
    
    return False