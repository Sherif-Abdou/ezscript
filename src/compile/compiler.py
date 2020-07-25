from typing import Union

from src.ast import Extern, Function, FunctionCall, Value, ExpressionType, Return, Types, SetVariable, Variable
from src.parser import Parser
from llvmlite import ir

double = ir.DoubleType()
floating = ir.FloatType()
integer = ir.IntType(32)
void = ir.VoidType()
byte = ir.IntType(8)
boolean = ir.IntType(1)
und = ir.Undefined


class Compiler:
    def __init__(self, file_name: str, parser: Parser):
        self.__file_name = file_name
        self.__parser = parser
        self.__parser.parse()
        self.__root = self.__parser.getTree()
        self.__externals = set()
        self.__functions = {}
        self.__variables = None
        self.module: ir.Module = None

    def compile(self):
        self.module = ir.Module(name=self.__file_name)
        for command in self.__root.commands:
            if type(command) is Extern:
                self.__compile_extern(command)

        for func in self.__root.functions:
            self.__compile_function(func)

    def __compile_function(self, func: Function):
        def compile_args(args):
            arr = []
            for v in args:
                arr.append(self.__toType(v.type))
            return arr

        if func.name in self.__externals:
            return
        self.__variables = {}
        func_type = ir.FunctionType(integer, compile_args(func.args))
        ir_func = ir.Function(self.module, func_type, func.name)
        self.__functions[func.name] = ir_func
        func_block = ir_func.append_basic_block(name="entry")
        builder = ir.IRBuilder(func_block)

        for arg_name, arg in zip(func.args, ir_func.args):
            self.__variables[arg_name.name] = arg

        for command in func.commands:
            if isinstance(command, FunctionCall):
                self.__compile_function_call(builder, command)
            elif isinstance(command, Return):
                value = self.__compile_value(builder, command.value)
                builder.ret(value)
                return
            elif isinstance(command, SetVariable):
                self.__compile_variable(builder, command)
        builder.ret(ir.Constant(byte, 0))

    def __compile_value(self, builder: ir.IRBuilder, value: Value):
        if value.type == ExpressionType.VALUE:
            if isinstance(v := value.value, float):
                return ir.Constant(double, v)
            elif isinstance(v := value.value, int):
                return ir.Constant(integer, v)
            elif isinstance(v := value.value, FunctionCall):
                return self.__compile_function_call(builder, v)
            elif isinstance(v := value.value, Variable):
                return self.__compile_variable(builder, v)
        left = self.__compile_value(builder, value.left)
        right = self.__compile_value(builder, value.right)
        if value.type == ExpressionType.ADD:
            if left.type == right.type == double:
                return builder.fadd(left, right)
            elif left.type == right.type == integer:
                return builder.add(left, right)
        elif value.type == ExpressionType.MINUS:
            if left.type == right.type == double:
                return builder.fsub(left, right)
            elif left.type == right.type == integer:
                return builder.sub(left, right)
        elif value.type == ExpressionType.MULTIPLY:
            if left.type == right.type == double:
                return builder.fmul(left, right)
            elif left.type == right.type == integer:
                return builder.mul(left, right)
        elif value.type == ExpressionType.DIVIDE:
            if left.type == right.type == double:
                return builder.fdiv(left, right)
            elif left.type == right.type == integer:
                return builder.sdiv(left, right)

    def __compile_function_call(self, builder: ir.IRBuilder, c: FunctionCall):
        return builder.call(self.__functions[c.name], [self.__compile_value(builder, arg) for arg in c.args])

    def __compile_variable(self, builder: ir.IRBuilder, c: Union[SetVariable, Variable]):
        if isinstance(c, SetVariable):
            value = self.__compile_value(builder, c.value)
            if c.name not in self.__variables:
                self.__variables[c.name] = builder.alloca(value.type)
            builder.store(value, self.__variables[c.name])
            self.__variables[c.name] = builder.load(self.__variables[c.name])
        elif isinstance(c, Variable):
            p = self.__variables[c.name]
            value = builder.load(p) if p.type.is_pointer else p
            return value

    def __compile_extern(self, extern: Extern):
        if extern.identifier == "abs":
            func_type = ir.FunctionType(integer, (integer,))
            func = ir.Function(self.module, func_type, name="abs")
            self.__functions["abs"] = func
            self.__externals.add("abs")

    def __toType(self, ty: Types):
        if ty == Types.INT:
            return integer
        elif ty == Types.FLOAT:
            return double
        elif ty == Types.BOOL:
            return boolean
        return None
