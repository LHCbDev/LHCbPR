import socket
import cPickle as serializer

CRLF = '\r\n'
class MalformedMessage(Exception): pass
class ConnectionClosed(Exception): pass

def read_exactly(sock, buflen):
    data = ''
    while len(data) != buflen:
        data += sock.recv(buflen - len(data))
    return data

def peek(sock, buflen):
    data = sock.recv(buflen, socket.MSG_PEEK)
    return data

#socket_send
def send(sock, obj):
    data = serializer.dumps(obj)
    size = len(data)
    sock.sendall('{0}{1}{2}'.format(size, CRLF, data))

#socket_recv
def recv(sock):
    peekdata = peek(sock, 1024)
    if peekdata == '':
        raise ConnectionClosed
    sizepos = peekdata.find(CRLF)
    if sizepos == -1:
        raise MalformedMessage('Did not find CRLF in message {0}'.format(peekdata))
    sizedata = read_exactly(sock, sizepos)
    read_exactly(sock, len(CRLF))
    try:
        size = int(sizedata)
    except ValueError:
        raise MalformedMessage(
            'size data {0} could not be converted to an int'.format(sizedata))
    data = read_exactly(sock, size)
    return serializer.loads(data)
