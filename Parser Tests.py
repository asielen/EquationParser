__author__ = 'asielen'

from Parser import solve
import unittest


class ParserTest(unittest.TestCase):
    def test_basic_add(self):
        self.assertEqual(solve('2+3'), 5)

    def test_basic_multiply(self):
        self.assertEqual(solve('2*3'), 6)

    def test_solitary_number(self):
        self.assertEqual(solve('89'), 89)

    def test_empty_error(self):
        with self.assertRaises(SyntaxError):
            solve('')

    def test_white_space(self):
        self.assertEqual(solve('   12     -   8   '), 4)
        self.assertEqual(solve('142   -9    '), 133)
        self.assertEqual(solve('72+  15'), 87)
        self.assertEqual(solve(' 12*  4'), 48)
        self.assertEqual(solve(' 50/10'), 5)

    def test_floats(self):
        self.assertEqual(solve('2.5'), 2.5)
        self.assertEqual(solve('4*2.5 + 8.5+1.5 /3.0'), 19)
        self.assertAlmostEqual(solve('5.005 + 0.0095'), 5.01, delta=0.01)

    def test_tight_expressions(self):
        self.assertEqual(solve('67+2'), 69)
        self.assertEqual(solve(' 2-7'), -5)
        self.assertEqual(solve('5*7 '), 35)
        self.assertEqual(solve('8/4'), 2)

    def test_long_add_sub(self):
        self.assertEqual(solve('2 -4 +6 -1 -1- 0 +8'), 10)
        self.assertEqual(solve('1 -1  +2  -2  + 4 - 4 +   6'), 6)

    def test_long_mixed(self):
        self.assertEqual(solve(' 2*3 - 4*5 + 6/3 '), -12)
        self.assertEqual(solve('2*3*4/8 -   5/2*4 +  6 + 0/3'), -1)

    def test_division_float(self):
        self.assertEqual(solve('10/4'), 2.5)
        self.assertAlmostEqual(solve('5/3'), 1.66, delta=0.01)
        self.assertAlmostEqual(solve('3 + 8/5 -1 -2*5'), -6.4, delta=0.01)

    def test_bad_token(self):
        with self.assertRaises(SyntaxError):
            solve('  6 + c')
        with self.assertRaises(SyntaxError):
            solve(' 7 &amp; 2')
        with self.assertRaises(SyntaxError):
            solve(' %')

    def test_syntax_error(self):
        with self.assertRaises(SyntaxError):
            solve(' 5 + + 6')
        with self.assertRaises(SyntaxError):
            solve('5 +(2')

    def test_div_zero(self):
        with self.assertRaises(ZeroDivisionError):
            solve('5/0')
        with self.assertRaises(ZeroDivisionError):
            solve('(5*7/5) + (23) - 5 * (98-4)/(6*7-42)') #should be x/0 div by zero error)

    def test_needless_parn(self):
        self.assertEqual(solve('(2)'), 2)

    def test_needless_parn2(self):
        self.assertEqual(solve('(5 + 2*3 - 1 + 7 * 8)'), 66)
        self.assertEqual(solve('(67 + 2 * 3 - 67 + 2/1 - 7)'), 1)

    def test_needless_parn3(self):
        self.assertEqual(solve('(((((5)))))'), 5)
        self.assertEqual(solve('(( ((2)) + 4))*((5))'), 30)

    def test_complex_structure(self):
        self.assertEqual(solve('(2) + (17*2-30) * (5)+2 - (8/2)*4'), 8)

    def test_unbalanced_parn(self):
        with self.assertRaises(SyntaxError):
            solve('2 + (5 * 2')
        with self.assertRaises(SyntaxError):
            solve('(((((4))))')
        with self.assertRaises(SyntaxError):
            solve('((2)) * ((3')
        with self.assertRaises(SyntaxError):
            solve('((9)) * ((1)')

if __name__ == "__main__":
    unittest.main()
