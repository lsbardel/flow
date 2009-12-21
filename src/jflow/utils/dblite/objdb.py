import bisect

from jflow.core.math import isnumeric

from dblite import dblite, DBentry, Field


class DBobjEntry(DBentry):
    
    def __init__(self,id,obj):
        super(DBobjEntry,self).__init__(id,obj)
        
    def get(self, key, def_ret=None):
        try:
            attr = getattr(self.data, key)
            if callable(attr):
                attr = attr()
            return attr
        except:
            return def_ret
    
    def __getitem__(self,key):
        return self.get(key)
    
    def __setitem__(self,key,val):
        raise AttributeError, 'Cannot assign the field'
        
    def __str__(self):
        return str(self.data)
    
    def __repr__(self):
        return self.__str__()


class objdb(dblite):
    '''
    Inline Object Database
    '''
    dbobject = DBobjEntry
    def __init__(self, NoneType = None, *args, **kwargs):
        super(objdb,self).__init__(*args, **kwargs)
        self.NoneType = NoneType
    
    def create(self, fields):
        self.fields = {}
        internalf   = self.InternalFields()
        for f in fields:
            fs = str(f)
            if fs in internalf:
                raise ValueError, 'Field %s not permitted' % fs
            if self.fields.get(fs,None) != None:
                raise ValueError, 'Duplicate Field %s' % fs
            sf = self.make_field(f)
            self.fields[fs] = sf
        
        self.records = {}
        self.next_id = 0
        self.indices = {}
        
    def insert(self, obj):
        '''
        Insert an object into the database
        '''
        if obj == None:
            return None
        self.next_id += 1
        try:
            pk  = getattr(obj,self.pk)
        except Exception, e:
            pk = self.next_id
            setattr(obj,self.pk,pk) 
        
        record = self.dbobject(pk,obj)
        self.records[record.id] = record
        
        # update index
        #for ix in self.indices.keys():
        #    bisect.insort(self.indices[ix].setdefault(record[ix],[]),id)
            
        return record
    
    def trim(self,val):
        if isnumeric(val):
            return val
        else:
            return str(val)
        
    def getid(self, obj):
        '''
        Get the object unique id.
        This can be reimplemented by derived classes
        '''
        return self.next_id
        
    def make_field(self,f):
        return Field(f)
    
    def get_field(self, fs):
        try:
            return self.make_field(fs)
        except:
            return None
        
    def InternalFields(self):
        return []
            
            