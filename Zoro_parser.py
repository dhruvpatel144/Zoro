from dataclasses import dataclass
from dataTypeDeclaration import *
from lexer import *

class SOMETHING: pass

@dataclass
class Stream:
    source: str
    pos: int

    def from_string(s): 
        return Stream(s,0)
    def next_char(self): 
        if self.pos >= len(self.source): raise SOMETHING()
        self.pos = self.pos + 1
        return self.source[self.pos - 1]
    def unget(self):
        assert self.pos > 0
        self.pos = self.pos - 1



@dataclass
class ApnaParser:
    lexer: Lexer

    def from_lexer(lexer): return ApnaParser(lexer)
    def parse_var(self): pass
    
    def parse_expr(self):
        match self.lexer.peek_token():
            case Keyword("if"): return self.parse_if()
            case _: return self.parse_BASE() 	

    def parse_if(self):
        conds=[]; seqs=[]; 
        self.lexer.match(Keyword("if"))
        cond = self.parse_expr()
        conds.append(cond)
        self.lexer.match(Keyword("then"))
        seq = self.parse_expr()
        seqs.append(seq)

        while True:
            match self.lexer.peek_token():
                case Keyword("elif"):
                    self.lexer.match(Keyword("elif"))
                    cond = self.parse_expr()
                    conds.append(cond)
                    self.lexer.match(Keyword("then"))
                    seq = self.parse_expr()
                    seqs.append(seq)

                case Keyword("else"):
                    self.lexer.match(Keyword("else"))
                    seq = self.parse_expr()
                    seqs.append(seq)
                    self.lexer.match(Keyword("endif"))
                    break
        
        """ ############## typecheck ############### """
        return If(conds,seqs)

    def parse_BASE(self): 
        return self.parse_rassi()
    
    def parse_atom(self):
        match self.lexer.peek_token():
            case Identifier(name):  self.lexer.advance(); return Variable(name); 
            case Int(value):        self.lexer.advance(); return Int(value); 
            case Bool(value):       self.lexer.advance(); return Bool(value); 

    def parse_exp(self):
        left = self.parse_atom()
        while True:
            match self.lexer.peek_token():
                case Operator("**"):
                    self.lexer.advance()
                    m = self.parse_atom()
                    left = BinOp("**", left, m)
                case _: break
        return left

    def parse_neg(self):
        while True:
            match self.lexer.peek_token():
                case Operator("-"):
                    self.lexer.advance()
                    return -(self.parse_expr())
                case _:	
                    return self.parse_exp()

    def parse_mul(self):
        left = self.parse_neg()
        while True:
            match self.lexer.peek_token():
                case Operator(op) if op in (" * / // % ".split()):
                    self.lexer.advance()
                    m = self.parse_atom()
                    left = BinOp(op, left, m)
                case _: break
        return left

    def parse_add(self):
        left = self.parse_mul()
        while True:
            match self.lexer.peek_token():
                case Operator(op) if op in (" + - ".split()):
                    self.lexer.advance()
                    m = self.parse_mul()
                    left = BinOp(op, left, m)
                case _: break
        return left

    def parse_shift(self):
        left = self.parse_add()
        while True:
            match self.lexer.peek_token():
                case Operator(op) if op in (" >> << ".split()):
                    self.lexer.advance()
                    m = self.parse_atom()
                    left = BinOp(op, left, m)
                case _: break
        return left

    def parse_bnot(self):
        while True:
            match self.lexer.peek_token():
                case Operator("~"):
                    self.lexer.advance()
                    return ~(self.parse_expr())	
                case _:	
                    return self.parse_shift()

    def parse_band(self):
        left = self.parse_bnot()
        while True:
            match self.lexer.peek_token():
                case Operator("&"):
                    self.lexer.advance()
                    m = self.parse_bnot()
                    left = BinOp("&", left, m)
                case _: break
        return left

    def parse_bxor(self):
        left = self.parse_band()
        while True:
            match self.lexer.peek_token():
                case Operator("^"):
                    self.lexer.advance()
                    m = self.parse_band()
                    left = BinOp("^", left, m)
                case _: break
        return left

    def parse_bor(self):
        left = self.parse_bxor()
        while True:
            match self.lexer.peek_token():
                case Operator("|"):
                    self.lexer.advance()
                    m = self.parse_bxor()
                    left = BinOp("|", left, m)
                case _: break
        return left

    def parse_cmp(self):
        left = self.parse_bor()
        match self.lexer.peek_token():
            case Operator(op) if op in (" < > <= >= == != ".split()):
                self.lexer.advance()
                right = self.parse_bor()
                return BinOp(op, left, right)
        return left

    def parse_lnot(self):
        left = self.parse_cmp()
        while True:
            match self.lexer.peek_token():
                case Keyword("not"):
                    self.lexer.advance()
                    m = self.parse_cmp()
                    left = BinOp("not", left, m)
                case _: break
        return left

    def parse_lnand(self):
        left = self.parse_lnot()
        while True:
            match self.lexer.peek_token():
                case Keyword("nand"):
                    self.lexer.advance()
                    m = self.parse_lnot()
                    left = BinOp("nand", left, m)
                case _: break
        return left

    def parse_land(self):
        left = self.parse_lnand()
        while True:
            match self.lexer.peek_token():
                case Keyword("and"):
                    self.lexer.advance()
                    m = self.parse_lnand()
                    left = BinOp("and", left, m)
                case _: break
        return left

    def parse_lxnor(self):
        left = self.parse_land()
        while True:
            match self.lexer.peek_token():
                case Keyword("xnor"):
                    self.lexer.advance()
                    m = self.parse_land()
                    left = BinOp("xnor", left, m)
                case _: break
        return left

    def parse_lxor(self):
        left = self.parse_lxnor()
        while True:
            match self.lexer.peek_token():
                case Keyword("xor"):
                    self.lexer.advance()
                    m = self.parse_lxnor()
                    left = BinOp("xor", left, m)
                case _: break
        return left

    def parse_lnor(self):
        left = self.parse_lxor()
        while True:
            match self.lexer.peek_token():
                case Keyword("nor"):
                    self.lexer.advance()
                    m = self.parse_lxor()
                    left = BinOp("nor", left, m)
                case _: break
        return left

    def parse_lor(self):
        left = self.parse_lnor()
        while True:
            match self.lexer.peek_token():
                case Keyword("or"):
                    self.lexer.advance()
                    m = self.parse_lnor()
                    left = BinOp("or", left, m)
                case _: break
        return left

    def parse_lassi(self):
        left = self.parse_var()
        match self.lexer.peek_token():
            case Operator("<-"):
                self.lexer.advance()
                m = self.parse_lor()
                left = BinOp("<-", left, m)
        return left

    def parse_rassi(self):
        left = self.parse_lor()
        match self.lexer.peek_token():
            case Operator("->"):
                self.lexer.advance()
                m = self.parse_var()
                right = BinOp("->", left, m)
                return right
        return left




