#!/usr/bin/env python
#
#  listNewEvtTypes.py 
#  Author   Emmanouil Kiagias, 6 June 2012
#
#  Create a file with the list of event types added to the package since
#  the last released version
#
#  Optionally the full path of the area to compare to can be given
#  By default the file is written in the $DECFILESROOT/doc directory
#
#  Use listNewEvtTypes.py --h for more information
#
import os, inspect, re, logging, json
from optparse import OptionParser
 
def difference(a, b):
    """ show whats in list b which isn't in list a """
    return list(set(b).difference(set(a))) 

def filterPick(list,regex):
    """ Filters the elements of the given list with the given regex """
    return [ m.group(0) for l in list for m in [regex.search(l)] if m ]

def getSplitted(version):
    """Takes a version and tranforms it like v41r0 ----> ['v', 41, 'r', '0']"""
    split_regex = re.compile('\d+|[^\d\s]+')
    splittedElement = []
    for v in re.findall(split_regex, version):
        if v.isdigit():
            splittedElement.append(int(v))
        else:
            splittedElement.append(v)
       
    return splittedElement

def getLatestVersion(path):
    """Takes a path(path with the versions), returns the latest"""
    listFolders = os.listdir(path)
    search_regex = re.compile('v(\d+)r(\d+)(?:p(\d+))?') 
    versions = filterPick(listFolders, search_regex)
        
    return sorted(versions, key = getSplitted )[-1]

decfilesrootpath = ''
try:
    decfilesrootpath = os.environ['DECFILESROOT'] 
except KeyError:
    #logging.info("VARIABLE "+key+" is not defined, using ../")
    decfilesrootpath = os.path.abspath('..')
     
DECFILESROOT_OPTIONS = decfilesrootpath+'/options'
ALL_VERSIONS = os.environ['LHCBRELEASES']+'/DBASE/Gen/DecFiles'
LATEST_VERSION_OPTIONS = ALL_VERSIONS+os.sep+getLatestVersion(ALL_VERSIONS)+'/options'
WRITE_OUTPUT_FILE = decfilesrootpath+'/doc/newdecfiles.txt'   


def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option( "-v" , "--version-path" , type="string" , 
                    dest="latestOptions" , default=LATEST_VERSION_OPTIONS, 
                    help="Path to version you want to compare [ default: %default ]") 
    parser.add_option( "-d" , "--decfilesrootOptions" , type="string" ,
                    dest="decfilesroot_options" , default=DECFILESROOT_OPTIONS, 
                    help="Path to DECFILESROOT/options (options to be compared with the latest version options [ default: %default ]") 
    parser.add_option( "-o" , "--output-path" , type="string" , 
                    dest="output_path" , default=WRITE_OUTPUT_FILE ,
                    help="Path to save the output file [ default: %default ]") 
    parser.add_option("-q", "--quiet", action="store_true",
                      dest="ssss", default=True,
                      help="Just be quiet (do not print info from logger)")
    
    (options, args) = parser.parse_args()
    
    if not options.ssss:
        logging.root.setLevel(logging.DEBUG)
    
    logging.info('Using LATEST_VERSION_OPTIONS: '+options.latestOptions)
    logging.info('Using DECFILESROOT_OPTIONS: '+options.decfilesroot_options)
    logging.info('Using OUTPUT_PATH: '+options.output_path+'\n')
                
    decroot_optionsall = os.listdir(options.decfilesroot_options)
    latest_optionsall = os.listdir(options.latestOptions)

    searchRegex = re.compile('[0-9]{8}')
    decroot_options = filterPick(decroot_optionsall,searchRegex)
    latest_options = filterPick(latest_optionsall,searchRegex)

    new_options = difference(latest_options, decroot_options)
    
    if len(new_options) > 0:
        DataDict = { 'new_options' : new_options }
        f = open(options.output_path,'w')
        f.write(json.dumps(DataDict))
        logging.info('Output file saved at: '+options.output_path+'\n')
    else:
        logging.info('No differences were found, no file created.\n')

if __name__ == "__main__":
    main()

