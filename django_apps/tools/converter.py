import pickle, cPickle, zlib, bz2, base64

def serialize(obj, protocol='01'):
    """
    Takes as input a binary object(ex ROOT objects)
    and converts them into strings, depending on the protocol
    uses different methods
    """
    final_str = [protocol]
    if protocol == '01':
        final_str.append(base64.b64encode(zlib.compress(cPickle.dumps(obj))))
        return ''.join(final_str)
    elif protocol == '02':
        final_str.append(base64.b64encode(bz2.compress(cPickle.dumps(obj))))
        return ''.join(final_str) 
    elif protocol == '03':
        final_str.append(pickle.dumps(obj))
        return ''.join(final_str)
    else:
        return None

def deserialize(obj_str):
    """
    Convert the saved string to back to binary objects
    """
    protocol = obj_str[:2]
    if protocol == '01':
        return cPickle.loads(zlib.decompress(base64.b64decode(obj_str[2:])))
    elif protocol == '02':
        return cPickle.loads(bz2.decompress(base64.b64decode(obj_str[2:])))
    elif protocol == '03':
        return cPickle.loads(obj_str[2:])
    else:
        None