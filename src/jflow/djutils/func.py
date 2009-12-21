import re

from django.utils.safestring import mark_safe


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
    
    
    
def slugify(value, rtx = '-'):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip())
    return mark_safe(re.sub('[-\s]+', rtx, value))


def safepath(path, rtx = '-'):
    rpath = path.split('/')
    bits = []
    for p in rpath:
        if p:
            bits.append(slugify(p, rtx = rtx))
    return '/'.join(bits)