print("\n")

def test_parse():
    def parse(string): return ApnaParser.parse_expr( ApnaParser.from_lexer( Lexer.from_stream(Stream.from_string(string)) ) )

    # print(parse("a"))
    # print(parse("m*6*b"))
    # print(parse("this_vAr1_is_var <= 2"))
    # print(parse("_this_vAr1_is_var <= 2"))
    # print(parse("1+2**6-8//4+7/9"))
    # print(parse("a*5-9<<1^6+~a**6 >= m&6%4/5//8-6+!2"))

test_parse()
print("\n")











'''

import re
var_pattern = "^[_a-zA-z][a-zA-Z0-9_]*$" 
x = re.match(var_pattern, str) 

unary: ! - ~ 
arithmetic: + - * / // % ** 
comparison: > < >= <= == !=  
shift: >> << 
logical : and or not xor xnor nand nor 
bitwise: ~ & | ^ 
assignment: <- -> 

Literals = dtypes 
atom = Literals | var_pattern | expr 

exp = atom | atom**exp 
neg = exp | -neg 
mul = neg | mul * neg | mul / neg | mul // neg | mul % neg 
add = mul | add + mul | add - mul 

shift = add | add >> shift | add << shift 
bnot = shift | ~bnot 
band = bnot | bnot & band 
bxor = band | band ^ bxor 
bor = bxor | "bxor | bor "

comp = bor | bor < bor | bor > bor | bor <= bor | bor >= bor | bor == bor | bor != bor  

lnot = comp | not(lnot) 
lnand = lnot | lnot "nand" lnand 
land = lnand | lnand "and" land 
lxnor = land | land "xnor" lxnor 
lxor = lxnor | lxnor "xor" lxor 
lnor = lxor | lxor "nor" lnor 
lor = lnor | lnor "or" lor 

assi = var <- lor | lor -> var 

'''
