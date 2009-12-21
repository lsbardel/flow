from django.db import models



class BondManager(models.Manager):
    
    def bullet(self, bond_class = None):
        return None