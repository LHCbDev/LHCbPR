import os, re
from django.db.models import Q
from django.conf import settings
#extra functions which are used in lhcbPR app, i moved them here in order
#to keep the views clean

def combineStatements(StatementsDict, operator):
    """Takes a dictionary with statements, combines them depending on the
    given operator(AND,OR) and return a final query(query)"""
    query =  Q()
    for k,v in StatementsDict.iteritems():
        query.add(Q( **{ v : k }),operator)
    
    return query
     
def makeQuery(statement,arguments,operator):
    """Gets a list of different arguments and for each argument creates 
    a dictionary with the given statement
    example :
    argument : v43r0
    statement: application__appVersion__exact"""
    dataDict = {}
    
    for arg in arguments:
        dataDict[arg] = statement
        
    return combineStatements(dataDict, operator)

def makeCheckedList(mylist,are_checked = []):
    """For each dictionary in mylist check if the dictionary[key] 
    exists in the checked values, if yes/no it saves it as checked/unchecked 
    in a final dictionary list, this method is used for bookmarking the 
    filtering values in /jobDescriptions/APP_NAME page
    """
    List = []
    for myObj in mylist:
        if myObj in are_checked:
            List.append({'value' : myObj, 'checked' : True})
        else:
            List.append({'value' : myObj, 'checked' : False})
    return List

def handle_uploaded_file(f):
    path_to_save = os.path.join(settings.PROJECT_PATH, 'static/uploaded/'+f.name)
    with open( path_to_save , 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            
#change version (make decimal to str) with map function 
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], map(str,row)))
        for row in cursor.fetchall()
    ]

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