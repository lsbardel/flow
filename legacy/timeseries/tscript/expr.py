
from language import *        

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression EQUAL expression
                  | expression CONCAT expression
                  | expression SPLIT expression'''
    v = p[2]
    if v == '+':
        p[0] = PlusOp(p[1],p[3])
    elif v == '-':
        p[0] = MinusOp(p[1],p[3])
    elif v == '*':
        p[0] = MultiplyOp(p[1],p[3])
    elif v == '/':
        p[0] = DivideOp(p[1],p[3])
    elif v == '=':
        p[0] = EqualOp(p[1],p[3])
    elif v == concat_operator:
        p[0] = ConcatenationOp(p[1],p[3])
    elif v == separator_operator:
        p[0] = SplittingOp(p[1],p[3])
    elif v == field_operator:
        p[0] = Id(p[1], field = p[3])
        

def p_expression_group(p):
    '''expression : LPAREN expression RPAREN
                  | LSQUARE expression RSQUARE'''
    v = p[1]
    if v == '(':
        p[0] = functionarguments(p[2])
    elif v == '[':
        p[0] = tsentry(p[2])

def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = Number(p[1])
    
def p_expression_id(p):
    '''expression : ID'''
    p[0] = Id(p[1])
    
def p_expression_string(p):
    '''expression : QUOTE expression QUOTE'''
    p[0] = String(p[2])
    
def p_expression_function(p):
    '''expression : FUNCTION LPAREN expression RPAREN'''
    func = p[1]
    p[0] = Function(p[1],p[3],p[2],p[4])
    
def p_expression_bad_function(p):
    '''expression : ID LPAREN expression RPAREN'''
    raise FunctionDoesNotExist(str(p[1]))

def p_error(p):
    pass
    


def parse(input, oper = None, method = 'SLR'):
    from language import rules
    from ply import yacc
    
    ru = rules(oper)
    ru.build()
    ru.input(str(input).lower())
    tokens     = ru.tokens
    precedence = ru.precedence
    yacc       = yacc.yacc(method = method)
    return yacc.parse(lexer = ru.lexer)


if __name__ == '__main__':
    from createts import createts    
    while 1:
        try:
            s = raw_input('calc > ')
        except EOFError:
            break
        if not s:
            continue
        result = parse(s)
        #ts = createts(result)
        print result