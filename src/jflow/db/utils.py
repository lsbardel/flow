

def django_choices(vals):
    '''
    vals is an iterable
    '''
    choices = []
    if isinstance(vals,dict):
        for k,v in vals.iteritems():
            choices.append((str(k),str(v)))
    else:
        try:
            for v in vals:
                sv = str(v)
                choices.append((sv,sv))
        except:
            pass
    return choices

def dict_from_choices(cho):
    di = {}
    for c in cho:
        di[c[0]] = c[1]
    return di



def inv_dict_from_choices(cho):
    di = {}
    for c in cho:
        di[c[1]] = c[0]
    return di
                           

def function_module(dotpath, default = None):
    '''
    Load a function from a module.
    If the module or the function is not available, return the default argument
    '''
    if dotpath:
        bits = str(dotpath).split('.')
        try:
            module = __import__('.'.join(bits[:-1]),globals(),locals(),[''])
            return getattr(module,bits[-1],default)
        except Exception, e:
            return default
    else:
        return default
