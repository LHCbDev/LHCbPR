import socket
import socket_service as service

def get_results(requestDict, cursor):
    connection = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
    #now connect to the web server on port 80
    # - the normal http port
    connection.connect(("localhost", 4321))
    
    #send to ROOT_service histogram info from user's request
    
    service.send(connection,requestDict)
    
    #send to ROOT service the logical groups
    #service.send(connection,groups)
    
    groups = {}
    
    result = cursor.fetchone()
    while not result == None:
        group = tuple(result[:-1])
        if not group in groups:
            groups[group] = len(groups)
            service.send(connection, ('NEWGROUP', groups[group], group))
        service.send(connection, (groups[group], result[-1]))
        result = cursor.fetchone()
#    while not result == None:
#        service.send(connection, (tuple(result[:-1]), result[-1]))
#        result = cursor.fetchone()
    service.send(connection,'STAHP')
    answerDict = service.recv(connection)
    
    #connection.close()
    
    return answerDict