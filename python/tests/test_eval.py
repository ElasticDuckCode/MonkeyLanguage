from unittest import main, TestCase
from src.monkey import lexer, parser, obj, eval


class TestEval(TestCase):

    def verify_eval(self, code: str) -> obj.Object:
        lex = lexer.Lexer(code)
        par = parser.Parser(lex)
        program = par.parse_program()
        self.assertIsNotNone(program)
        self.assertEqual(len(par.errors), 0, par.error_str)
        return eval.eval(program)

    def verify_integer_obj(self, o: obj.Integer, expect: int):
        self.assertIsInstance(o, obj.Integer)
        self.assertEqual(o.value, expect)

    def test_eval_integer(self):
        cases = [
            ("5", 5),
            ("10", 10)
        ]
        for code, expect in cases:
            self.verify_integer_obj(self.verify_eval(code), expect)
        pass
