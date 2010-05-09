from base import DatabaseVendor

class manual(DatabaseVendor):
    
    def external(self):
        return False

manual()
            