"""
Both methods get a dictionary containg the request data and
return a dictionary with the response data.
To check if an error occurred while making the request you can check
if 'error' field is True or False and print the errorMessage if needed
"""
import urllib, urllib2, json

#urls to make the requests
newjobdescription_url = 'http://lhcb-pr.web.cern.ch/lhcb-pr/newjobdescription'
getcontent_url = 'http://lhcb-pr.web.cern.ch/lhcb-pr/getcontent/'

def newjobdescription(dataDict):
    """
    dictionary input must at least contain the following keys:
        application, version and optionsD
    optional extra keys(in case you want to create a new job description)
        options, setupproject, setupprojectD 
    """
    #create an opener
    opener = urllib2.build_opener()
    
    req = urllib2.Request(newjobdescription_url)
    req.add_data(urllib.urlencode(dataDict))
    
    return json.loads(opener.open(req).read())

def getcontent(dataDict):
    """
    dictionary input must contain either setupprojectD or optionsD key
    """
    #create an opener
    opener = urllib2.build_opener()
    
    req = urllib2.Request(getcontent_url)
    req.add_data(urllib.urlencode(dataDict))
    
    return json.loads(opener.open(req).read())