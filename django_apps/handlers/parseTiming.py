from xml.etree.ElementTree import ElementTree
from xml.parsers.expat import ExpatError
import json

def parse(DataDict,resultslist):
    """ 
    Parses the timing.xml output of Brunel v41r0p1 and fixes the final
    dictionary containing the full job 
    """
    tree = ElementTree(previousDataDict)
    #'/afs/cern.ch/user/e/ekiagias/workspace/database_test/database_test/inputs/results.xml'
    if not len(resultslist) == 1:
        return 'Wrong resultslist...try again!'
    
    try:
        tree.parse(resultslist[0])
    except ExpatError:
        return 'Invalid xml file!Check your syntax'
    except IOError:
        return 'No such file or directory!'
    except IndexError:
        return 'No input was given!\n'
      
    attributesList=[]
    attributeTemp = {}
    for parent in tree.getiterator("alg"):
        # parent.attrib.get("name")
        for child in parent:
            attributeTemp['name'] = parent.attrib.get("name")+'_'+child.tag 
            attributeTemp['data'] = child.text
            attributeTemp['description'] = ''
            if child.tag == 'count':
               attributeTemp['type'] = 'Integer' 
            else:
               attributeTemp['type'] = 'Float' 
        
        attributesList.append(attributeTemp)
    
    DataDict['JobAttributes'] = attributesList
    
    #return the results in json format
    return json.dumps(DataDict)