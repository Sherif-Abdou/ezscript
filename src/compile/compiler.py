from src.ast import Extern, Function, FunctionCall, Value, ExpressionType, Return
from src.parser import Parser
from llvmlite import ir

double = ir.DoubleType()
floating = ir.FloatType()
integer = ir.IntType(32)
void = ir.VoidType()
byte = ir.IntType(8)
und = ir.Undefined


class Compiler:
    def __init__(self, file_name: str, parser: Parser):
        self.__file_name = file_name
        self.__parser = parser
        self.__parser.parse()
        self.__root = self.__parser.getTree()
        self.__externals = set()
        self.__functions = {}
        self.module: ir.Module = None

    def compile(self):
        self.module = ir.Module(name=self.__file_name)
        for command in self.__root.commands:
            if type(command) is Extern:
                self.__compile_extern(command)

        for func in self.__root.functions:
            self.__compile_function(func)

    def __compile_function(self, func: Function):
        if func.name in self.__externals:
            return
        func_type = ir.FunctionType(integer, ())
        ir_func = ir.Function(self.module, func_type, func.name)
        func_block = ir_func.append_basic_block(name="entry")
        builder = ir.IRBuilder(func_block)

        for command in func.commands:
            if isinstance(command, FunctionCall):
                self.__compile_function_call(builder, command)
            elif isinstance(command, Return):
                builder.ret(self.__compile_value(builder, command.value))
                return
        builder.ret(ir.Constant(byte, 0))

    def __compile_value(self, builder: ir.IRBuilder, value: Value):
        if value.type == ExpressionType.VALUE:
            if isinstance(v := value.value, float):
                return ir.Constant(double, v)
            elif isinstance(v := value.value, int):
                return ir.Constant(integer, v)
            elif isinstance(v := value.value, FunctionCall):
                return self.__compile_function_call(builder, v)
        left = self.__compile_value(builder, value.left)
        right = self.__compile_value(builder, value.right)
        if value.type == ExpressionType.ADD:
            if left.type == right.type == double:
                return builder.fadd(left, right)
            elif left.type == right.type == integer:
                return builder.add(left, right)

    def __compile_function_call(self, builder: ir.IRBuilder, c: FunctionCall):
        return builder.call(self.__functions[c.name], [self.__compile_value(builder, arg) for arg in c.args])

    def __compile_extern(self, extern: Extern):
        if extern.identifier == "abs":
            func_type = ir.FunctionType(integer, (integer,))
            func = ir.Function(self.module, func_type, name="abs")
            self.__functions["abs"] = func
            self.__externals.add("abs")
