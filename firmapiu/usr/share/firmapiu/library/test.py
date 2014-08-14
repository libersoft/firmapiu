

class Pippo(object):
    
    def __new__(cls, *args, **kwargs):
        print '__new__'
        return object.__new__(cls, *args, **kwargs)
    
    def __init__(self):
        print '__init__'

    def __enter__(self):
        print '__enter__'
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        print '__exit__'
        
    def __del__(self):
        print '__del__'
        
    def prova(self):
        print 'prova'


