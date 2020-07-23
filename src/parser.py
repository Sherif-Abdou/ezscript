from src import Lexer, Token
from collections import deque

from src.ast import *
from src.ast.function_call import FunctionCall

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
        self.top = self.que[len(self.que) - 1] if len(self.que)-1 >= 0 else None
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
        while self.__last_token != Token.EOF:
            if self.__last_token == Token.FUN:
                self.__parse_function()
                self.__next()
            elif self.__last_token == Token.IDENTIFIER and self.__funInScope(self.__last_identifier()):
                self.__parse_function_call(self.__last_identifier())
            elif self.__last_token == Token.EXTERN:
                self.__parse_extern()
            elif self.__last_token == Token.END:
                self.__parse_end()
                self.__next()
            else:
                self.__next()

    def __parse_function(self):
        self.__next()
        if self.__last_token != Token.IDENTIFIER:
            raise Exception()
        name = self.__last_identifier()
        self.__next()
        if self.__last_token != Token.EOL:
            raise Exception()
        func = Function(name)
        self.__scope_stack.push(func)

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
        self.__scope_stack.top.commands.append(FunctionCall(identifier, args))

    def __parse_extern(self):
        self.__next()
        if self.__last_token != Token.IDENTIFIER:
            raise Exception()
        identifier = self.__last_identifier()
        self.__next()
        if self.__last_token != Token.EOL:
            raise Exception()
        extern = Extern(identifier)
        self.__root.commands.append(extern)
        self.__root.functions.append(Function(identifier))

    def __parse_assignment(self, name):
        self.__next()
        if self.__last_identifier() != "=":
            raise Exception()
        self.__next()
        value = self.parse_value()

    def parse_value(self):
        tree = Value(None, ExpressionType.PLACEHOLDER)
        op_stack = PeakStack([tree])
        while self.__last_token != Token.CLOSE_PARENTH and self.__last_token != Token.COMMA:
            if self.__last_token == Token.NUMBER:
                val = Value(float(self.__last_identifier()), ExpressionType.VALUE)
                self.__add_value(op_stack, val)
            elif self.__last_token == Token.OPEN_PARENTH:
                self.__next()
                val = self.parse_value()
                self.__add_value(op_stack, val)
            elif self.OPERATOR_EXPS[self.__last_token] in self.OPERATORS:
                operator = self.OPERATOR_EXPS[self.__last_token]
                if op_stack.top.type == ExpressionType.VALUE:
                    temp = op_stack.top
                    op_stack.pop()
                    op_stack.push(Value(self.OPERATOR_STRS[self.__last_token], operator))
                    op_stack.top.left = temp
                elif self.OPERATORS[op_stack.top.type] <= self.OPERATORS[operator]:
                    temp = op_stack.pop()
                    temp2 = op_stack.top
                    op_stack.push(Value(self.OPERATOR_STRS[self.__last_token], operator))
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
