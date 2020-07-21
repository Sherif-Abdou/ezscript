import unittest
from src import Token, Lexer


class MyTestCase(unittest.TestCase):
    def test_lexer_fun(self):
        text = """
        fun num:
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


if __name__ == '__main__':
    unittest.main()
