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

    def verify_boolean_obj(self, o: obj.Boolean, expect: bool):
        self.assertIsInstance(o, obj.Boolean)
        self.assertEqual(o.value, expect)

    def test_eval_integer(self):
        cases = [
            ("5", 5),
            ("10", 10),
            ("-5", -5),
            ("-10", -10),
            ("5 + 5 + 5 + 5 - 10", 10),
            ("2 * 2 * 2 * 2 * 2", 32),
            ("-50 + 100 + -50", 0),
            ("5 * 2 + 10", 20),
            ("5 + 2 * 10", 25),
            ("20 + 2 * -10", 0),
            ("50 / 2 * 2 + 10", 60),
            ("2 * (5 + 10)", 30),
            ("3 * 3 * 3 + 10", 37),
            ("3 * (3 * 3) + 10", 37),
            ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50)
        ]
        for code, expect in cases:
            self.verify_integer_obj(self.verify_eval(code), expect)
        pass

    def test_eval_boolean(self):
        cases = [
            ("true", True),
            ("false", False),
            ("1 < 2", True),
            ("1 > 2", False),
            ("1 < 1", False),
            ("1 > 1", False),
            ("1 == 1", True),
            ("1 != 1", False),
            ("1 == 2", False),
            ("1 != 2", True),
            ("true == true", True),
            ("false == false", True),
            ("true == false", False),
            ("true != false", True),
            ("false != true", True),
            ("(1 < 2) == true", True),
            ("(1 < 2) == false", False),
            ("(1 > 2) == true", False),
            ("(1 > 2) == false", True),
        ]
        for code, expect in cases:
            self.verify_boolean_obj(self.verify_eval(code), expect)

    def test_eval_bang_operator(self):
        cases = (
            ("!true", False),
            ("!false", True),
            ("!5", False),
            ("!!true", True),
            ("!!false", False),
            ("!!5", True),
        )
        for code, expect in cases:
            self.verify_boolean_obj(self.verify_eval(code), expect)
