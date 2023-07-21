from unittest import TestCase

from src.monkey import symbols


class TestSymbols(TestCase):
    def test_define_global(self):
        expected = {
            "a": symbols.Symbol("a", symbols.GLOBAL_SCOPE, 0),
            "b": symbols.Symbol("b", symbols.GLOBAL_SCOPE, 1),
        }

        g = symbols.Table()

        a = g.define("a")
        self.assertEqual(a, expected["a"])

        b = g.define("b")
        self.assertEqual(b, expected["b"])

    def test_resolve_global(self):
        expected = [
            symbols.Symbol("a", symbols.GLOBAL_SCOPE, 0),
            symbols.Symbol("b", symbols.GLOBAL_SCOPE, 1),
        ]

        g = symbols.Table()
        g.define("a")
        g.define("b")

        for sym in expected:
            result = g.resolve(sym.name)
            self.assertIsNotNone(result)
            self.assertEqual(result, sym)
