from collections import deque

from src.token import Token


class Lexer:
    def __init__(self, text: str):
        self.__text = text
        self.__que = deque(text)
        self.__identifier = ""
        self.__special_chars = {"(": Token.OPEN_PARENTH, ")": Token.CLOSE_PARENTH, ",": Token.COMMA,
                                "+": Token.ADD, "-": Token.SUBTRACT, "*": Token.MULTIPLY, "/": Token.DIVIDE}

    def lastIdentifier(self):
        return self.__identifier

    def nextToken(self):
        if len(self.__que) == 0:
            return Token.EOF

        c: str = self.__que.popleft()
        while c.isspace() and len(c) > 0:
            if c == "\n":
                self.__identifier = c
                return Token.EOL
            if len(self.__que) == 0:
                return Token.EOF
            c = self.__que.popleft()

        if c in self.__special_chars:
            self.__identifier = c
            return self.__special_chars[c]
        identifier = ""
        while c.isalnum():
            if c in self.__special_chars:
                self.__identifier = c
                return self.__special_chars[c]
            identifier += c
            if len(self.__que) == 0:
                break
            c = self.__que.popleft()
        else:
            self.__que.appendleft(c)

        self.__identifier = identifier
        if identifier == "fun":
            return Token.FUN
        elif identifier == "extern":
            return Token.EXTERN
        elif identifier == "end":
            return Token.END
        elif identifier.isnumeric():
            return Token.NUMBER
        else:
            return Token.IDENTIFIER
