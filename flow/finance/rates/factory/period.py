


class parserBase(object):
    name = None
        
    def parse(self):
        pass
    
class dparser(object):
    name = 'daily'
    
    def parse(self):
        pass

periodParser = {'d': dparser()}