import os, sys, subprocess
from optparse import OptionParser
from optparse import Option, OptionValueError

class MultipleOption(Option):
    """
    This class provides an extra action to the option parser
    so the user can assign multiple arguments to a unique option
    (giving arguments from the command line) 
    """
    ACTIONS = Option.ACTIONS + ("extend",)
    STORE_ACTIONS = Option.STORE_ACTIONS + ("extend",)
    TYPED_ACTIONS = Option.TYPED_ACTIONS + ("extend",)
    ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("extend",)

    def take_action(self, action, dest, opt, value, values, parser):
        """
        Split the contiguous arguments in the comma and stores 
        them to the destination
        """
        if action == "extend":
            lvalue = value.split(",")
            values.ensure_value(dest, []).extend(lvalue)
        else:
            Option.take_action(
                self, action, dest, opt, value, values, parser)

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

def getHandler(jobDesID):
    """
    Take as a parameter a job description id and returns the proper 
    handler for handling this job id
    """
    python_used = 'python26'
    manager = 'manage.py'
    command = 'getHandler'
    argslist =(python_used, manager, command, jobDesID )
    
    p = subprocess.Popen(argslist, stdout=subprocess.PIPE)
    result, err = p.communicate()

    return result
    
def getImportCommand(jobDesID):
    """
    Makes the command(in string format) to import the proper
    handler
    """
    myhandler = getHandler(jobDesID)

    return 'from handlers import '+myhandler+' as handler'

def main():
    #this is used for checking
    needed_options = 12
    description = """The program needs all the input arguments(options in order to run properly"""
    parser = OptionParser(option_class=MultipleOption,
                          usage='usage: %prog [options]',
                          description=description)
    parser.add_option('-r', '--results-job', 
                      action="extend", type="string",
                      dest='results', 
                      help='Comma separated list of input results of a job or multiple -r assignments.')
    parser.add_option( "-s" , "--start-time" , action="store", type="string" , 
                    dest="startTime" , help="The start time of the job.") 
    parser.add_option( "-e" , "--end-time" , action="store", type="string" , 
                    dest="endTime" , help="The end time of the job.") 
    parser.add_option( "-p" , "--hostname" , action="store", type="string" , 
                    dest="hostname" , help="The name of the host who runned the job.")
    parser.add_option( "-c" , "--cmtconfig" , action="store", type="string" , 
                    dest="cmtconfig" , help="The cmtconfig of the job.")  
    parser.add_option( "-j" , "--jobDescription-id" , action="store", type="string" , 
                    dest="jobDescription_id" , help="The job description unique id.")  
    #check if all  the options were given
    if len(sys.argv) < needed_options:
        parser.parse_args(['--help'])

    options, args = parser.parse_args()
    
    dataDict = JobDictionary(options.hostname,options.startTime,options.endTime,
                       options.cmtconfig,options.jobDescription_id)
    
    exec getImportCommand(options.jobDescription_id)
    
    print handler.parse(dataDict,options.results)

if __name__ == '__main__':
    main()
