


class fieldproxy(object):
    
    def __init__(self, name, *args):
        self.name = str(name)
        self.__underlyings = None
        if args:
            self.__underlyings = []
            for a in args:
                if not isinstance(a,fieldproxy):
                    a = fieldproxy(a) 
                self.__underlyings.append(a)
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    def __get_underlyings(self):
        return self.__underlyings
    underlyings = property(fget = __get_underlyings)
    
    def value(self,rate):
        return rate._get(self.name)


    
    
    
    