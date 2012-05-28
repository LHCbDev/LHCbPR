from xml.etree.ElementTree import ElementTree
from xml.parsers.expat import ExpatError
from handlers import parseTiming
import json

def parse(DataDict,resultslist):
    """ 
    Parses the timing.xml output of Brunel v41r0p1 and fixes the final
    dictionary containing the full job 
    """
    tree = ElementTree()
    if not len(resultslist) == 1:
        return 'Wrong resultslist...try again!'
        
    DataDict['JobAttributes'] = parseTiming.parse(resultslist[0])
    
    #return the results in json format
    return json.dumps(DataDict)