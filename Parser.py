# Project Description:
# For fun I decided to try to port a general equation parser from Ruby to Python to learn the theory behind it
# I had never looked at or used Ruby before so that was a learning experience in itself.
# This was also my first dive into unit tests
# Project time: ~8 hours over two days (1/30/15)
#
# Project Overview:
# The original one supported toe following syntax:
#   Addition, Subtraction, Multiplication, and Parentheses
# I added some new features:
#   power ^, mod %, and the ability to extend the functionality with functions f(x,y)
#   Current supported functions: square root <sqrt(x)>; power <pow(x,y)>, log <log(x,y)>
#
# Here is the original Ruby source it is based on.
# http://lukaszwrobel.pl/blog/math-parser-part-3-implementation

import math
class Token(object):
    Number      = 0

    # Basic Functions
    Plus        = 1
    Minus       = 2
    Multiply    = 3
    Divide      = 4
    Mod         = 5
    Power       = 6

    #Any non inline function (not axb but rather func(a,b))
    Function    = 10

    LParen      = 50
    RParen      = 51

    End         = 99


    base_symbols = {
        "+": Plus,
        "-": Minus,
        "*": Multiply,
        "/": Divide,
        "%": Mod,
        "^": Power,
        "(": LParen,
        ")": RParen,
        "": End,
    }

    a_functions = ("l", "s", "p")
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
                if (token.kind is None and lt == Token.negative and len(self.input_string) > 1) and \
                        (not self.previous_token or
                             (self.previous_token and self.previous_token.kind != Token.Number and self.previous_token.kind != Token.RParen)):
                    # If isn't already a number
                    # If it is negative sign
                    # And it isn't the last character (that would be an error)
                    # If there is a previous character
                    # And the previous character wasn't a number, like 5-(5)

                    if self.input_string[idx+1] in Token.numbers+("(", " ")+Token.a_functions:
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
                    if lt in Token.base_symbols:
                        token.kind = Token.base_symbols[lt]
                        break
                    elif lt in Token.a_functions:
                        token.kind = Token.Number
                        num_match = self.parse_function(token.negate)
                        break
                    else:
                        raise SyntaxError('Unknown Symbol: {}'.format(lt))
                else:
                    match_len -= 1
                    break


        if token.kind is Token.Number:
            token.value = self.to_num(num_match)
        # if token.negate: print("NEGATE")
        # print("In '{}': Matching '{}'".format(self.input_string, self.input_string[:match_len]))

        if token.kind is None:
            return token, self.input_string
        else:
            return token, self.input_string[match_len:]



    def _sqrt(self, num):
        return math.sqrt(num)

    def _log(self, num, base):
        return math.log(num, self.to_num(base))

    def _pow(self, num, exp):
        return math.pow(num, self.to_num(exp))

    functions = {
        "sqrt(": _sqrt,
        "log(": _log,
        "pow(": _pow
    }

    def parse_function(self, negate):
        function = ""
        parameters = None
        function_len = 0
        for idx, ch in enumerate(self.input_string):
            function += ch
            if ch == "(":
                break

        if negate is True:
            function = function[1:]
            function_len = len(function)+1
        else:
            function_len = len(function)
        if function.strip() not in self.functions: raise SyntaxError("Invalid Function {}".format(function))

        self.input_string = self.input_string[function_len:]
        self.input_string, parameters = self.find_matching_parn()

        if not len(parameters[0]): raise SyntaxError("Invalid Function {} {}".format(function, parameters[0]))
        parameters = [Parse(n) for n in parameters] #Parse all the parameters

        function = self.functions[function.strip()]
        # print(*parameters)
        # print(self.input_string)
        return function(self, *parameters)

    def find_matching_parn(self):
        """

        :return: Should return the whole sub-string + the string divided into parameters + the remaining string
            sub_string, end string, parameters[]
        """
        count = 1
        loc = 0
        parameters_loc = []
        parameters = []
        for idx, ch in enumerate(self.input_string):
            if ch == "(": count += 1
            elif ch == ")": count -= 1
            if ch == "," and count == 1:
                parameters_loc.append(idx)
            if count == 0: break
            loc += 1

        if count != 0: raise SyntaxError("Ill formed function, no end: {}".format(self.input_string))
        sub_string = self.input_string[:loc]
        end_string = self.input_string[loc:]

        if len(parameters_loc) == 0:
            parameters.append(sub_string)
        else:
            for idx, p in enumerate(parameters_loc):
                if idx != 0:
                    parameters.append(sub_string[parameters_loc[idx-1]+1:p])
                else:
                    parameters.append(sub_string[:p])
                if idx == len(parameters_loc)-1:
                    parameters.append(sub_string[p+1:])
        return end_string, parameters




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

        multiplicative_operators = [Token.Power, Token.Multiply, Token.Divide, Token.Mod]

        token = c_lexer.get_next_token()
        while token.kind in multiplicative_operators:
            factor2 = number()
            if token.kind == Token.Multiply:
                factor1 *= factor2
            elif token.kind == Token.Divide:
                factor1 /= factor2
            elif token.kind == Token.Power:
                factor1 **= factor2
            else:
                factor1 %= factor2

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