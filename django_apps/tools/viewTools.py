from django.db.models import Q
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
    dataDict = {}
    
    for arg in arguments:
        dataDict[arg] = statement
        
    return combineStatements(dataDict, operator)

def makeListChecked(mylist,key,are_checked = []):
    List = []
    for dict in mylist:
        if dict[key] in are_checked:
            List.append({'value' : dict[key], 'checked' : True})
        else:
            List.append({'value' : dict[key], 'checked' : False})
    return List