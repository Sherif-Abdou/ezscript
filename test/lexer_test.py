import unittest
from src import Token, Lexer
from src.parser import Parser


class MyTestCase(unittest.TestCase):
    def test_lexer_fun(self):
        text = """
        fun num()
            print("hello world")
        end
        """
        lexer = Lexer(text)
        token = lexer.nextToken()
        self.assertEqual(token, Token.EOL)
        self.assertEqual(lexer.lastIdentifier(), "\n")
        token = lexer.nextToken()
        self.assertEqual(token, Token.FUN)
        self.assertEqual(lexer.lastIdentifier(), "fun")

    def test_lexer_number(self):
        text = """123"""
        lexer = Lexer(text)
        token = lexer.nextToken()
        self.assertEqual(token, Token.NUMBER)
        self.assertEqual(lexer.lastIdentifier(), "123")

    # def test_expression(self):
    #     text = """
    #     extern printf
    #
    #     fun main()
    #         printf(12+3*2+10)
    #     end
    #     """
    #     lexer = Lexer(text)
    #     parser = Parser(lexer)
    #     parser.parse()
    #     functions = parser.getTree().functions[1].commands[0].args
    #     # print(functions)


if __name__ == '__main__':
    unittest.main()
