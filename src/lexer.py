from collections import deque

from src.token import Token


class Lexer:
    def __init__(self, text: str):
        self.__text = text
        self.__que = deque(text)
        self.__identifier = ""

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
            c = self.__que.popleft()

        identifier = ""
        while c.isalnum():
            identifier += c
            if len(self.__que) == 0:
                break
            c = self.__que.popleft()

        self.__identifier = identifier
        if identifier == "fun":
            return Token.FUN
        elif identifier == "extern":
            return Token.EXTERN
        elif identifier.isnumeric():
            return Token.NUMBER
        else:
            return Token.IDENTIFIER
