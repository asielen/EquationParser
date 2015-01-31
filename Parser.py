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
    numbers = ("0","1","2","3","4","5","6","7","8","9",".")
    negative = "-"
    space = " "


    def __init__(self):
        self.kind = None
        self.value = None
        self.negate = False

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

        token, self.input_string = self.read_token(token)
        # print("Token: {} / Value: {}".format(token.kind, token.value))
        if token.is_unknown(): raise SyntaxError('Unknown Token')

        self.previous_token = token
        return token

    def read_token(self, token):
        num_match = ''
        match_len = 0

        if len(self.input_string) == 0:
            token.kind = Token.End
        else:
            for idx, lt in enumerate(self.input_string):
                match_len += 1

                #Deal with negatives
                if token.kind is None and lt == Token.negative and len(self.input_string) > 1 \
                        and self.previous_token and self.previous_token.kind != Token.Number \
                        and self.previous_token.kind != Token.RParen:
                    # If isn't already a number
                    # If it is negative sign
                    # And it isn't the last character (that would be an error)
                    # If there is a previous character
                    # And the previous character wasn't a number, like 5-(5)

                    if self.input_string[idx+1] in Token.numbers+("(", " "):
                        token.negate = True
                        continue # look at the next character. Not needed explicitly but helps me know what i am doing
                    else:
                        raise SyntaxError("Improper '-'")

                elif lt == Token.space:
                    continue

                elif lt in Token.numbers:
                    token.kind = Token.Number
                    num_match += lt

                elif token.is_unknown():
                    if lt in Token.symbols:
                        token.kind = Token.symbols[lt]
                        break
                    else:
                        raise SyntaxError('Unknown Symbol: {}'.format(lt))
                else:
                    match_len -= 1
                    break

        if token.kind is Token.Number:
            token.value = self.to_num(num_match)
        if token.negate: print("NEGATE")
        # print("In '{}': Matching '{}'".format(self.input_string, self.input_string[:match_len]))

        if token.kind is None:
            return token, self.input_string
        else:
            return token, self.input_string[match_len:]

    def to_num(self, s):
        try:
            return int(s)
        except ValueError:
            return float(s)

    def revert(self):
        self.return_previous_token = True


def Parse(input_string):
    c_lexer = Lexer(input_string)

    def expression():
        component1 = factor()

        additive_operators = [Token.Plus, Token.Minus]

        token = c_lexer.get_next_token()
        while token.kind in additive_operators:
            component2 = factor()
            if token.kind == Token.Plus:
                component1 += component2
            else:
                component1 -= component2

            token = c_lexer.get_next_token()

        c_lexer.revert()
        if token.negate is True: component1 *= -1
        return component1

    def factor():
        factor1 = number()

        multiplicative_operators = [Token.Multiply, Token.Divide]

        token = c_lexer.get_next_token()
        while token.kind in multiplicative_operators:
            factor2 = number()
            if token.kind == Token.Multiply:
                factor1 *= factor2
            else:
                factor1 /= factor2

            token = c_lexer.get_next_token()

        c_lexer.revert()
        if token.negate is True: factor1 *= -1
        return factor1

    def number():
        value = None
        token = c_lexer.get_next_token()

        if token.kind == Token.LParen:
            value = expression()
            expected_rparen = c_lexer.get_next_token()
            if expected_rparen.kind != token.RParen: raise SyntaxError('Unbalanced parenthesis')

        elif token.kind == token.Number: value = token.value
        else: raise SyntaxError('Not a number: Token {} / Value {}'.format(token.kind, token.value))

        if token.negate is True: value *= -1

        return value

    expression_value = expression()

    c_token = c_lexer.get_next_token()
    if c_token.kind == Token.End:
        return expression_value
    else:
        raise SyntaxError('End Expected')

def solve(string):
    return Parse(string)

if __name__ == "__main__":
    while True:
        expression = input("Equation? ")
        print(Parse(expression))