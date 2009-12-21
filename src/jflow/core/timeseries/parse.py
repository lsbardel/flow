
from tscript import expr
import operators

__all__ = ['parsets','unwind','tojson']

def parsets(input):
    '''
    operator parser with operations given in the operators module
    '''
    cinput  = str(input).replace(' ', '')
    result = expr.parse(cinput, operators)
    if result:
        result.removeduplicates()
    else:
        raise expr.CouldNotParse(cinput)
    return result
    

def unwind(cpars, values):
    return cpars.unwind(values, operators.unwind)

def tojson(cpars, values):
    return cpars.json(values, operators.unwind)