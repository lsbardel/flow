
__all__ = ['frequency', 'frequencies', 'frequencytuple']

class Frequency(object):
    
    def __init__(self, code, name, description):
        self.code = code
        self.name = name
        self.description = description
        
def frequency(code):
    c = str(code).upper()
    f = frequencies()
    return f.get(c,None)

def frequencies():
    '''
    Create the global frequency list
    '''
    global _freq1
    if _freq1 == None:
        li = []
        li.append(Frequency('D','1D','daily'))
        li.append(Frequency('W','1W','weekly'))
        li.append(Frequency('BW','2W','bi-weekly'))
        li.append(Frequency('M','1M','monthly'))
        li.append(Frequency('BM','2M','bi-monthly'))
        li.append(Frequency('Q','3M','quarterly'))
        li.append(Frequency('S','6M','semi-annual'))
        li.append(Frequency('A','1Y','annual'))
        li.append(Frequency('BA','2Y','bi-annual'))
        _freq1 = {}
        for l in li:
            _freq1[l.code] = l
    return _freq1

def frequencytuple():
    fs = frequencies()
    fl = []
    for f in fs.itervalues():
        fl.append((f.code,f.description))
    return fl

_freq1 = None