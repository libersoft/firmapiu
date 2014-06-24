class Holder:
    
    def get_private_key(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def get_certificate(self):
        raise NotImplementedError("Subclass must implement abstract method")
