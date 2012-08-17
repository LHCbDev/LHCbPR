import os, sys, subprocess, inspect, json
from optparse import OptionParser
from optparse import Option, OptionValueError

def JobDictionary(hostname,starttime,endtime,cmtconfig,jodDesId):
    """
    For the time this method is needed to fill a dictionary,with some useful data,
    which will be passed to the subprocesses, is used for testing for the moment,
    later to be deleted
    """
    
    hostDict = { 'hostname': hostname, 'cpu_info': '', 'memoryinfo': ''}
    cmtconfigDict = {'platform': cmtconfig}
    DataDict = {
                'HOST': hostDict,
                'CMTCONFIG': cmtconfigDict,
                'time_start': starttime,
                'time_end': endtime,
                'status': '',
                'id_jobDescription': jodDesId
                }
    
    return DataDict

def main():
    #this is used for checking
    needed_options = 12
    description = """The program needs all the input arguments(options in order to run properly"""
    parser = OptionParser(usage='usage: %prog [options]',
                          description=description)
    parser.add_option('-r', '--results-directory', 
                      action='store', type='string',
                      dest='results', default=".", 
                      help='Directory which contains results')
    parser.add_option( '-s' , '--start-time' , action='store', type='string' , 
                    dest='startTime' , help='The start time of the job.') 
    parser.add_option( '-e' , '--end-time' , action='store', type='string' , 
                    dest="endTime" , help="The end time of the job.") 
    parser.add_option( "-p" , "--hostname" , action="store", type="string" , 
                    dest="hostname" , help="The name of the host who runned the job.")
    parser.add_option( "-c" , "--cmtconfig" , action="store", type="string" , 
                    dest="cmtconfig" , help="The cmtconfig of the job.")  
    parser.add_option( "-j" , "--jobDescription-id" , action="store", type="string" , 
                    dest="jobDescription_id" , help="The job description unique id.")
    parser.add_option("-l" , "--list-handlers" , action="store", type="string" , 
                    dest="handlers" , help="The list of handlers(comma separated.")  
    #check if all  the options were given
    if len(sys.argv) < needed_options:
        parser.parse_args(['--help'])

    options, args = parser.parse_args()
    
    dataDict = JobDictionary(options.hostname,options.startTime,options.endTime,
                       options.cmtconfig,options.jobDescription_id)
    
    jobAttributes = []

    for handler in options.handlers.split(','):
        module = ''.join(['handlers','.',handler])
        mod = __import__(module, fromlist=[module])
        
        klass = getattr(mod, handler)
        currentHandler = klass()
        
        currentHandler.collectResults(options.results)
        jobAttributes.extend(currentHandler.getResults())
    
    dataDict['JobAttributes'] = jobAttributes
        
    print json.dumps(dataDict)

if __name__ == '__main__':
    main()
