import errno

def read_file(filepath):
    try:
        fp = open(filepath)
    except IOError as e:
        if e.errno == errno.EACCES:
            return None
        # Not a permission error.
        if e.errno == errno.ENOENT:
            return None
        raise
    else:  # se non viene lanciata un eccezione
        with fp:
            return fp.read()
        
def write_file(filepath, data):
    try:
        fp = open(filepath, 'w')
    except IOError as e:
        if e.errno == errno.EACCES:
            return None
        # Not a permission error.
        raise
    else:  # se non viene lanciata un eccezione
        with fp:
            return fp.write(data)
        