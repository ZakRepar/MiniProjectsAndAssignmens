# COMP 3200 -- Recursive-descent calculator

import re

# --- lexer (lexical analyzer, or scanner) ---

class Lexer:
    ignore = re.compile(r'[ \t]+') # spaces and tabs

    rules = [
        (re.compile(r'[0-9]+'),     lambda s: int(s)),              # integer literals
        (re.compile(r'[a-zA-Z]+'),  lambda s: s),                   # variables
        (re.compile(r'[+\-*/^()]'), lambda s: s),                   # single char operators
        (re.compile(r'.'),          lambda s: '#' + str(ord(s))),   # otherwise, error
        ]

    def __init__(self, input_string):
        self.s = input_string
        self.pos = 0

    def next(self):
        # skip over ignorable characters
        m = self.ignore.match(self.s, self.pos)
        if m: self.pos = m.end()

        if self.pos >= len(self.s):
            return '$'      # denotes end of input

        for rule in self.rules:
            r, f = rule
            m = r.match(self.s, self.pos)
            if m:
                self.pos = m.end()
                return f(m.group())


# --- parse error exception ---

class ParseError(Exception):
    def __init__(self, message):
        self.message = message


# --- parser (syntax analyzer): returns an AST ---

class Parser:
    def __init__(self, input_string):
        self.lexer = Lexer(input_string)
        self.next()


    def error(self, message):
        raise ParseError(message + ' [next token: ' + str(self.tok) + ']')


    def next(self):
        self.tok = self.lexer.next()


    def parse(self):
        """ input : expr '$' """

        e = self.parse_expr()
        if self.tok == '$':
            return e
        else:
            self.error('extraneous input')


    def parse_expr(self):
        """ expr ::= mul_expr {(+|-) mul_expr} """

        e = self.parse_mul()
        while self.tok in ('+', '-'):
            t = self.tok      # remember operator
            self.next()
            e = (t, e, self.parse_mul())
        return e


    def parse_mul(self):
        """ mul_expr ::= neg_expr {(*|/) neg_xpr} """

        e = self.parse_neg()
        while self.tok in ('*', '/'):
            t = self.tok
            self.next()
            e = (t, e, self.parse_neg())
        return e


    def parse_neg(self):
        """ neg_expr ::= - neg_expr | pow_expr """

        if self.tok == '-':
            self.next()
            return ('neg', self.parse_neg())
        else:
            return self.parse_pow()


    def parse_pow(self):
        """ pow_expr ::= factor [^ pow_expr] """

        e = self.parse_factor()
        if self.tok == '^':
            self.next()
            e = ('^', e, self.parse_pow())
        return e


    def parse_factor(self):
        """ factor ::= int | id | '(' expr ')' """

        if isinstance(self.tok, int):
            n = self.tok
            self.next()
            return n
        elif self.tok.isalpha():
            var = self.tok
            self.next()
            return var
        elif self.tok == '(':
            self.next()
            e = self.parse_expr()
            if self.tok != ')':
                self.error('missing )')
            else:
                self.next()
            return e
        else:
            self.error("expected int or '('")


# --- postorder AST walker ---

VARS = {}   # dictionary of variables

def assign(v, value):
    VARS[v] = value
    return value

eval_op = {
    '+'  : lambda x,y: eval(x) + eval(y),
    '-'  : lambda x,y: eval(x) - eval(y),
    '*'  : lambda x,y: eval(x) * eval(y),
    '/'  : lambda x,y: eval(x) // eval(y),
    '^'  : lambda x,y: eval(x) ** eval(y),
    'neg': lambda x: -eval(x),
    }

def eval(e):
    if isinstance(e, int):
        return e
    elif isinstance(e, str):
        return VARS.get(e, 0) # second arg is default return value if key not in dict
    else:
        return eval_op[e[0]](*e[1:]) # pass remaining elements as parameters


# --- main calculator function ---

def calc(line):
    return eval(Parser(line).parse())


# --- scaffolding for interactive testing ---

if __name__ == '__main__':
    while True:
        try:
            line = input('calc> ')
        except EOFError:
            break

        if line == '' or line.isspace(): break

        try:
            e = Parser(line).parse()
            print('\tAST:', e)
            print(eval(e))
        except ParseError as err:
            print('parse error:', err.message)
            
