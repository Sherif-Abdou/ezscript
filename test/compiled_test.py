import unittest

from src import Lexer, Parser
from src.compile import Compiler
from src.compile.runner import run


class CompileCases(unittest.TestCase):
    def test_compile(self):
        raw_str = ""
        with open("../test_file.ez") as f:
            raw_str = f.read()
        parser = Parser(Lexer(raw_str))
        compiler = Compiler("test_file", parser)
        run(compiler)


if __name__ == '__main__':
    unittest.main()
