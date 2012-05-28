from xml.etree.ElementTree import ElementTree
from xml.parsers.expat import ExpatError
import json

def parse(xmlfile):
    """ 
    Parses the timing.xml output of Brunel v41r0p1 and fixes the final
    dictionary containing the full job 
    """
    tree = ElementTree()
    
    try:
        tree.parse(xmlfile)
    except ExpatError:
        return 'Invalid xml file!Check your syntax'
    except IOError:
        return 'No such file or directory!'
    except IndexError:
        return 'No input was given!\n'
      
    attributesList=[]
    for parent in tree.getiterator("alg"):
        for child in parent:
            attributeTemp = {}
            attributeTemp['name'] = parent.attrib.get("name")+'_'+child.tag 
            attributeTemp['data'] = child.text
            attributeTemp['description'] = ''
            attributeTemp['group'] = ''
            if child.tag == 'count':
               attributeTemp['type'] = 'Integer' 
            else:
               attributeTemp['type'] = 'Float' 
            
            attributesList.append(attributeTemp)
        
    
    return attributesList