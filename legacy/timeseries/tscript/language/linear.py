


class linearDecomp(object):
    
    def __init__(self):
        self.values = []
        self.sign   = sign
    
    def __len__(self):
        return len(self.values)
    
    def __iter__(self):
        return self.values.__iter__()
    
    def append(self, val, sign = 1):
        self.values.append((val,sign))
        return self
    
    def expand(self, ld):
        if isinstance(ld,linearDecomp):
            for v,s in ld:
                self.append(v,s)
        return self
        
    def changesign(self):
        for v in self.values:
            v[1] *= -1
        return self