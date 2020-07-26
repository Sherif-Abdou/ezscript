from src import Lexer, Token
from collections import deque

from src.ast import *

PRECEDENCE = {
    "+": 1,
    "-": 2,
    "*": 3,
    "/": 4
}


class PeakStack:
    def __init__(self, arr):
        self.que = deque(arr)
        self.top = arr[len(arr) - 1]

    def push(self, value):
        self.que.append(value)
        self.top = value

    def pop(self):
        value = self.que.pop()
        self.top = self.que[len(self.que) - 1] if len(self.que) - 1 >= 0 else None
        return value

    def __iter__(self):
        for v in self.que:
            yield v


class Parser:
    OPERATORS = {ExpressionType.ADD: 2, ExpressionType.MINUS: 2, ExpressionType.MULTIPLY: 1, ExpressionType.DIVIDE: 1}
    OPERATOR_STRS = {Token.ADD: "+", Token.SUBTRACT: "-", Token.MULTIPLY: "*", Token.DIVIDE: "/"}
    OPERATOR_EXPS = {Token.ADD: ExpressionType.ADD, Token.SUBTRACT: ExpressionType.MINUS,
                     Token.MULTIPLY: ExpressionType.MULTIPLY, Token.DIVIDE: ExpressionType.DIVIDE}

    def __init__(self, lexer: Lexer):
        self.__lexer = lexer
        self.__last_token = self.__lexer.nextToken()
        self.__root_commands = []
        self.__root = Scope(True)
        self.__scope_stack = PeakStack([self.__root])

    def __last_identifier(self):
        return self.__lexer.lastIdentifier()

    def __next(self):
        self.__last_token = self.__lexer.nextToken()

    def getTree(self):
        return self.__root

    def parse(self):
        deref = False
        while self.__last_token != Token.EOF:
            if self.__last_token == Token.FUN:
                self.__parse_function()
                self.__next()
            elif self.__last_token == Token.IDENTIFIER and self.__funInScope(self.__last_identifier()):
                func = self.__parse_function_call(self.__last_identifier())
                self.__scope_stack.top.commands.append(func)
            elif self.__last_token == Token.IDENTIFIER and not self.__funInScope(name := self.__last_identifier()):
                self.__parse_assignment(name, deref)
            elif self.__last_token == Token.RETURN:
                self.__parse_return()
            elif self.__last_token == Token.EXTERN:
                self.__parse_extern()
            elif self.__last_token == Token.END:
                self.__parse_end()
                self.__next()
            elif self.__last_token == Token.MULTIPLY:
                deref = True
                self.__next()
            else:
                self.__next()

    def __parse_type_set(self):
        args = []
        self.__next()
        while self.__last_token != Token.CLOSE_PARENTH:
            if len(args) > 0 and self.__last_token != Token.COMMA:
                raise Exception()
            elif len(args) > 0:
                self.__next()
            if self.__last_token != Token.IDENTIFIER:
                raise Exception()
            iden = self.__last_identifier()
            self.__next()
            if self.__last_token != Token.COLON:
                raise Exception()
            self.__next()
            if self.__last_token != Token.IDENTIFIER:
                raise Exception()
            ty = Types.from_identifier(self.__last_identifier())
            args.append(Variable(iden, ty))
            self.__next()

        return args

    def __parse_function(self):
        self.__next()
        if self.__last_token != Token.IDENTIFIER:
            raise Exception()
        name = self.__last_identifier()
        self.__next()
        if self.__last_token != Token.OPEN_PARENTH:
            raise Exception()
        args = self.__parse_type_set()
        self.__next()
        ret = self.__get_return()
        self.__next()
        func = Function(name, args, ret)
        self.__scope_stack.push(func)

    def __get_return(self):
        ret = None
        if self.__last_token == Token.COLON:
            self.__next()
            if self.__last_token != Token.IDENTIFIER:
                raise Exception
            ret = Types.from_identifier(self.__last_identifier())
        return ret

    def __parse_return(self):
        self.__next()
        if self.__last_token != Token.IDENTIFIER:
            raise Exception()
        va = self.parse_value()
        self.__scope_stack.top.commands.append(Return(va))

    def __parse_end(self):
        full_scope = self.__scope_stack.pop()
        if type(full_scope) == Function:
            self.__scope_stack.top.functions.append(full_scope)

    def __parse_function_call(self, identifier):
        self.__next()
        if self.__last_token != Token.OPEN_PARENTH:
            raise Exception()

        self.__next()
        args = []
        while self.__last_token != Token.CLOSE_PARENTH:
            value = self.parse_value()
            args.append(value)
            if self.__last_token == Token.COMMA:
                self.__next()
        return FunctionCall(identifier, args)

    def __parse_extern(self):
        self.__next()
        if self.__last_token != Token.IDENTIFIER:
            raise Exception()
        identifier = self.__last_identifier()
        self.__next()
        if self.__last_token != Token.OPEN_PARENTH:
            raise Exception()
        args = self.__parse_type_set()
        self.__next()
        ret = self.__get_return()
        self.__next()
        func = Function(identifier, args, ret)
        extern = Extern(identifier, func)
        self.__root.commands.append(extern)
        self.__root.functions.append(func)

    def __parse_assignment(self, identifier, deref=False):
        self.__next()
        ty = None
        if self.__last_token == Token.COLON:
            self.__next()
            if self.__last_token != Token.IDENTIFIER:
                raise Exception()
            iden = self.__last_token
            ty = Types.from_identifier(iden)

        elif self.__last_identifier() != "=":
            raise Exception()
        self.__next()
        value = self.parse_value()
        if not self.__varInScope(identifier):
            if ty is None:
                ty = self.__typeOf(value)
            variable = Variable(identifier, ty)
            self.__scope_stack.top.variables.append(variable)
        set_var = SetVariable(identifier, value, deref)
        self.__scope_stack.top.commands.append(set_var)

    def __typeOf(self, v: Value):
        if v.type in {ExpressionType.VALUE, ExpressionType.REFERENCE, ExpressionType.DEREFERENCE}:
            if isinstance(v.value, int):
                return Types.INT
            elif isinstance(v.value, float):
                return Types.FLOAT
            elif isinstance(v.value, Variable):
                return v.value.type
        else:
            if ty := self.__typeOf(v.left) is not None:
                return ty
            if ty := self.__typeOf(v.right) is not None:
                return ty
        return None

    def parse_value(self):
        tree = Value(None, ExpressionType.PLACEHOLDER)
        negate = False
        ref = False
        deref = False
        op_stack = PeakStack([tree])
        while self.__last_token != Token.CLOSE_PARENTH and self.__last_token != Token.COMMA and self.__last_token != Token.EOL:
            if self.__last_token == Token.NUMBER:
                integer = int(self.__last_identifier())
                if negate:
                    integer *= -1
                    negate = False
                val = Value(integer, ExpressionType.VALUE)
                self.__add_value(op_stack, val)
            elif self.__last_token == Token.OPEN_PARENTH:
                self.__next()
                val = self.parse_value()
                self.__add_value(op_stack, val)
            elif self.__last_token == Token.IDENTIFIER and self.__funInScope(iden := self.__last_identifier()):
                value = self.__parse_function_call(iden)
                val = None
                if negate:
                    val = Value("*", ExpressionType.MULTIPLY)
                    val.left = Value(-1, ExpressionType.VALUE)
                    val.right = Value(value, ExpressionType.VALUE)
                    negate = False
                else:
                    val = Value(value, ExpressionType.VALUE)
                self.__add_value(op_stack, val)
            elif self.__last_token == Token.IDENTIFIER and self.__varInScope(iden := self.__last_identifier()):
                variable = self.__getVar(iden)
                val = None
                if negate:
                    val = Value("*", ExpressionType.MULTIPLY)
                    val.left = Value(-1, ExpressionType.VALUE)
                    val.right = Value(variable, ExpressionType.VALUE)
                    negate = False
                elif deref:
                    val = Value(variable, ExpressionType.DEREFERENCE)
                    deref = False
                elif ref:
                    val = Value(variable, ExpressionType.REFERENCE)
                    ref = False
                else:
                    val = Value(variable, ExpressionType.VALUE)

                self.__add_value(op_stack, val)
            elif self.__last_token == Token.REF and op_stack.top.type == ExpressionType.PLACEHOLDER:
                ref = True
            elif self.OPERATOR_EXPS[self.__last_token] in self.OPERATORS:
                operator = self.OPERATOR_EXPS[self.__last_token]
                if op_stack.top.type == ExpressionType.VALUE:
                    temp = op_stack.top
                    op_stack.pop()
                    op_stack.push(Value(self.OPERATOR_STRS[self.__last_token], operator))
                    op_stack.top.left = temp
                elif op_stack.top.type == ExpressionType.PLACEHOLDER and operator == ExpressionType.MINUS:
                    negate = True
                elif op_stack.top.type == ExpressionType.PLACEHOLDER and operator == ExpressionType.MULTIPLY:
                    deref = True
                elif self.OPERATORS[op_stack.top.type] <= self.OPERATORS[operator]:
                    temp = op_stack.pop()
                    temp2 = op_stack.top
                    op_stack.push(Value(self.OPERATOR_STRS[self.__last_token], operator))
                    if temp2 is not None:
                        if temp2.left is temp:
                            temp2.left = op_stack.top
                        elif temp2.right is temp:
                            temp2.right = op_stack.top
                    op_stack.top.left = temp
                    op_stack.push(temp)
                elif self.OPERATORS[op_stack.top.type] > self.OPERATORS[operator]:
                    first_val = op_stack.top.right
                    op_stack.top.right = None
                    new_val = Value(self.OPERATOR_STRS[self.__last_token], operator)
                    op_stack.top.right = new_val
                    op_stack.push(new_val)
                    op_stack.top.left = first_val
            self.__next()

        return op_stack.que[0]

    def __add_value(self, op_stack, val):
        while len(op_stack.que) > 0:
            if op_stack.top is None or op_stack.top.type == ExpressionType.PLACEHOLDER:
                op_stack.top.type = ExpressionType.VALUE
                if val.type == ExpressionType.REFERENCE or val.type == ExpressionType.DEREFERENCE:
                    op_stack.top.type = val.type
                op_stack.top.value = val.value
                break
            elif op_stack.top.left is None and op_stack.top.type != ExpressionType.VALUE:
                op_stack.top.left = val
                break
            elif op_stack.top.right is None and op_stack.top.type != ExpressionType.VALUE:
                op_stack.top.right = val
                break
            else:
                op_stack.pop()

    def __funInScope(self, identifier):
        for s in self.__scope_stack:
            for fun in s.functions:
                if fun.name == identifier:
                    return True
        return False

    def __varInScope(self, identifier):
        for s in self.__scope_stack:
            for var in s.variables:
                if var.name == identifier:
                    return True
        return False

    def __getVar(self, identifier):
        for s in self.__scope_stack:
            for var in s.variables:
                if var.name == identifier:
                    return var
        return None
