# http://lukaszwrobel.pl/blog/math-parser-part-3-implementation

class Token(object):
    Plus        = 0
    Minus       = 1
    Multiply    = 2
    Divide      = 3

    Number      = 4

    LParen      = 5
    RParen      = 6

    End         = 7

    symbols = {
        "+": Plus,
        "-": Minus,
        "*": Multiply,
        "/": Divide,
        "(": LParen,
        ")": RParen,
        "": End,
    }
    numbers = ("0","1","2","3","4","5","6","7","8","9")


    def __init__(self):
        self.kind = None
        self.value = None

    def is_unknown(self):
        return self.kind is None



class Lexer(object):
    def __init__(self, input_string):
        self.input_string = input_string.strip()
        self.return_previous_token = False
        self.previous_token = None

    def get_next_token(self):
        if self.return_previous_token:
            self.return_previous_token = False
            return self.previous_token

        token = Token()

        token.kind, self.input_string = self.read_token()
        print("Token {}".format(token.kind))
        if token.is_unknown():
            print('Unknown Token')

        self.previous_token = token
        return token

    def read_token(self):
        matcher = ""
        kind = None

        for idx, lt in enumerate(self.input_string):
            matcher += lt
            if matcher in Token.numbers:
                next_char = self.input_string[idx+1]
                while next_char in Token.numbers:
                    matcher += matcher
                    next_char = self.input_string[idx+1]
                kind = Token.Number
                break
            elif matcher in Token.symbols:
                kind = Token.symbols[matcher]
                break

        if kind is None:
            return kind, self.input_string
        else:
            return kind, self.input_string[len(matcher):]

    def revert(self):
        self.return_previous_token = True

class Parse(object):
    def __init__(self, input_string):
        self.lexer = Lexer(input_string)

        expression_value = self.expression()

        token = self.lexer.get_next_token()
        if token == Token.End:
            return expression_value
        else:
            print('End Expected')

    def expression(self):
        component1 = self.factor()

        additive_operators = [Token.Plus, Token.Minus]

        token = self.lexer.get_next_token()

        while token.kind in additive_operators:
            component2 = self.factor()

            if token.kind == Token.Plus:
                component1 += component2
            else:
                component1 -= component2

            token = self.lexer.get_next_token()

        self.lexer.revert()

        return component1

    def factor(self):
        factor1 = self.number

        multiplicative_operators = [Token.Multiply, Token.Divide]

        token = self.lexer.get_next_token()
        while token.kind in multiplicative_operators:
            factor2 = self.number()

            if token.kind == Token.Multiply:
                factor1 *= factor2
            else:
                factor1 /= factor2

            token = self.lexer.get_next_token()

        self.lexer.revert()

        return factor1

    def number(self):
        token = self.lexer.get_next_token()

        if token.kind == Token.LParen:
            value = self.expression()

            expected_rparen = self.lexer.get_next_token()
            if expected_rparen != token.RParen:
                print('Unbalanced parenthesis')
        elif token.kind == token.Number:
            value = token.value
        else:
            print('Not a number')

        return value

expression = input("Equation? ")
print(Parse(expression))